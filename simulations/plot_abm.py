import numpy as np
from scipy.interpolate import griddata
import plotly.plotly as py
from plotly.graph_objs import *

from analyze_abm import *
from parseFiles import *

    
def prepareXYZ(descDic):
    
    parDic = cooperationLevel(descDic)
    x = np.array(parDic['d'])
    y = np.array(parDic['s'])
    z = np.array(parDic['coopLevel'])

    
    #index = np.argwhere(np.array(parDic['M'])==M)
    #print index
    
    #x = np.array(parDic['d'])[index]
    #y = np.array(parDic['s'])[index]
    #try:
    #except:
    #z = np.array(parDic['coopLevel'])[index[:-1]]
    
    xi = np.linspace(min(x), max(x),100)
    yi = np.linspace(min(y), max(y),100)

    #xi = np.linspace(0.1, 0.65)
    #yi = np.linspace(0.1, 0.5)

    X, Y = np.meshgrid(xi, yi)
    Z = griddata(np.array(zip(*[x, y])), z, (X, Y),method="linear")
    Z[Z<0.001]=0
    Z[Z>1]=1
    Z[np.isnan(Z)]=0
    
    return {'X':X,'Y':Y,'Z':Z}



def export2plotly(descDic):
        
    dicXYZ = prepareXYZ(descDic)  

    data = Data([
        Surface(
            z = dicXYZ['Z'],
            x = dicXYZ['X'],
            y = dicXYZ['Y'],
            name='trace0',
            colorscale=[[0, 'rgb(0,0,131)'], [0.125, 'rgb(0,60,170)'], [0.375, 'rgb(5,255,255)'], [0.625, 'rgb(255,255,0)'], [0.875, 'rgb(250,0,0)'], [1, 'rgb(128,0,0)']]
        )
    ])
    layout = Layout(
        title = descDic.__str__(),
        autosize = False,
        width = 1500,
        height = 900,
        margin=Margin(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ),
        scene=Scene(
            xaxis=XAxis(
                range=[0, 1],
                domain=[1,0],
                title = '',
                #titlefont = Font(size = 18),
                tickfont = Font(size = 14),
                nticks=10,
                gridcolor='rgb(255, 255, 255)',
                gridwidth=2,
                zerolinecolor='rgb(255, 255, 255)',
                zerolinewidth=2
            ),
            yaxis=YAxis(
                title = '',
                #titlefont = Font(size = 18),
                tickfont = Font(size = 14),
                nticks=10,
                gridcolor='rgb(255, 255, 255)',
                gridwidth=2,
                zerolinecolor='rgb(255, 255, 255)',
                zerolinewidth=2
            ),
            zaxis=ZAxis(
                range=[0, 1],
                domain=[0, 1],
                autorange=False,
                title = '',
                #titlefont = Font(size = 18),
                tickfont = Font(size = 14),
                nticks=10,
                gridcolor='rgb(255, 255, 255)',
                gridwidth=2,
                zerolinecolor='rgb(255, 255, 255)',
                zerolinewidth=2
            ),
            bgcolor='rgb(244, 244, 248)'
        )
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig)
    return plot_url



def export2plotly2(X,Y,Z):
        
    data = Data([
        Surface(
            z = Z,
            x = X,
            y = Y,
            name='trace0',
            colorscale=[[0, 'rgb(0,0,131)'], [0.125, 'rgb(0,60,170)'], [0.375, 'rgb(5,255,255)'], [0.625, 'rgb(255,255,0)'], [0.875, 'rgb(250,0,0)'], [1, 'rgb(128,0,0)']]
        )
    ])
    layout = Layout(
        #title='ppGame_M%.2f_r%.2f_q%.2f_m%.2f'%(parDic['M'],parDic['r'],parDic['q'],parDic['m']),
        autosize = False,
        width = 1500,
        height = 900,
        margin=Margin(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ),
        scene=Scene(
            xaxis=XAxis(
                range=[0, 1],
                domain=[1,0],
                title = '',
                #titlefont = Font(size = 18),
                tickfont = Font(size = 14),
                nticks=10,
                gridcolor='rgb(255, 255, 255)',
                gridwidth=2,
                zerolinecolor='rgb(255, 255, 255)',
                zerolinewidth=2
            ),
            yaxis=YAxis(
                title = '',
                #titlefont = Font(size = 18),
                tickfont = Font(size = 14),
                nticks=10,
                gridcolor='rgb(255, 255, 255)',
                gridwidth=2,
                zerolinecolor='rgb(255, 255, 255)',
                zerolinewidth=2
            ),
            zaxis=ZAxis(
                range=[0, 1],
                domain=[0, 1],
                autorange=False,
                title = '',
                #titlefont = Font(size = 18),
                tickfont = Font(size = 14),
                nticks=10,
                gridcolor='rgb(255, 255, 255)',
                gridwidth=2,
                zerolinecolor='rgb(255, 255, 255)',
                zerolinewidth=2
            ),
            bgcolor='rgb(244, 244, 248)'
        )
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig)
    return plot_url

def heatmap(descDic):
    
    parDic = cooperationLevel(descDic)
    x = np.array(parDic['d'])
    y = np.array(parDic['s'])
    z = np.array(parDic['coopLevel'])

    dicXYZ = prepareXYZ(descDic)  

    data = Data([
        Heatmap(
            z = dicXYZ['Z'],
            x = dicXYZ['X'][1],
            y = dicXYZ['Y'][:,0],
            colorscale=[[0, 'rgb(0,0,131)'], [0.125, 'rgb(0,60,170)'], [0.375, 'rgb(5,255,255)'], [0.625, 'rgb(255,255,0)'], [0.875, 'rgb(250,0,0)'], [1, 'rgb(128,0,0)']]
            )
    ])
    
    layout = Layout(
        title = descDic.__str__(),
        autosize = False,
        width = 1000,
        height = 1000)
    
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig)
    return plot_url
    
    
def heatmap2(X,Y,Z):
        
    data = Data([
        Heatmap(
            z = Z,
        )
    ])
   
    fig = Figure(data=data)
    plot_url = py.plot(fig)
    return plot_url
