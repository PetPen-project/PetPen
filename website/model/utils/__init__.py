from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd
import os

def bokeh_plot(log_dir,detail=True):
    if detail:
        train_log_name = os.path.join(log_dir,'train_logfull')
        validate_log_name = os.path.join(log_dir,'test_logfull')
    else:
        train_log_name = os.path.join(log_dir,'train_log')
        validate_log_name = os.path.join(log_dir,'test_log')
        
    train_log = pd.read_csv(train_log_name)
    validate_log = pd.read_csv(validate_log_name)
    plot = figure(plot_width=800, plot_height=300, title="evaluation result")
    plot.multi_line([train_log.index.values, validate_log.index.values], [train_log['loss'].values, validate_log['loss'].values], color=['firebrick','navy'])
    if detail:
        plot.xaxis.axis_label = 'batch counts'
    else:
        plot.xaxis.axis_label = 'epochs'
    plot.yaxis.axis_label = 'loss'
    script, div = components(plot)
    return script, div
