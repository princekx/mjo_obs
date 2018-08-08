import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import layout, row, widgetbox, column
from bokeh.models import ColumnDataSource, HoverTool, Select, LabelSet, Div
from bokeh.plotting import figure, output_file, show
from bokeh.models.glyphs import MultiLine
import glob, os, sys
import copy

rmm_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/analysis/rmms/'


def read_rmms(selected_date):
    rmm1s = []
    rmm2s = []
    dates_2d = []
    phases = []
    amps = []
    dum_files = glob.glob(os.path.join(rmm_dir, 'createdPCs.15sn.%s.nrt.txt' % selected_date))
    print dum_files
    fa = open(dum_files[0], 'r')
    lines = fa.readlines()
    lines = lines[1:]
    lines = lines[-40:]
    ntime_anals = len(lines)

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
    print len(analy_dates)

    # now read forecasts
    fcast_rmm_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/glosea/rmms'
    dum_files = glob.glob(os.path.join(fcast_rmm_dir, 'createdPCs.15sn.%s.fcast.?.txt' % selected_date))
    for n in range(len(dum_files)):
        fa = open(dum_files[n], 'r')
        lines = fa.readlines()
        lines = lines[1:31]
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
    print attrname, old, new
    data_dates, rmm1s, rmm2s, phases, amps = read_rmms(new)
    nanalysis = 41
    cint = 1
    source_ana.data = dict(rmm1s=rmm1s[0, :nanalysis], \
                           rmm2s=rmm2s[0, :nanalysis], \
                           phases=phases[0, :nanalysis], \
                           amps=amps[0, :nanalysis], \
                           descs=data_dates[0, :nanalysis])
    source_ana_circle.data = dict(rmm1s=rmm1s[0, :nanalysis], \
                                  rmm2s=rmm2s[0, :nanalysis], \
                                  phases=phases[0, :nanalysis], \
                                  amps=amps[0, :nanalysis], \
                                  descs=data_dates[0, :nanalysis])

    source_fcast.data = dict(rmm1s=rmm1s[:, nanalysis - 1:].tolist(), \
                             rmm2s=rmm2s[:, nanalysis - 1:].tolist(), \
                             phases=phases[:, nanalysis - 1:].tolist(), \
                             amps=amps[:, nanalysis - 1:].tolist())

    source_fcast_ensmean.data = dict(rmm1s=np.mean(rmm1s[:, nanalysis - 1:], axis=0), \
                                     rmm2s=np.mean(rmm2s[:, nanalysis - 1:], axis=0), \
                                     phases=np.mean(phases[:, nanalysis - 1:], axis=0), \
                                     amps=np.mean(amps[:, nanalysis - 1:], axis=0), \
                                     descs=data_dates[0, nanalysis - 1:])


nanalysis = 41
cint = 1
menu_dates = get_dates()

selected_date = menu_dates[0]
data_dates, rmm1s, rmm2s, phases, amps = read_rmms(selected_date)

print data_dates[0, nanalysis - 1:]
hover = HoverTool(tooltips=[
    ("Date", "@descs"),
    ("RMM1", "@rmm1s"),
    ("RMM2", "@rmm2s"),
    ("Phase", "@phases"),
    ("Amp", "@amps"),
], mode='mouse', names =["analysis", "analysis_dots", "ens_mean", "ens_mean_dots"])

source_ana = ColumnDataSource(data=dict(rmm1s=rmm1s[0, :nanalysis], \
                                        rmm2s=rmm2s[0, :nanalysis], \
                                        phases=phases[0, :nanalysis], \
                                        amps=amps[0, :nanalysis], \
                                        descs=data_dates[0, :nanalysis]))
print '1', amps[0, :nanalysis].shape
source_ana_circle = ColumnDataSource(data=dict(rmm1s=rmm1s[0, :nanalysis], \
                                               rmm2s=rmm2s[0, :nanalysis], \
                                               phases=phases[0, :nanalysis], \
                                               amps=amps[0, :nanalysis], \
                                               descs=data_dates[0, :nanalysis]))
print '2', amps[0, 0:nanalysis:cint].shape
source_fcast = ColumnDataSource(data=dict(rmm1s=rmm1s[:, nanalysis - 1:].tolist(), \
                                          rmm2s=rmm2s[:, nanalysis - 1:].tolist(), \
                                          phases=phases[:, nanalysis - 1:].tolist(), \
                                          amps=amps[:, nanalysis - 1:].tolist(), \
                                          descs=data_dates[:, nanalysis - 1:]))
print '3', amps[0, nanalysis - 1:].shape
source_fcast_ensmean = ColumnDataSource(data=dict(rmm1s=np.mean(rmm1s[:, nanalysis - 1:], axis=0), \
                                                  rmm2s=np.mean(rmm2s[:, nanalysis - 1:], axis=0), \
                                                  phases=np.mean(phases[:, nanalysis - 1:], axis=0), \
                                                  amps=np.mean(amps[:, nanalysis - 1:], axis=0), \
                                                  descs=data_dates[0, nanalysis - 1:]))
print '4', amps[0, nanalysis - 1:].shape
# print rmm1s[:, nanalysis - 1:].shape

date_select = Select(value=selected_date, title='Date:', \
                     options=menu_dates)

desc = Div(text=open(os.path.join(os.path.dirname(__file__), "description.html")).read(), width=800)

# Set up plot
plot = figure(plot_height=600, plot_width=600, title="MJO Forecast %s" % date_select.value,
              tools=["pan,reset,save, wheel_zoom", hover],
              x_range=[-4, 4], y_range=[-4, 4])
#
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
                                                 phase_names=[str(i) for i in range(1, 9)]))
labels = LabelSet(x='xt', y='yt', text='phase_names', level='glyph', \
                  x_offset=0, y_offset=0, source=phase_marker_source, \
                  render_mode='canvas', text_color='grey', text_font_size="30pt", text_alpha=0.25)
plot.add_layout(labels)

plot.circle([0], [0], radius=1, color="white", line_color='grey', alpha=0.6)
# glyph = MultiLine(xs="rmm1s", ys="rmm2s")#, line_width=3, line_alpha=0.6)
# plot.add_glyph(source, glyph)
plot.line('rmm1s', 'rmm2s', source=source_ana, name="analysis", line_color='grey', line_width=5, line_alpha=0.8)
plot.circle('rmm1s', 'rmm2s', source=source_ana_circle, name="analysis_dots", color='grey', radius=0.05, alpha=0.8)

plot.multi_line('rmm1s', 'rmm2s', source=source_fcast, line_width=2, line_color='skyblue', line_alpha=0.5)

plot.line('rmm1s', 'rmm2s', source=source_fcast_ensmean, name="ens_mean", line_color='blue', line_width=5, line_alpha=0.4)
plot.circle('rmm1s', 'rmm2s', source=source_fcast_ensmean, name="ens_mean_dots", color='blue', radius=0.05, alpha=0.3)

# plot.circle('rmm1', 'rmm2', source=source)


date_select.on_change('value', update_data)
# Set up layouts and add to document
controls = column(date_select)

# output_file("mjo_glosea.html", title="MJO Glosea Monitor")
# show(row(plot, controls))
sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

page_layout = layout([[desc], [controls, plot], ], sizing_mode=sizing_mode)

# curdoc().add_root(row(controls, plot))
curdoc().add_root(page_layout)
curdoc().title = "MJO GloSea Monitor"
