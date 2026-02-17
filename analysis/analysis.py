import numpy as np
import pylab as pl
import s3parse

fig_width_pt = 420.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0 / 72.27  # Convert pt to inch
golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
fig_width = fig_width_pt * inches_per_pt  # width in inches
fig_height = fig_width  # *golden_mean      # height in inches
fig_size = [fig_width, fig_height]

params = {'backend': 'ps',
          'axes.labelsize': 25,
          'text.fontsize': 32,
          'legend.fontsize': 14,
          'title.fontsize': 20,
          'xtick.labelsize': 20,
          'ytick.labelsize': 20,
          'text.usetex': False,
          'figure.figsize': fig_size}
pl.rcParams.update(params)


def rescaleIter(dic):
    l = dic['description']['descDic']['l']
    h = dic['description']['descDic']['h']
    iterations = l*h
    dic['summary']['iter'] = list(np.array(dic['summary']['iter'])/iterations)

    for k in ['E', 'M', 'RE', 'R', 'U', 'RM', 'FM']:
        try:
            dic['moves'][k]['iter'] = list(np.array(dic['moves'][k]['iter'])/iterations)
        except:
            continue

    return dic
