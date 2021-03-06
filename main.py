import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import layout, row, widgetbox, column, gridplot
from bokeh.models import ColumnDataSource, HoverTool, Select, LabelSet, Div
from bokeh.plotting import figure, output_file, show
from bokeh.models.glyphs import MultiLine, Text
import glob, os, sys
import copy

def read_rmms(rmm_ana_dir, rmm_fcast_dir, nanalysis, nforecast, selected_date):
    rmm1s = []
    rmm2s = []
    dates_2d = []
    phases = []
    amps = []

    # read the analysis data
    dum_files = glob.glob(os.path.join(rmm_ana_dir, 'createdPCs.15sn.%s.nrt.txt' % selected_date))
    fa = open(dum_files[0], 'r')
    lines = fa.readlines()
    lines = lines[1:]
    lines = lines[-nanalysis:]

    year = np.array([int(line.split()[0]) for line in lines])
    month = np.array([int(line.split()[1]) for line in lines])
    day = np.array([int(line.split()[2]) for line in lines])
    pc1 = np.array([float(line.split()[3]) for line in lines])
    pc2 = np.array([float(line.split()[4]) for line in lines])
    pha = np.array([int(line.split()[5]) for line in lines])
    amp = np.array([float(line.split()[6]) for line in lines])
    fa.close()

    analy_dates = np.array(['%s/%s/%s' % (year[i], month[i], day[i]) \
                            for i in range(len(year))])

    # now read nforecast days of forecasts
    # append each forecast to the analyis
    # and create a 2D array of forecasts for the members
    # Since there are some files with "*P.txt" pattern, they need to be
    # avoided. So taking this following approach
    all_files = glob.glob(os.path.join(rmm_fcast_dir, 'createdPCs.15sn.%s.fcast.*.txt' % selected_date))
    pfiles = glob.glob(os.path.join(rmm_fcast_dir, 'createdPCs.15sn.%s.fcast.*P.txt' % selected_date))
    # Eliminating P.txt files
    dum_files = list(set(all_files) - set(pfiles))
    for n in range(len(dum_files)):
        fa = open(dum_files[n], 'r')
        lines = fa.readlines()
        lines = lines[1:nforecast]
        ntime_fcasts = len(lines)

        year_fc = np.array([int(line.split()[0]) for line in lines])
        month_fc = np.array([int(line.split()[1]) for line in lines])
        day_fc = np.array([int(line.split()[2]) for line in lines])
        pc1_fc = np.array([float(line.split()[3]) for line in lines])
        pc2_fc = np.array([float(line.split()[4]) for line in lines])
        pha_fc = np.array([int(line.split()[5]) for line in lines])
        amp_fc = np.array([float(line.split()[6]) for line in lines])
        fa.close()

        dum_dates = copy.copy(analy_dates)
        dum_rmm1 = pc1.copy()
        dum_rmm2 = pc2.copy()
        dum_pha = pha.copy()
        dum_amp = amp.copy()

        fcast_dates = np.array(['%s/%s/%s' % (year_fc[i], month_fc[i], day_fc[i]) \
                                for i in range(len(year_fc))])
        rmm1s.append(np.append(dum_rmm1, pc1_fc))
        rmm2s.append(np.append(dum_rmm2, pc2_fc))
        dates_2d.append(np.append(dum_dates, fcast_dates))
        phases.append(np.append(dum_pha, pha_fc))
        amps.append(np.append(dum_amp, amp_fc))

    return np.array(dates_2d), np.array(rmm1s), np.array(rmm2s), \
           np.array(phases), np.array(amps)


# Set up data
def get_dates():
    fcast_rmm_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/glosea/rmms'
    dum_files = glob.glob(os.path.join(fcast_rmm_dir, 'createdPCs.15sn.????????.fcast.0.txt'))
    dates = [dum_file.split('.')[2] for dum_file in dum_files]
    dates.sort(reverse=True)
    return dates


