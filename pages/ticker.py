from dash import Dash, html, dcc, Input, Output, register_page, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import json
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date

# Nice function that convert 1000000 to "1M"
# Modified from: https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings/45846841#45846841
def human_format(num):
    x = float(f'{num:.3g}') # round to the nearest 3 decimal places
    magnitude = 0
    while abs(x) >= 1000:
        magnitude += 1
        x *= 0.001
    return f'{x:f}'.rstrip('0').rstrip('.') + ['','K','M','B','T','Qd','Qn'][magnitude] # and on, and on, and on...


# Register this page to the dash application
register_page(__name__, path_template="/ticker/<tickerID>") # require ticker ID to process data

# Global objects - not to be recreated every time
dfTicker = pd.DataFrame()
figTicker = make_subplots()
dateMin = ''
dateMax = ''
zoomTriggered = False # updateDatePicker will set it to true to prevent circular update
yCandleStart = 0.0 # Need to keep track of vertical range as well. Somehow updating x axis also updates y axis!?
yCandleEnd = 0.0
yCandleMin = 0.0
yCandleMax = 0.0
yVolumeStart = 0.0
yVolumeEnd = 0.0
yVolumeMin = 0.0
yVolumeMax = 0.0

# Layout definition
def layout(tickerID=None):
    global dfTicker, figTicker, dateMin, dateMax
    global yCandleStart, yCandleEnd, yCandleMin, yCandleMax, yVolumeStart, yVolumeEnd, yVolumeMin, yVolumeMax
    if tickerID:
        dfTicker = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
        # Assume data is sorted by date, ealier to later
        dateMax = dfTicker['Date'].iloc[-1] # can't use [-1] directly, and it has to be iloc[-1], not iloc(-1), to access the LAST element of a series
        dateMin = dfTicker['Date'].iloc[0] # has to be .iloc[0] instead of [0]
        yCandleMin = dfTicker['AAPL.Low'].min()
        yCandleMax = dfTicker['AAPL.High'].max()
        yVolumeMin = dfTicker['AAPL.Volume'].min()
        yVolumeMax = dfTicker['AAPL.Volume'].max()
        ntail = 90 # display last 90 records (~3 months) by default
        dfTickerTail = dfTicker.tail(ntail)
        dateEnd = dateMax
        dateStart = dfTickerTail['Date'].iloc[0]
        niceDateEnd = datetime.strptime(dateEnd, '%Y-%m-%d') + timedelta(hours=12)
        niceDateStart = datetime.strptime(dateStart, '%Y-%m-%d') - timedelta(hours=12)
        yCandleStart = dfTickerTail['AAPL.Low'].min() # auto rescale to chosen date range
        yCandleEnd = dfTickerTail['AAPL.High'].max()
        yVolumeStart = dfTickerTail['AAPL.Volume'].min()
        yVolumeEnd = dfTickerTail['AAPL.Volume'].max()

        dprTicker = dcc.DatePickerRange(
            id='dprTicker',
            end_date=dateEnd,
            start_date=dateStart,
        )
        figTicker = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.8, 0.2], # volume subplot is much shorter than candle stick
        )
        figTicker.add_trace(go.Candlestick(
            x=dfTicker['Date'],
            open=dfTicker['AAPL.Open'],
            high=dfTicker['AAPL.High'],
            low=dfTicker['AAPL.Low'],
            close=dfTicker['AAPL.Close'],
            increasing_line_color='green', # just make sure it's pure green and red
            decreasing_line_color='red',
            hoverinfo='none', # has to be exactly 'none' instead of None to suppress the tooltip but still fire up hover event
        ), row=1, col=1)
        figTicker.add_trace(go.Bar(
            x=dfTicker['Date'],
            y=dfTicker['AAPL.Volume'],
            opacity=0.3,
            hoverinfo='none',
        ), row=2, col=1)
        figTicker.update_xaxes(dict(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='gray',
            spikedash='dot',
            spikethickness=1,
            showgrid=False,
            range=[niceDateStart,niceDateEnd],
        )) # remove vertical grid lines
        figTicker.update_yaxes(
            dict(
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                spikecolor='gray',
                spikedash='dot',
                spikethickness=1,
            )
        )
        figTicker.update_yaxes(range=[yCandleStart,yCandleEnd], row=1, col=1) # set some default to y range
        figTicker.update_yaxes(range=[yVolumeStart,yVolumeEnd], row=2, col=1)
        figTicker.update_layout(
            hovermode='x',
            margin=dict(l=5, r=5, t=5, b=5),
            xaxis_rangeslider_visible=False,
            showlegend=False,
            template='plotly_dark',
        )
        
        csTicker = dcc.Graph(
            id='csTicker',
            figure=figTicker,
            config={
                'displaylogo': False,
                'modeBarButtonsToRemove': ['select', 'lasso2d', 'zoomIn', 'zoomOut']
            }
        )

        lbTicker = dbc.Label(f"Mã chứng khoán: {tickerID}", id='lbTicker')
        
        return dbc.Container(dbc.Col([
            dprTicker,
            csTicker,
            lbTicker,
        ]))
    else:
        return html.Div(f"Không tìm thấy mã chứng khoán {tickerID}!")

