import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import layout, row, widgetbox, column, gridplot
from bokeh.models import ColumnDataSource, HoverTool, Select, LabelSet, Div
from bokeh.plotting import figure, output_file, show
from bokeh.models.glyphs import MultiLine, Text
from bokeh.models.widgets.inputs import DatePicker
from datetime import datetime, timedelta
import glob, os
import urllib.request, urllib.error, urllib.parse  # the lib that handles the url stuff


def read_web_dates(start_date, end_date):
    # Get available data dates and data for the first
    # available date to plot as a start
    target_url = 'http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt'
    req = urllib.request.Request(target_url, headers={'User-Agent': "Magic Browser"})
    data = urllib.request.urlopen(req)
    lines = data.readlines()[2:]  # skip 2 header lines

    year = np.array([int(line.split()[0]) for line in lines])
    month = np.array([int(line.split()[1]) for line in lines])
    day = np.array([int(line.split()[2]) for line in lines])
    pc1 = np.array([float(line.split()[3]) for line in lines])
    pc2 = np.array([float(line.split()[4]) for line in lines])
    pha = np.array([int(line.split()[5]) for line in lines])
    amp = np.array([float(line.split()[6]) for line in lines])

    dates = [year[i] * 10000 + month[i] * 100 + day[i] for i in range(len(year))]
    print(start_date, end_date)
    start_ind = dates.index(start_date)
    end_ind = dates.index(end_date)
    source.data = dict(rmm1s=pc1[start_ind:end_ind],
                               rmm2s=pc2[start_ind:end_ind],
                               phases=pha[start_ind:end_ind],
                               amps=amp[start_ind:end_ind],
                               descs=dates[start_ind:end_ind])
    return source

def read_local_dates(start_date, end_date):
    target_file = '/home/h03/hadpx/python_all/mypylibs/Bokeh_examples/mjo_obs/rmm.74toRealtime.txt'
    fa = open(target_file, 'r')
    lines = fa.readlines()[2:]

    year = np.array([int(line.split()[0]) for line in lines])
    month = np.array([int(line.split()[1]) for line in lines])
    day = np.array([int(line.split()[2]) for line in lines])
    pc1 = np.array([float(line.split()[3]) for line in lines])
    pc2 = np.array([float(line.split()[4]) for line in lines])
    pha = np.array([int(line.split()[5]) for line in lines])
    amp = np.array([float(line.split()[6]) for line in lines])

    dates = np.array([year[i] * 10000 + month[i] * 100 + day[i] for i in range(len(year))])

    start_ind = np.where(start_date == dates)[0][0]
    end_ind = np.where(end_date == dates)[0][0]
    print(end_ind)
    data = ColumnDataSource(data=dict(rmm1s=pc1[start_ind:end_ind],
                               rmm2s=pc2[start_ind:end_ind],
                               phases=pha[start_ind:end_ind],
                               amps=amp[start_ind:end_ind],
                               descs=dates[start_ind:end_ind]))

    return data


def update_data(attr, old, new):
    start_date = date1_select.value
    end_date = date2_select.value
    start_date_x = start_date.year * 10000 + start_date.month * 100 + start_date.day
    end_date_x = end_date.year * 10000 + end_date.month * 100 + end_date.day

    # Update data
    source = read_web_dates(start_date_x, end_date_x)


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


#
# menu_dates = read_local_dates()
# selected_date = menu_dates[-40]

# set up a drop down menu of available dates
# date1_select = Select(value=menu_dates[-40], title='Date:', options=menu_dates)

# print np.where(date1_select.value==menu_dates)


# Latest date
latest_date = datetime.now() - timedelta(days=5) # allow 5 days lag
date2_select = DatePicker(title="End Date:", min_date=datetime(1974, 6, 1),
                          max_date=latest_date,
                          value=datetime(latest_date.year,
                                         latest_date.month,
                                         latest_date.day)
                          )

prev_date = date2_select.max_date - timedelta(days=40)

date1_select = DatePicker(title="Start Date:", min_date=datetime(1974, 6, 1),
                          max_date=prev_date,
                          value=datetime(prev_date.year,
                                         prev_date.month,
                                         prev_date.day)
                          )

start_date = date1_select.value
end_date = date2_select.value
start_date_x = start_date.year * 10000 + start_date.month * 100 + start_date.day
end_date_x = end_date.year * 10000 + end_date.month * 100 + end_date.day


source = ColumnDataSource(data=dict(rmm1s=np.arange(10),
                               rmm2s=np.arange(10),
                               phases=np.arange(10),
                               amps=np.arange(10),
                               descs=np.arange(10)))
#update data source
source = read_web_dates(start_date_x, end_date_x)


# date2_select = Select(value=date1_select.value, title='Date:', options=menu_dates)
# get glosea data

# Set up plot
hover = HoverTool(tooltips=[
    ("Date", "@descs"),
    ("RMM1", "@rmm1s"),
    ("RMM2", "@rmm2s"),
    ("Phase", "@phases"),
    ("Amp", "@amps"),
], mode='mouse', names=["analysis", "analysis_dots", "ens_mean", "ens_mean_dots"])

############## Glosea plot #######################
plot = make_plot('Observed MJO %s-%s' %(start_date_x, end_date_x))
# # Plotting data
plot.line('rmm1s', 'rmm2s', source=source, name="analysis", line_color='grey', line_width=5, line_alpha=0.8)
plot.circle('rmm1s', 'rmm2s', source=source, name="analysis_dots", color='grey', radius=0.05,
               alpha=0.8)

# Menu
date1_select.on_change('value', update_data)
date2_select.on_change('value', update_data)

# Set up layouts and add to document
controls = column(date1_select, date2_select)

desc = Div(text=open(os.path.join(os.path.dirname(__file__), "description.html")).read(), width=1600)
sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

plots = gridplot([[plot]])
page_layout = layout([[desc], [controls, plots], ], sizing_mode=sizing_mode)
#page_layout = layout([[desc], [controls], ], sizing_mode=sizing_mode)
# curdoc().add_root(row(controls, plot))
curdoc().add_root(page_layout)
curdoc().title = "MJO Observed"
