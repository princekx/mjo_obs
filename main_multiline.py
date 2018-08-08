import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, HoverTool, Select
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure, output_file
from bokeh.models.glyphs import MultiLine
import glob, os, sys

rmm_dir = '/project/MJO_GCSS/MJO_monitoring/processed_MJO_data/glosea/rmms'

def read_rmms(selected_date):
    dum_files = glob.glob(os.path.join(rmm_dir, 'createdPCs.15sn.%s.fcast.0.txt' %selected_date))
    print dum_files
    fa = open(dum_files[0], 'r')
    lines = fa.readlines()
    lines = lines[1:]
    ntime_anals = len(lines)
    
    year = [int(line.split()[0]) for line in lines]
    month = [int(line.split()[1]) for line in lines]
    day = [int(line.split()[2]) for line in lines]
    pc1 = [float(line.split()[3]) for line in lines]
    pc2 = [float(line.split()[4]) for line in lines]
    pha = [int(line.split()[5]) for line in lines]
    fa.close()
    return year, month, day, pc1, pc2
# Set up data
def get_dates():
    dum_files = glob.glob(os.path.join(rmm_dir, 'createdPCs.15sn.????????.fcast.0.txt'))
    dates = [dum_file.split('.')[2] for dum_file in dum_files]
    dates.sort(reverse=True)
    return dates

def update_data(attrname, old, new):
    print attrname, old, new
    year, month, day, rmm1, rmm2 = read_rmms(new)
    #rmm1s.append(np.array(rmm1))
    #rmm2s.append(np.array(rmm2))
    print rmm1
    #dates_2d.append(data_dates)
    #source.data = dict(rmm1s=rmm1s, rmm2s=rmm2s, descs=dates_2d)
    source.data = dict(rmm1s=np.array(rmm1), rmm2s=np.array(rmm2), descs=dates_2d)
menu_dates = get_dates()

selected_date = menu_dates[0]
year, month, day, rmm1, rmm2 = read_rmms(selected_date)

data_dates = ['%s/%s/%s' %(year[i],month[i], day[i]) for i in range(len(year))]
print data_dates

hover = HoverTool(tooltips=[
    ("(rmm1,rmm2)", "(@rmm1, @rmm2)"),
    ("Date", "@desc"),
], mode='vline')

#source = ColumnDataSource(data=dict(rmm1=rmm1, rmm2=rmm2, desc=data_dates))
rmm1s = []
rmm2s = []
dates_2d = []
rmm1s.append(np.array(rmm1))
rmm2s.append(np.array(rmm2))
dates_2d.append(data_dates)

source = ColumnDataSource(data=dict(\
                                    rmm1s = rmm1s, \
                                    rmm2s = rmm2s, \
                                    descs = dates_2d))

date_select = Select(value=selected_date, title='Date:', \
                                  options=menu_dates)


# Set up plot
plot = figure(plot_height=600, plot_width=600, title="my sine wave",
              tools=["pan,reset,save,wheel_zoom"],
              x_range=[-4, 4], y_range=[-4, 4])
#              

#glyph = MultiLine(xs="rmm1s", ys="rmm2s")#, line_width=3, line_alpha=0.6)
#plot.add_glyph(source, glyph)
plot.multi_line('rmm1s', 'rmm2s', source=source, line_width=3, line_alpha=0.6)
#plot.circle('rmm1', 'rmm2', source=source)


date_select.on_change('value', update_data)
# Set up layouts and add to document
controls = column(date_select)

output_file("mjo_mogreps.html", title="MJO_MOGREPS_monitor")
# show(row(plot, controls))

lcurdoc().add_root(row(plot, controls))
curdoc().title = "Weather"