def update_data(attrname, old, new):
    # for Glosea5
    rmm_ana_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/analysis/rmms/'
    rmm_fcast_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/glosea/rmms/'
    nanalysis = 41
    nforecast = 30

    data_dates, rmm1s, rmm2s, phases, amps = read_rmms(rmm_ana_dir,
                                                       rmm_fcast_dir,
                                                       nanalysis,
                                                       nforecast,
                                                       new)
    source_ana.data = dict(rmm1s=rmm1s[0, :nanalysis],
                           rmm2s=rmm2s[0, :nanalysis],
                           phases=phases[0, :nanalysis],
                           amps=amps[0, :nanalysis],
                           descs=data_dates[0, :nanalysis])
    source_ana_circle.data = dict(rmm1s=rmm1s[0, :nanalysis],
                                  rmm2s=rmm2s[0, :nanalysis],
                                  phases=phases[0, :nanalysis],
                                  amps=amps[0, :nanalysis],
                                  descs=data_dates[0, :nanalysis])

    source_fcast_glosea.data = dict(rmm1s=rmm1s[:, nanalysis - 1:].tolist(),
                                    rmm2s=rmm2s[:, nanalysis - 1:].tolist(),
                                    phases=phases[:, nanalysis - 1:].tolist(),
                                    amps=amps[:, nanalysis - 1:].tolist())

    source_fcast_ensmean_glosea.data = dict(rmm1s=np.mean(rmm1s[:, nanalysis - 1:], axis=0),
                                            rmm2s=np.mean(rmm2s[:, nanalysis - 1:], axis=0),
                                            phases=np.mean(phases[:, nanalysis - 1:], axis=0),
                                            amps=np.mean(amps[:, nanalysis - 1:], axis=0),
                                            descs=data_dates[0, nanalysis - 1:])
    plot_gl.title.text = "GloSea5 MJO Forecasts %s" % new

    rmm_fcast_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/mogreps/rmms/'
    nforecast = 7
    data_dates, rmm1s, rmm2s, phases, amps = read_rmms(rmm_ana_dir,
                                                       rmm_fcast_dir,
                                                       nanalysis,
                                                       nforecast,
                                                       new)
    source_fcast_mogreps.data = dict(rmm1s=rmm1s[:, nanalysis - 1:].tolist(),
                                     rmm2s=rmm2s[:, nanalysis - 1:].tolist(),
                                     phases=phases[:, nanalysis - 1:].tolist(),
                                     amps=amps[:, nanalysis - 1:].tolist())

    source_fcast_ensmean_mogreps.data = dict(rmm1s=np.mean(rmm1s[:, nanalysis - 1:], axis=0),
                                             rmm2s=np.mean(rmm2s[:, nanalysis - 1:], axis=0),
                                             phases=np.mean(phases[:, nanalysis - 1:], axis=0),
                                             amps=np.mean(amps[:, nanalysis - 1:], axis=0),
                                             descs=data_dates[0, nanalysis - 1:])
    plot_mog.title.text = "MOGREPS MJO Forecasts %s" % new


