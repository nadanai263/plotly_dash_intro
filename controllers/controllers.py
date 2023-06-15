import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import tellurium as te

# 1. Define models
def control(tmax,nsteps,params):
    # Open-loop and closed-loop control
    # Solves dynamical system as defined

    u=params[0]
    d0=params[1]
    G=params[2]
    K=params[3]
    
    r = te.loada('''
        J1: -> y1 ; -y1 + u + d
        J2: -> y2 ; -y2 + (u-y2*K)*G + d

        y1=0;
        y2=0;
        u='''+str(u)+'''; 
        d='''+str(d0)+''';
        G='''+str(G)+''';
        K='''+str(K)+''';
    ''')

    out=r.simulate(0,tmax,points=nsteps)
    return(out)


# 2. Start Dash
app = dash.Dash()


markdown_text = '''
### Feedback control

Different types of feedback control
'''


# 3. Set layouts
app.layout = html.Div([

    html.Div([
    dcc.Markdown(children=markdown_text)]),

    html.Div(id='intermediate-value', style={'display': 'none'}), # Hidden Div for data storage

    html.Div([

        html.Div([
        dcc.Graph(
            id='controllers',
        )
        ],style={'width':'50%','float':'left','margin-left':'60px'}),

        html.Div([

        html.Label('u - setpoint'),
        dcc.Slider(
            id='u',
            min=0,
            max=20,
            marks={i: str(i) for i in [5,10,15,20]},
            value=1,
            step=0.5,
            updatemode='drag'
        ),

        html.Label('d - perturbation'),
        dcc.Slider(
            id='d',
            min=-4,
            max=4,
            marks={i: str(i) for i in [-2,0,2,4]},
            value=1,
            step=0.5,
            updatemode='drag'
        ),

        html.Label('G - gain'),
        dcc.Slider(
            id='G',
            min=0,
            max=100,
            marks={i: str(i) for i in [50,100]},
            value=50,
            step=10,
            updatemode='drag'
        ),

        html.Label('K - amplification factor'),
        dcc.Slider(
            id='K',
            min=0,
            max=10,
            marks={i: str(i) for i in [5,10]},
            value=1,
            step=0.5,
            updatemode='drag'
        )

    	],style={'width':'30%','float':'right','margin-right':'60px','margin-top':'100px'})

    ])

])  

# 4. Define callbacks and functions
@app.callback(
    dash.dependencies.Output('intermediate-value', 'children'),
    [dash.dependencies.Input('u', 'value'),
    dash.dependencies.Input('d', 'value'),
    dash.dependencies.Input('G', 'value'),
    dash.dependencies.Input('K', 'value')])
def update_data(u,d,G,K):
    
    tmax=6
    nsteps=100
    time=np.linspace(0,tmax,nsteps)

    params=np.array([u,d,G,K],np.float64)

    out=pd.DataFrame(control(tmax,nsteps,params))

    return out.to_json(date_format='iso', orient='split')


@app.callback(
    dash.dependencies.Output('controllers', 'figure'),
    [dash.dependencies.Input('intermediate-value','children')])
def update_Rfigure(out):
 
    model=pd.read_json(out,orient='split')
    y_OL=model.iloc[:,1]
    y_CL=model.iloc[:,2]

    traces = []

    traces.append(go.Scatter(
        y=y_OL,
        mode='lines',
        opacity=1
    ))

    traces.append(go.Scatter(
        y=y_CL,
        mode='lines',
        opacity=1
    ))

    return {
        'data': traces,
        'layout': go.Layout(title='Open-loop vs closed-loop', 
                 titlefont={'family':'Arial','size':22},
                xaxis={'title':'Time',
                       'titlefont':{'size':18},
                       'type':'linear',
                       'autorange':True,'range':[2,5], # Autorange overrides manual range
                       'ticks':'inside','zeroline':False,'ticklen':6,'tickwidth':2,
                       'tickfont':{'family':'Arial','size':18},
                      'showgrid':False,'showline':True,'mirror':'ticks','linewidth':2},
                yaxis={'title':'y',
                       'titlefont':{'size':18},
                       'type':'linear',
                       'autorange':False,'range':[0,20], # Autorange overrides manual range
                       'ticks':'inside','zeroline':False,'ticklen':6,'tickwidth':2,
                       'tickfont':{'family':'Arial','size':18},
                      'showgrid':False,'showline':True,'mirror':'ticks','linewidth':2},
                autosize=False,
                margin=go.layout.Margin(l=100,r=100,b=100,t=100,pad=4), 
                showlegend=True,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    }


app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server()