@callback(
    Output('lbTicker', 'children'),
    Input('csTicker', 'hoverData')
)
def printHoverData(hd):
    if (hd):
        j = hd['points'][0]['pointIndex']
        hoverDate = dfTicker['Date'].iloc[j]
        hoverOpen = dfTicker['AAPL.Open'].iloc[j]
        hoverHigh = dfTicker['AAPL.High'].iloc[j]
        hoverLow = dfTicker['AAPL.Low'].iloc[j]
        hoverClose = dfTicker['AAPL.Close'].iloc[j]
        hoverVolume = dfTicker['AAPL.Volume'].iloc[j]
        return f"{hoverDate} O:{hoverOpen:.2f} H:{hoverHigh:.2f} L:{hoverLow:.2f} C:{hoverClose:.2f} Vol:{human_format(hoverVolume)}"
    else:
        return "Detail of a Candle Stick"
    
@callback(
    Output('csTicker', 'figure'),
    Input('dprTicker', 'start_date'),
    Input('dprTicker', 'end_date'),
    prevent_initial_call=True, # dash call each callback once when page initialize
) # function to update plot when user pick date range
def updatePlotXRange(start_date, end_date):
    global figTicker, zoomTriggered
    global yCandleStart, yCandleEnd, yVolumeStart, yVolumeEnd
    
    if zoomTriggered: # called from updateDatePicker, ignore
        zoomTriggered = False
        raise PreventUpdate
    if (start_date is not None) and (end_date is not None):
        nicedateStart = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(hours=12) # half a day before
        nicedateEnd = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(hours=12) # half a day after
        figTicker.update_xaxes(range=[nicedateStart,nicedateEnd])
        figTicker.update_yaxes(range=[yCandleStart,yCandleEnd], row=1, col=1) # somehow updating x also reset y, so I have to update y to prevent reset...o_O
        figTicker.update_yaxes(range=[yVolumeStart,yVolumeEnd], row=2, col=1)
        return figTicker
    else:
        raise PreventUpdate

@callback(
    Output('dprTicker', 'start_date'),
    Output('dprTicker', 'end_date'),
    Input('csTicker', 'relayoutData'),
    prevent_initial_call=True, # dash call each callback once when page initialize
) # function to update date picker when user zoom in/out of the graph
def updateDatePicker(rd):
    global dateMin, dateMax, zoomTriggered
    global yCandleStart, yCandleEnd, yCandleMin, yCandleMax, yVolumeStart, yVolumeEnd, yVolumeMin, yVolumeMax
    if rd:
        # Need to keep track of y range, BEFORE updating the date picker. Damn it.
        if "yaxis.range[0]" in rd: # zoomed in
            yCandleStart = rd["yaxis.range[0]"]
            yCandleEnd = rd["yaxis.range[1]"]
        if "yaxis.autorange" in rd: # zoomed out
            yCandleStart = yCandleMin
            yCandleEnd = yCandleMax
        if "yaxis2.range[0]" in rd: # zoomed in
            yVolumeStart = rd["yaxis2.range[0]"]
            yVolumeEnd = rd["yaxis2.range[1]"]
        if "yaxis2.autorange" in rd: # zoomed out
            yVolumeStart = yVolumeMin
            yVolumeEnd = yVolumeMax
        if "xaxis.range[0]" in rd: # zoomed in
            start_date = rd["xaxis.range[0]"].split()[0] # only take the date part
            end_date = rd["xaxis.range[1]"].split()[0]
            zoomTriggered = True
            return start_date, end_date
        elif "xaxis.autorange" in rd: # zoomed out completely
            start_date = dateMin
            end_date = dateMax
            zoomTriggered = True
            return start_date, end_date
        else: # initial, or zoom only in y direction
            raise PreventUpdate
    else:
        raise PreventUpdate