def get_sourcedata(selected_date, rmm_fcast_dir, nforecast):
    # for both models
    rmm_ana_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/analysis/rmms/'
    nanalysis = 41
    data_dates, rmm1s, rmm2s, phases, amps = read_rmms(rmm_ana_dir,
                                                       rmm_fcast_dir,
                                                       nanalysis,
                                                       nforecast,
                                                       selected_date)
    source_ana = ColumnDataSource(data=dict(rmm1s=rmm1s[0, :nanalysis],
                                            rmm2s=rmm2s[0, :nanalysis],
                                            phases=phases[0, :nanalysis],
                                            amps=amps[0, :nanalysis],
                                            descs=data_dates[0, :nanalysis]))
    source_ana_circle = ColumnDataSource(data=dict(rmm1s=rmm1s[0, :nanalysis],
                                                   rmm2s=rmm2s[0, :nanalysis],
                                                   phases=phases[0, :nanalysis],
                                                   amps=amps[0, :nanalysis],
                                                   descs=data_dates[0, :nanalysis]))
    source_fcast = ColumnDataSource(data=dict(rmm1s=rmm1s[:, nanalysis - 1:].tolist(),
                                              rmm2s=rmm2s[:, nanalysis - 1:].tolist(),
                                              phases=phases[:, nanalysis - 1:].tolist(),
                                              amps=amps[:, nanalysis - 1:].tolist(),
                                              descs=data_dates[:, nanalysis - 1:]))
    source_fcast_ensmean = ColumnDataSource(data=dict(rmm1s=np.mean(rmm1s[:, nanalysis - 1:], axis=0),
                                                      rmm2s=np.mean(rmm2s[:, nanalysis - 1:], axis=0),
                                                      phases=np.mean(phases[:, nanalysis - 1:], axis=0),
                                                      amps=np.mean(amps[:, nanalysis - 1:], axis=0),
                                                      descs=data_dates[0, nanalysis - 1:]))
    return source_ana, source_ana_circle, source_fcast, source_fcast_ensmean

def make_plot(title='Forecasts'):
    plot = figure(plot_height=500, plot_width=500, tools=["pan,reset,save, wheel_zoom", hover],
                     x_range=[-4, 4], y_range=[-4, 4])

    plot.title.text = title

    # Mark the 8 sectors
    x = 4
    y = 0.707107
    linewidth = 0.25
    plot.line([-x, -y], [-x, -y], line_width=0.5, line_alpha=0.6)
    plot.line([y, x], [y, x], line_width=0.5, line_alpha=0.6)
    plot.line([-x, -y], [x, y], line_width=0.5, line_alpha=0.6)
    plot.line([y, x], [-y, -x], line_width=0.5, line_alpha=0.6)
    plot.line([-x, -1], [0, 0], line_width=0.5, line_alpha=0.6)
    plot.line([1, x], [0, 0], line_width=0.5, line_alpha=0.6)
    plot.line([0, 0], [-x, -1], line_width=0.5, line_alpha=0.6)
    plot.line([0, 0], [1, x], line_width=0.5, line_alpha=0.6)

    xt, yt = 3., 1.5
    phase_marker_source = ColumnDataSource(data=dict(xt=[-xt, -yt, yt, xt, xt, yt, -yt, -xt],
                                                     yt=[-yt, -xt, -xt, -yt, yt, xt, xt, yt],
                                                     phase_labels=[str(i) for i in range(1, 9)]))
    labels = LabelSet(x='xt', y='yt', text='phase_labels', level='glyph', \
                      x_offset=0, y_offset=0, source=phase_marker_source, \
                      render_mode='canvas', text_color='grey', text_font_size="30pt", text_alpha=0.25)
    plot.add_layout(labels)
    plot.circle([0], [0], radius=1, color="white", line_color='grey', alpha=0.6)

    phase_name_source = ColumnDataSource(dict(x=[0, 0], y=[-3.75, 3.], text=['Indian \n Ocean', 'Western \n Pacific']))
    glyph = Text(x="x", y="y", text="text", angle=0., text_color="grey", text_align='center', text_alpha=0.25)
    plot.add_glyph(phase_name_source, glyph)

    phase_name_source = ColumnDataSource(dict(x=[-3.], y=[0], text=['West. Hem\n Africa']))
    glyph = Text(x="x", y="y", text="text", angle=np.pi / 2., text_color="grey", text_align='center', text_alpha=0.25)
    plot.add_glyph(phase_name_source, glyph)

    phase_name_source = ColumnDataSource(dict(x=[3.], y=[0], text=['Maritime\n continent']))
    glyph = Text(x="x", y="y", text="text", angle=-np.pi / 2., text_color="grey", text_align='center', text_alpha=0.25)
    plot.add_glyph(phase_name_source, glyph)

    plot.xaxis[0].axis_label = 'RMM1'
    plot.yaxis[0].axis_label = 'RMM2'

    return plot


