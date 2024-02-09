import math

from django.shortcuts import render
from django_plotly_dash import DjangoDash
from dash import html, dcc, dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_ta import bbands
import numpy as np
import datetime
from scipy.stats import pearsonr
import yfinance as yf

from indicatorapp.models import Item, Ohlcv

sector_stocks = {
    'Crypto': ['BTC-USD', 'ETH-USD', 'USDT-USD', 'USDC-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOGE-USD'],
    'Stock': ['TSLA', 'AAPL', 'MARA', 'SOFI', 'AMD', 'MIO', 'F', 'LTHM'],
    # 'Futures': ['ES=F', 'YM=F', 'NQ=F', 'RTY=F', 'ZB=F', 'GC=F'],
}

min_date = '2023-01-01'
max_date = '2023-12-31'


def TestView(request):
    event_data = Ohlcv.objects.filter(symbol__exact="ETH-USD")
    return render(request, 'indicatorapp/test.html', {'event_data': event_data})

# https://python.plainenglish.io/stock-analysis-dashboard-with-python-366d431c8721
def index(request):

    ambev = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact="ETH-USD").values()))
    ambev.set_index(ambev['timestamp'], inplace=True)
    # 'ambev_variation' is a complementary information stored inside the card that
    # shows the stock's current price (to be built futurely). It presents, as its
    # variable name already suggests, the stock's price variation when compared to
    # its previous value.
    ambev_variation = 1 - (ambev['Close'].iloc[-1] / ambev['Close'].iloc[-2])

    # 'fig' exposes the candlestick chart with the prices of the stock since 2015.
    fig = go.Figure()

    # Observe that we are promtly filling the charts with AMBEV's data.
    fig.add_trace(go.Candlestick(x=ambev.index,
                                 open=ambev['Open'],
                                 close=ambev['Close'],
                                 high=ambev['High'],
                                 low=ambev['Low'],
                                 name='Stock Price'))
    fig.update_layout(
        margin=dict(l=10, r=10, b=5, t=5),
        autosize=True,
        showlegend=False,
        template = 'plotly_white',
    )
    # Setting the graph to display the 2021 prices in a first moment.
    # Nonetheless,the user can also manually ajust the zoom size either by selecting a
    # section of the chart or using one of the time span buttons available.

    # These two variables are going to be of use for the time span buttons.
    global min_date, max_date
    fig.update_xaxes(range=[min_date, max_date])
    fig.update_yaxes(tickprefix='$')

    # The output from this small resample operation feeds the weekly average price chart.
    ambev_mean_52 = ambev.resample('W')['Close'].mean().iloc[-52:]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=ambev_mean_52.index, y=ambev_mean_52.values))
    fig2.update_layout(
        title={'text': 'Weekly Average Price', 'y': 0.9},
        font={'size': 8},
        margin=dict(l=10, r=10, b=5, t=5),
        autosize=True,
        showlegend=False,
        template='plotly_white',
    )
    fig2.update_xaxes(showticklabels=False, showgrid=False)
    fig2.update_yaxes(range=[ambev_mean_52.min() - 1, ambev_mean_52.max() + 1.5],
                      showticklabels=False, gridcolor='darkgrey', showgrid=False)

    # Making a speedometer chart which indicates the stock' minimum and maximum closing prices
    # reached during the last 52 weeks along its current price.
    df_52_weeks_min = ambev.resample('W')['Close'].min()[-52:].min()
    df_52_weeks_max = ambev.resample('W')['Close'].max()[-52:].max()
    current_price = ambev.iloc[-1]['Close']
    fig3 = go.Figure()
    fig3.add_trace(go.Indicator(mode='gauge+number', value=current_price,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={
                                    'axis': {'range': [df_52_weeks_min, df_52_weeks_max]},
                                    'bar': {'color': '#606bf3'}}))
    fig3.update_layout(
        title={'text': 'Min-Max Prices', 'y': 0.9},
        font={'size': 8},
        margin=dict(l=35, r=0, b=5, t=5),
        autosize=True,
        showlegend=False,
        template='plotly_white',
    )

    # 1. Data Collection & Cleaning (Continuance)

    # A function that is going to measure the stocks' price variation.
    def variation(name):
        df = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact=f"{name}").values()))
        df.set_index(df['timestamp'], inplace=True)
        # tick = yf.Ticker(f"{name}")
        # df = tick.history(period='1wk')
        return 1 - (df['Close'].iloc[-1] / df['Close'].iloc[-2])

    # Listing the companies to be shown in the Carousel.
    carousel_stocks = ['BTC-USD', 'ETH-USD', 'USDT-USD', 'USDC-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOGE-USD']

    # This dictionary will later be converted into a json file.
    carousel_prices = {}
    for stock in carousel_stocks:
        # Applying the 'variation' function for each of the list elements.
        carousel_prices[stock] = variation(stock)

    sector_stocks = {
        'Crypto': ['BTC-USD', 'ETH-USD', 'USDT-USD', 'USDC-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOGE-USD'],
        'Stock': ['TSLA', 'AAPL', 'MARA', 'SOFI', 'AMD', 'MIO', 'F', 'LTHM'],
        # 'Futures': ['ES=F', 'YM=F', 'NQ=F', 'RTY=F', 'ZB=F', 'GC=F'],
    }

    # 3. Application's Layout
    app = DjangoDash(
        'indicatorapp',
        suppress_callback_exceptions=True,
        add_bootstrap_links=True,
        # external_stylesheets=[dbc.themes.CYBORG],
    )

    # Beginning the layout. The whole dashboard is contained inside a Div and a Bootstrap Row.
    app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                # This row holds the dropdowns responsible for the selection of the stock
                # which informations are going to be displayed.
                dbc.Row([
                    # Both dropdowns are placed inside two Bootstrap columns with equal length.
                    dbc.Col([
                        # A small title guiding the user on how to use the component.
                        html.Label('Select the desired sector',
                                   style={'margin-right': '15px', 'margin-left': '15px'},),

                        # The economic sectors dropdown. It mentions all the ones that are
                        # available in the 'sector_stocks' dictionary.
                        dcc.Dropdown(options=[{'label': sector, 'value': sector}
                                              for sector in sorted(list(sector_stocks.keys()))],
                                     value='Crypto',
                                     id='sectors-dropdown',
                                     style={'margin-right': '15px', 'margin-left': '15px'},
                                     searchable=False,
                                     clearable=False,
                                     )
                    ], width=6),

                    # The column holding the stock names dropdown.
                    dbc.Col([
                        # Nothing new here. Just using the same commands as above.
                        html.Label('Select the stock to be displayed',
                                   style={'margin-right': '15px', 'margin-left': '15px'},),
                        dcc.Dropdown(
                            id='stocks-dropdown',
                            style={'margin-right': '15px', 'margin-left': '15px'},
                            searchable=False,
                            clearable=False,
                        )
                    ], width=6),

                    dbc.Row([

                        # Firstly, the candlestick chart is invoked. It is contained in a dcc.Loading
                        # object, which presents a loading animation while the data is retrieved.
                        dcc.Loading(
                            [dcc.Graph(id='price-chart', figure=fig)],
                            id='loading-price-chart', type='dot', color='#1F51FF'),

                        # Next, this row will store the time span buttons as well
                        # as the indicators checklist
                        dbc.Row([

                            # The buttons occupy 1/3 of the available width.
                            dbc.Col([

                                # This Div contains the time span buttons for adjusting
                                # of the x-axis' length.
                                html.Div([
                                    html.Button('1W', id='1W-button',
                                                n_clicks=0, className='btn-secondary'),
                                    html.Button('1M', id='1M-button',
                                                n_clicks=0, className='btn-secondary'),
                                    html.Button('3M', id='3M-button',
                                                n_clicks=0, className='btn-secondary'),
                                    html.Button('6M', id='6M-button',
                                                n_clicks=0, className='btn-secondary'),
                                    html.Button('1Y', id='1Y-button',
                                                n_clicks=0, className='btn-secondary'),
                                    html.Button('3Y', id='3Y-button',
                                                n_clicks=0, className='btn-secondary'),

                                ], style={'padding': '15px', 'margin-left': '35px'})
                            ], width=6),

                            # The indicators have the remaining two thirds of the space.
                            dbc.Col([
                                dcc.Checklist(
                                    ['Rolling Mean',
                                     'Exponential Rolling Mean',
                                     'Bollinger Bands'],
                                    inputStyle={'margin-left': '15px',
                                                'margin-right': '5px'},
                                    id='complements-checklist',
                                    style={'margin-top': '20px'}),
                            ], width=6),
                        ]),
                    ]),
                ]),

                # The left major column closing bracket
            ], width=8),

            # =======================================================

            dbc.Col([
                dbc.Row([
                    # The DataTable stores the prices from the companies that pertain
                    # to the same economic sector as the one chosen in the dropdowns.
                    dcc.Loading([

                        dash_table.DataTable(
                            id='stocks-table',
                            style_cell={
                                'font_size': '12px',
                                'textAlign': 'center'},
                            style_header={
                                'backgroundColor': 'white',
                                'padding-right': '62px',
                                'border': 'none'},
                            style_data={
                                'height': '12px',
                                'backgroundColor': 'white',
                                'border': 'none'},
                            style_table={
                                'height': '200px',
                                'overflowY': 'auto'}
                        )
                    ], id='loading-table', type='circle', color='#1F51FF'),

                ], style={
                    'margin-top': '28px',
                    'margin-top': '15px',
                    'margin-bottom': '15px',
                    'margin-right': '15px',
                    'margin-left': '15px',
                }),

                # =======================================================

                dbc.Card([
                    # The card below presents the selected stock's current price.
                    dbc.CardBody([
                        # Recall that the name shown as default needs to be 'ABEV3',
                        # since it is the panel's standard stock.
                        html.H1('ETH-USD', id='stock-name', style={'font-size': '13px', 'text-align': 'center'}),
                        dbc.Row([
                            dbc.Col([
                                # Placing the current price.
                                html.P('$ {:.2f}'.format(ambev['Close'].iloc[-1]),
                                       id='stock-price', style={
                                        'font-size': '30px', 'margin-left': '5px'})
                            ], width=8),
                            dbc.Col([
                                # This another paragraph shows the price variation.
                                html.P(
                                    '{}{:.2%}'.format(
                                        '+' if ambev_variation > 0 else '', ambev_variation),
                                    id='stock-variation',
                                    style={'font-size': '20px',
                                           # 'margin-top': '25px',
                                           'color': 'green' if ambev_variation > 0 else 'red'})
                            ], width=4)
                        ])
                    ])
                ], id='stock-data',
                   style={
                       'height': '105px',
                       'margin-top': '15px',
                       'margin-bottom': '15px',
                       'margin-right': '15px',
                       'margin-left': '15px',
                   },
                   color='white'),

                # =======================================================

                html.Hr(
                    style={
                       'margin-right': '15px',
                       'margin-left': '15px',
                   }
                ),

                # =======================================================

                dbc.Col([
                    html.H1('52-Week Data',
                            style={'font-size': '25px', 'text-align': 'center',
                                    'color': 'grey', 'margin-top': '5px',
                                    'margin-bottom': '0px'}
                    ),
                    # Creating a Carousel showing the stock's weekly average price and a
                    # Speedoemeter displaying how far its current price is from
                    # the minimum and maximum values achieved.

                    html.Div([dcc.Graph(
                        id='52-avg-week-price',
                        figure=fig2,
                    )],
                             style={
                                 'margin-top': '5px',
                                 'margin-right': '15px',
                                 'margin-left': '15px',
                                 "height": "100%",
                             }
                    ),

                    html.Div([dcc.Graph(
                        id='52-week-min-max',
                        figure=fig3,
                    )],
                             style={
                                 'margin-top': '5px',
                                 'margin-right': '15px',
                                 'margin-left': '15px',
                                 "height": "100%",
                             }
                    ),
                ]),

                # =======================================================

                html.Hr(
                    style={
                        'margin-right': '15px',
                        'margin-left': '15px',
                    }
                ),

                # =======================================================

                dbc.Row([
                    # A small title for the section.
                    html.H2('Correlations', style={'font-size': '12px', 'color': 'grey', 'text-align': 'center'}),
                    # dbc.Col([
                    #     # BTCUSD correlation.
                    #     html.Div([
                    #         html.H1('BTCUSD', style={'font-size': '10px'}),
                    #         html.P(id='btcusd-correlation', style={'font-size': '20px', 'margin-top': '5px'})
                    #     ], style={'text-align': 'center'})
                    # ], width=6),
                    dbc.Col([
                        # Sector correlation.
                        html.Div([
                            html.H1('S&P 500', style={'font-size': '10px'}),
                            html.P(id='sector-correlation', style={'font-size': '20px', 'margin-top': '5px'})
                        ], style={'text-align': 'center'})
                    ], width=12),
                ], style={'margin-top': '2px'})

                # =======================================================

                # The right major column closing bracket.
            ], width=4)
        ])
    ])

    @app.callback(
        Output('stocks-dropdown', 'options'),
        Input('sectors-dropdown', 'value')
    )
    def set_symbol_options(sector):
        return [{'label': i, 'value': i} for i in sector_stocks[sector]]

    @app.callback(
        Output('stocks-dropdown', 'value'),
        Input('stocks-dropdown', 'options')
    )
    def set_symbol_value(available_options):
        return available_options[0]['value']

    @app.callback(
        Output('price-chart', 'figure'),
        Input('stocks-dropdown', 'value'),
        Input('complements-checklist', 'value'),
        Input('1W-button', 'n_clicks'),
        Input('1M-button', 'n_clicks'),
        Input('3M-button', 'n_clicks'),
        Input('6M-button', 'n_clicks'),
        Input('1Y-button', 'n_clicks'),
        Input('3Y-button', 'n_clicks'),
    )
    def change_price_chart(stock, checklist_values, button_1w, button_1m, button_3m, button_6m, button_1y, button_3y):
        # Retrieving the stock's data.
        # tick = yf.Ticker(f"{stock}")
        # df = tick.history(period='5y')
        df = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact=f"{stock}").values()))
        df.set_index(df['timestamp'], inplace=True)

        # Applying some indicators to its closing prices. Below we are measuring
        # Bollinger Bands.
        df_bbands = bbands(df['Close'].astype('float'), length=20, std=2)

        # Measuring the Rolling Mean and Exponential Rolling means
        df['Rolling Mean'] = df['Close'].rolling(window=9).mean()
        df['Exponential Rolling Mean'] = df['Close'].ewm(span=9, adjust=False).mean()

        # Each metric will have its own color in the chart.
        colors = {'Rolling Mean': '#6fa8dc',
                  'Exponential Rolling Mean': '#03396c', 'Bollinger Bands Low': 'darkorange',
                  'Bollinger Bands AVG': 'brown',
                  'Bollinger Bands High': 'darkorange'}

        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], close=df['Close'],
                                     high=df['High'], low=df['Low'], name='Stock Price'))

        # If the user has selected any of the indicators in the checklist, we'll represent it in the chart.
        if checklist_values != None:
            for metric in checklist_values:

                # Adding the Bollinger Bands' typical three lines.
                if metric == 'Bollinger Bands':
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df_bbands.iloc[:, 0],
                        mode='lines', name=metric,
                        line={'color': colors['Bollinger Bands Low'], 'width': 1}))

                    fig.add_trace(go.Scatter(
                        x=df.index, y=df_bbands.iloc[:, 1],
                        mode='lines', name=metric,
                        line={'color': colors['Bollinger Bands AVG'], 'width': 1}))

                    fig.add_trace(go.Scatter(
                        x=df.index, y=df_bbands.iloc[:, 2],
                        mode='lines', name=metric,
                        line={'color': colors['Bollinger Bands High'], 'width': 1}))

                # Plotting any of the other metrics remained, if they are chosen.
                else:
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df[metric], mode='lines', name=metric,
                        line={'color': colors[metric], 'width': 1}))

        fig.update_layout(
            margin=dict(l=10, r=10, b=5, t=5),
            autosize=False,
            showlegend=False,
            template='plotly_white',
        )
        # Defining the chart's x-axis length according to the button clicked.
        # To do this, we'll alter the 'min_date' and 'max_date' global variables that were
        # defined in the beginning of the script.
        global min_date, max_date
        # changed_id = ctx.triggered[0]["prop_id"].split(".")
        # if '1W-button' in changed_id:
        #     min_date = df.iloc[-1].name - datetime.timedelta(7)
        #     max_date = df.iloc[-1].name
        # elif '1M-button' in changed_id:
        #     min_date = df.iloc[-1].name - datetime.timedelta(30)
        #     max_date = df.iloc[-1].name
        # elif '3M-button' in changed_id:
        #     min_date = df.iloc[-1].name - datetime.timedelta(90)
        #     max_date = df.iloc[-1].name
        # elif '6M-button' in changed_id:
        #     min_date = df.iloc[-1].name - datetime.timedelta(180)
        #     max_date = df.iloc[-1].name
        # elif '1Y-button' in changed_id:
        #     min_date = df.iloc[-1].name - datetime.timedelta(365)
        #     max_date = df.iloc[-1].name
        # elif '3Y-button' in changed_id:
        #     min_date = df.iloc[-1].name - datetime.timedelta(1095)
        #     max_date = df.iloc[-1].name
        # else:
        #     min_date = min_date
        #     max_date = max_date
        #     fig.update_xaxes(range=[min_date, max_date])
        #     fig.update_yaxes(tickprefix='$')
        #     return fig

        # Updating the x-axis range.
        fig.update_xaxes(range=[min_date, max_date])
        fig.update_yaxes(tickprefix='$')
        return fig

    @app.callback(
        Output('stocks-table', 'data'),
        Output('stocks-table', 'columns'),
        Input('sectors-dropdown', 'value')
    )
    # Updating the panel's DataTable
    def update_stocks_table(sector):
        global sector_stocks
        # This DataFrame will be the base for the table.
        df = pd.DataFrame({'Stock': [stock for stock in sector_stocks[sector]],
                           'Close': [np.nan for i in range(len(sector_stocks[sector]))]},
                          index=[stock for stock in sector_stocks[sector]])
        # Each one of the stock names and their respective prices are going to be stored
        # in the 'df'  DataFrame.
        for stock in sector_stocks[sector]:
            tick = yf.Ticker(f"{stock}")
            stock_value = tick.history(period='1wk')['Close'].iloc[1]

            # stock_value = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact=f"{stock}").values()))[['Close', 'timestamp']].iloc[1]
            # stock_value.set_index(stock_value['timestamp'], inplace=True)

            df = df.astype({'Close': 'str'})
            df.loc[stock, 'Close'] = f'$ {stock_value :.2f}'

        # Finally, the DataFrame cell values are stored in a dictionary and its column
        # names in a list of dictionaries.
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]

    @app.callback(
        Output('stock-name', 'children'),
        Output('stock-price', 'children'),
        Output('stock-variation', 'children'),
        Output('stock-variation', 'style'),
        Input('stocks-dropdown', 'value')
    )
    def update_stock_data_card(stock):
        # Retrieving data from the Yahoo Finance API.
        tick = yf.Ticker(f"{stock}")
        df = tick.history(period='1wk')['Close']
        # df = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact=f"{stock}").values()))[['Close', 'timestamp']]
        # df.set_index(df['timestamp'], inplace=True)
        # df.drop(columns=['timestamp'], inplace=True)
        # df['Close'] = df['Close'].astype('float')

        # Getting the chosen stock's current price and variation in comparison to
        # its previous value.
        stock_current_price = df.iloc[-1]
        stock_variation = 1 - (df.iloc[-1] / df.iloc[-2])

        # Note that as in the Carousel, the varitation value will be painted in red or
        # green depending if it is a negative or positive number.
        return (
            stock,
            '$ {:.2f}'.format(stock_current_price),
            '{}{:.2%}'.format('+' if stock_variation > 0 else '', stock_variation),
            {'font-size': '14px', 'margin-top': '25px', 'color': 'green' if stock_variation > 0 else 'red'}
        )

    @app.callback(
        Output('52-avg-week-price', 'figure'),
        Input('stocks-dropdown', 'value')
    )
    def update_average_weekly_price(stock):
        # Receiving the stock's prices and measuring its average weekly price
        # in the last 52 weeks.
        tick = yf.Ticker(f"{stock}")
        df = tick.history(period='2y')['Close']

        # df = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact=f"{stock}").values()))[['Close', 'timestamp']]
        # df.set_index(df['timestamp'], inplace=True)
        # df.drop(columns=['timestamp'], inplace=True)

        df.index = pd.to_datetime(df.index)
        df_avg_52 = df.resample('W').mean().iloc[-52:]

        # Plotting the data in a line chart.
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_avg_52.index, y=df_avg_52.values))
        fig2.update_layout(
            title={'text': 'Weekly Average Price', 'y': 0.9},
            font={'size': 8},
            height=220,
            margin=dict(l=10, r=10, b=5, t=5),
            autosize=False,
            showlegend=False,
            template='plotly_white',
        )
        fig2.update_xaxes(tickformat='%m-%y', showticklabels=False,
                          gridcolor='darkgrey', showgrid=False)
        fig2.update_yaxes(range=[df_avg_52.min() - 1, df_avg_52.max() + 1.5],
                          showticklabels=False, gridcolor='darkgrey', showgrid=False)
        return fig2

    # This function will update the speedometer chart.
    @app.callback(
        Output('52-week-min-max', 'figure'),
        Input('stocks-dropdown', 'value')
    )
    def update_min_max(stock):
        # The same logic as 'update_average_weekly_price', but instead we are getting
        # the minimum and maximum prices reached in the last 52 weeks and comparing
        # them with the stock's current price.
        tick = yf.Ticker(f"{stock}")
        df = tick.history(period='2y')['Close']

        # df = pd.DataFrame(list(Ohlcv.objects.filter(symbol__exact=f"{stock}").values()))[['Close', 'timestamp']]
        # df.set_index(df['timestamp'], inplace=True)
        # df.drop(columns=['timestamp'], inplace=True)
        # df['Close'] = df['Close'].astype('float')

        df.index = pd.to_datetime(df.index)
        df_avg_52 = df.resample('W').mean().iloc[-52:]
        df_52_weeks_min = df_avg_52.resample('W').min()[-52:].min()
        df_52_weeks_max = df_avg_52.resample('W').max()[-52:].max()
        current_price = df.iloc[-1]
        fig3 = go.Figure()
        fig3.add_trace(go.Indicator(mode='gauge+number', value=current_price,
                                    domain={'x': [0, 1], 'y': [0, 1]},
                                    gauge={
                                        'axis': {'range': [df_52_weeks_min, df_52_weeks_max]},
                                        'bar': {'color': '#606bf3'}}))
        fig3.update_layout(
            title={'text': 'Min-Max Prices', 'y': 0.9},
            font={'size': 8},
            margin=dict(l=35, r=0, b=5, t=5),
            autosize=False,
            showlegend=False,
            template='plotly_white',
        )
        return fig3

    @app.callback(
        Output('btcusd-correlation', 'children'),
        Input('stocks-dropdown', 'value'),
    )
    def btcusd_correlation(stock):
        start = datetime.datetime(2023, 12, 31).date() - datetime.timedelta(days=7 * 52)
        end = datetime.datetime(2023, 12, 31).date()

        btcusd = yf.Ticker('BTC-USD').history(start=start, end=end)['Close']
        stock_close = yf.Ticker(f'{stock}').history(start=start, end=end)['Close']

        df = pd.concat([btcusd, stock_close], axis=1, join='inner')
        df.columns = ['btcusd', 'stock']
        df.dropna(inplace=True)

        # Returning the correlation coefficient.
        return f"{pearsonr(df.btcusd, df.stock)[0] :.2%}"

    @app.callback(
        Output('sector-correlation', 'children'),
        Input('sectors-dropdown', 'value'),
        Input('stocks-dropdown', 'value')
    )
    def sector_correlation(sector, stock):
        start = datetime.datetime(2023, 12, 31).date() - datetime.timedelta(days=7 * 52)
        end = datetime.datetime(2023, 12, 31).date()

        # Retrieving the daily closing prices from the selected stocks in the prior 52 weeks.
        tick = yf.Ticker(f'{stock}')
        stock_close = tick.history(start=start, end=end)['Close']

        # Creating a DataFrame that will store the prices in the past 52 weeks
        # from all the stocks that pertain to the economic domain selected.
        sector_df = pd.DataFrame()

        # Retrieving the price for each of the stocks included in 'sector_stocks'
        global sector_stocks
        stocks_from_sector = [stock_ for stock_ in sector_stocks[sector]]
        for stock_ in stocks_from_sector:
            tick = yf.Ticker(f'{stock_}')
            sector_df[stock_] = tick.history(start=start, end=end)['Close']

        # With all the prices obtained, let's measure the sector's daily average value.
        sector_daily_average = sector_df.mean(axis=1)

        # Now, returning the correlation coefficient.
        return f'{pearsonr(sector_daily_average, stock_close)[0] :.2%}'


    return render(request, 'indicatorapp/index.html')


