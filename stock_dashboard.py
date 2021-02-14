import yfinance as yf
import dash
import dash_table as dt
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table.Format import Format
import plotly.express as px

import pandas as pd


# ------------------------------------------------

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server
app.config.suppress_callback_exceptions = True


# ------------------------------------------------
# set the layout

app.layout = html.Div([

    html.H1(
        'Stock Dashboard version 2.0',
        style={
            'padding-top': '15px',
            'padding-left': '10px',
            'padding-bottom': '5px',
            'color': 'white',
            'font-weight': 'bold'
        }, className="navbar navbar-expand-lg navbar-dark bg-primary"),

    html.Div([

        html.Label(
            ['Enter stock symbols separated by a comma: '],
            style={
                'color': '#111111',
                'font-weight': 'bold'
            }
        ),

        html.Br(),

        dcc.Input(
            id='tickers',
            type='text',
            debounce=True,
            autoFocus=True,
            value='spy, gbtc',  # , vnq, pltr',
            spellCheck=False,
            style={'width': "20%"},
        )

    ], style={
        'background-color': '#E8E8E8',
        'padding-left': '12px',
        'padding-bottom': '10px',
        'padding-top': '12px',
        'margin-top': '-8px'
    }),

    html.Br(),

    html.Div([

        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='corr_chart',
                    config={'displayModeBar': False}
                ), width=5
            ),
            dbc.Col(
                dcc.Graph(
                    id='performance_chart',
                    config={'displayModeBar': False}
                ), width={
                    'size': 6,
                    'offset': 1
                }
            )
        ]),

        dbc.Row([
            dbc.Col(
                html.P(
                    id='corr_desc',
                    style={'width': '80%'}
                )
            ),
            dbc.Col(
                html.Div(
                    id='performance_table',
                    style={
                        'padding-right': '30px'
                    }
                )
            )
        ])
    ], id='content'),

    html.Footer(
        [
            'Created by ',
            html.A(
                'Miguel Fernandez',
                href='https://miguelf88.github.io/',
                target='_blank'
            ),
            ' using ',
            html.A(
                'Dash by Plotly',
                href='https://plotly.com/dash/',
                target='_blank'
            ),
            ', 2021'
        ],
        style={
            'position': 'absolute',
            'bottom': 0,
            'background-color': '#E8E8E8',
            'width': '100%',
            'padding-top': '10px',
            'padding-right': '20px',
            'padding-bottom': '10px',
            'text-align': 'right'
        }
    )

])
# -----------------------------------------------------

# callback to content
@app.callback(
    [Output('corr_chart', 'figure'),
     Output('corr_desc', 'children'),
     Output('performance_chart', 'figure'),
     Output('performance_table', 'children')],
    [Input('tickers', 'value')]
)
def correlation_analysis(tickers):

    # list of tickers
    tickers = tickers.replace(' ', '').split(',')
    # converts list to uppercase
    for ticker in range(len(tickers)):
        tickers[ticker] = tickers[ticker].upper()

    # create empty dataframe
    stocks = pd.DataFrame()

    # iterate through tickers and grab
    # all historical closing prices
    # and append to dataframe
    for ticker in tickers:
        symbol = yf.Ticker(ticker)
        stock_close = symbol.history(period='max')['Close']
        stocks = stocks.append(stock_close)

    # reshape dataframe and rename columns
    stocks = stocks.transpose()
    stocks.columns = tickers

    # create correlation matrix
    corr_matrix = px.imshow(
        stocks.corr()[tickers],
        title='Correlation Matrix'
    )

    # define function to get lower part of correlation matrix
    def get_redundant_pairs(df):
        pairs_to_drop = set()
        cols = df.columns
        for i in range(0, df.shape[1]):
            for j in range(0, i + 1):
                pairs_to_drop.add((cols[i], cols[j]))
        return pairs_to_drop

    # reshape dataframe
    au_corr = stocks.corr().abs().unstack()
    labels_to_drop = get_redundant_pairs(stocks)

    # get the top correlated pair
    au_corr_top = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
    top_corr_label_1 = au_corr_top.index[0][0]
    top_corr_label_2 = au_corr_top.index[0][1]
    top_corr_value = round(au_corr_top[0], 2)

    # get the bottom correlated pair
    au_corr_low = au_corr.drop(labels=labels_to_drop).sort_values(ascending=True)
    low_corr_label_1 = au_corr_low.index[0][0]
    low_corr_label_2 = au_corr_low.index[0][1]
    low_corr_value = round(au_corr_low[0], 2)

    # create statement to return to dashboard
    statement = 'The two symbols with the highest correlation are ' + top_corr_label_1 + ' and ' \
                + top_corr_label_2 + '. They have a correlation of ' + str(top_corr_value) + '. The two symbols' \
                ' with the lowest correlation are ' + low_corr_label_1 + ' and ' + low_corr_label_2 + '. They have' \
                ' a correlation of ' + str(low_corr_value) + '.'

    # generate performance chart
    performance_chart = px.line(
        stocks,
        x=stocks.index,
        y=stocks.columns,
        labels={
            'index': 'Date',
            'value': 'Asset Price',
            'variable': 'Symbol'
        },
        title='Performance Chart',
        template='simple_white'
    )
    performance_chart.update_traces(hovertemplate='Date: %{x}<br>Price: %{y:$,.2f}')
    performance_chart.update_layout(yaxis_tickformat='$')
    performance_chart.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    performance_chart.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
    )

    # generate performance table
    # calculate one day returns
    oneDayReturn = round((stocks.pct_change() * 100).iloc[-1], 2)

    # calculate monthly returns
    monthlyReturns = stocks.resample('M').ffill().pct_change()

    # calculate one month returns
    oneMonthReturn = round(monthlyReturns.iloc[-2] * 100, 2)

    # calculate three month returns
    threeMonthReturn = round(monthlyReturns.iloc[-4:-1].sum() * 100, 2)

    # calculate yearly returns
    yearlyReturns = stocks.resample('Y').ffill().pct_change()

    # calculate year to date returns
    ytdReturn = round(yearlyReturns.iloc[-1] * 100, 2)

    # calculate one year returns
    oneYearReturn = round(yearlyReturns.iloc[-2] * 100, 2)

    # calculate three year returns
    threeYearReturn = round((yearlyReturns.iloc[-4:-1] * 100).dropna(axis=1).mean(), 2)

    # calculate five year returns
    fiveYearReturn = round((yearlyReturns.iloc[-6:-1] * 100).dropna(axis=1).mean(), 2)

    # calculate ten year returns
    tenYearReturn = round((yearlyReturns.iloc[-11:-1] * 100).dropna(axis=1).mean(), 2)

    # create performance table by merging series
    performance_table = pd.concat([
        oneDayReturn, oneMonthReturn, threeMonthReturn, ytdReturn, oneYearReturn, threeYearReturn,
        fiveYearReturn, tenYearReturn
    ], axis=1)
    # reset the index so ticker symbols become column in table
    performance_table.reset_index(inplace=True)
    # name columns
    performance_table.columns = [
        'Asset', '1-Day Return', '1-Month Return', '3-Month Return', 'YTD Return', '1-Year Return', '3-Year Return',
        '5-Year Return', '10-Year Return'
    ]

    # construct the data table
    data = performance_table.to_dict('records')
    columns = [{"name": i, "id": i, } for i in performance_table.columns]
    data_table = dt.DataTable(
        data=data,
        columns=columns,
        sort_action='native',
        style_cell_conditional=[
            {
                'if': {'column_id': 'Asset'},
                'textAlign': 'left'
            }
        ],
        style_header={
            'backgroundColor': '#78C2AD',
            'color': 'white',
            'border': '1px solid white'
        },
        style_data={
            'border': '1px solid white'
        }
    )

    print(performance_table)

    return corr_matrix, statement, performance_chart, data_table


# -----------------------------------------------------
# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