# Get available data dates and data for the first
# available date to plot as a start
menu_dates = get_dates()
selected_date = menu_dates[0]

# set up a drop down menu of available dates
date_select = Select(value=selected_date, title='Date:', options=menu_dates)
# get glosea data
rmm_fcast_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/glosea/rmms/'
nforecast = 30
source_ana, source_ana_circle, source_fcast_glosea, source_fcast_ensmean_glosea \
    = get_sourcedata(selected_date, rmm_fcast_dir, nforecast)

# get mogreps data
rmm_fcast_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/mogreps/rmms/'
nforecast = 7
source_ana, source_ana_circle, source_fcast_mogreps, source_fcast_ensmean_mogreps \
    = get_sourcedata(selected_date, rmm_fcast_dir, nforecast)

# Set up plot
hover = HoverTool(tooltips=[
    ("Date", "@descs"),
    ("RMM1", "@rmm1s"),
    ("RMM2", "@rmm2s"),
    ("Phase", "@phases"),
    ("Amp", "@amps"),
], mode='mouse', names=["analysis", "analysis_dots", "ens_mean", "ens_mean_dots"])

############## Glosea plot #######################
plot_gl = make_plot('GloSea5 MJO Forecasts %s' % date_select.value)
# Plotting data
plot_gl.line('rmm1s', 'rmm2s', source=source_ana, name="analysis", line_color='grey', line_width=5, line_alpha=0.8)
plot_gl.circle('rmm1s', 'rmm2s', source=source_ana_circle, name="analysis_dots", color='grey', radius=0.05,
               alpha=0.8)
plot_gl.multi_line('rmm1s', 'rmm2s', source=source_fcast_glosea, line_width=2, line_color='skyblue', line_alpha=0.5)
plot_gl.line('rmm1s', 'rmm2s', source=source_fcast_ensmean_glosea, name="ens_mean", line_color='blue', line_width=5,
             line_alpha=0.4)
plot_gl.circle('rmm1s', 'rmm2s', source=source_fcast_ensmean_glosea, name="ens_mean_dots", color='blue',
               radius=0.05, alpha=0.3)
############## mogreps plot #######################
plot_mog = make_plot('MOGREPS MJO Forecasts %s' % date_select.value)
plot_mog.x_range = plot_gl.x_range
plot_mog.y_range = plot_gl.y_range
# Plotting data
plot_mog.line('rmm1s', 'rmm2s', source=source_ana, name="analysis", line_color='grey', line_width=5, line_alpha=0.8)
plot_mog.circle('rmm1s', 'rmm2s', source=source_ana_circle, name="analysis_dots", color='grey', radius=0.05,
               alpha=0.8)
plot_mog.multi_line('rmm1s', 'rmm2s', source=source_fcast_mogreps, line_width=2, line_color='skyblue', line_alpha=0.5)
plot_mog.line('rmm1s', 'rmm2s', source=source_fcast_ensmean_mogreps, name="ens_mean", line_color='blue', line_width=5,
             line_alpha=0.4)
plot_mog.circle('rmm1s', 'rmm2s', source=source_fcast_ensmean_mogreps, name="ens_mean_dots", color='blue',
               radius=0.05, alpha=0.3)

# Menu
date_select.on_change('value', update_data)
# Set up layouts and add to document
controls = column(date_select)

desc = Div(text=open(os.path.join(os.path.dirname(__file__), "description.html")).read(), width=1600)
sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

plots = gridplot([[plot_gl, plot_mog]])
page_layout = layout([[desc], [controls, plots], ], sizing_mode=sizing_mode)
# curdoc().add_root(row(controls, plot))
curdoc().add_root(page_layout)
curdoc().title = "MJO GloSea Monitor"