def crawler(request):

    sector_stocks = {
        'Crypto': ['BTC-USD', 'ETH-USD', 'USDT-USD', 'USDC-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOGE-USD'],
        'Stock': ['TSLA', 'AAPL', 'MARA', 'SOFI', 'AMD', 'MIO', 'F', 'LTHM'],
        # 'Futures': ['ES=F', 'YM=F', 'NQ=F', 'RTY=F', 'ZB=F', 'GC=F'],
    }

    for sc in sector_stocks['Crypto']:
        tick = yf.Ticker(sc)
        df = tick.history(period='5y')
        i = Item.objects.create(
            symbol=sc,
            name=sc,
            country='',
            market='',
            sectorName='',
            sectorSymbol='',
        )
        i.save()
        for index, row in df.iterrows():
            digit = digit_length(row['Open'])
            o = Ohlcv.objects.create(
                symbol=sc,
                interval = '1d',
                timestamp = index,
                open = round(row['Open'], 8-digit),
                high = round(row['High'], 8-digit),
                low = round(row['Low'], 8-digit),
                close = round(row['Close'], 8-digit),
                volume = row['Volume'],
            )
            o.save()


    for ss in sector_stocks['Stock']:
        tick = yf.Ticker(ss)
        df = tick.history(period='5y')
        i = Item.objects.create(
            symbol=ss,
            name=ss,
            country='',
            market='',
            sectorName='',
            sectorSymbol='',
        )
        i.save()
        for index, row in df.iterrows():
            digit = digit_length(row['Open'])
            o = Ohlcv.objects.create(
                symbol=ss,
                interval='1d',
                timestamp=index,
                open=round(row['Open'], 8-digit),
                high=round(row['High'], 8-digit),
                low=round(row['Low'], 8-digit),
                close=round(row['Close'], 8-digit),
                volume=row['Volume'],
            )
            o.save()

    return render(request, 'indicatorapp/crawler.html')

def digit_length(n):
    return int(math.log10(n)) + 1 if n else 0