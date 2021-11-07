from datetime import datetime
import plotly
# import plotly.express as px
import plotly.graph_objects as go
import json

from plotly.graph_objs import layout

def graph_forecast(forecast_data):
    temperature = [dataset["temp"] for dataset in forecast_data]
    humidity = [dataset["humidity"] for dataset in forecast_data]
    pressure = [dataset["pressure"] for dataset in forecast_data]
    time = [datetime.fromtimestamp(int(dataset["dt"])) for dataset in forecast_data]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time,
        y=temperature,
        name="Temperature",
        yaxis="y"
    ))
    fig.add_trace(go.Scatter(
        x=time,
        y=humidity,
        name="Humidity",
        yaxis="y2"
    ))
    fig.add_trace(go.Scatter(
        x=time,
        y=pressure,
        name="Pressure",
        yaxis="y3"
    ))

    
    # Create axis objects
    fig.update_layout(
        xaxis=dict(domain=[0, 0.8]),
        yaxis=dict(
            title="Temperature [℃]",
            titlefont=dict(color="#1f77b4"),
            tickfont=dict(color="#1f77b4"),
            ),
        yaxis2=dict(
            title="Humidity [%]",
            titlefont=dict(color="#ff7f0e"),
            tickfont=dict(color="#ff7f0e"),
            #required to use position
            anchor="x",
            overlaying="y",
            side="right"
            ),
        yaxis3=dict(
            title="Pressure [hPa]",
            titlefont=dict(color="#d62728"),
            tickfont=dict(color="#d62728"),
            anchor="free",
            position=0.90,
            overlaying="y",
            side="right"
            ),


        )

    # Update layout properties
    fig.update_layout(
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        margin=dict(l=0,r=0,b=0,t=70,pad=5)
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON