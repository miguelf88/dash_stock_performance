import yfinance as yf
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd


# ------------------------------------------------
# external_stylesheets = ['codepen url']

app = dash.Dash(__name__)  # external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True


# ------------------------------------------------
# set the layout
app.layout = html.Div([

    html.H1('Stock Dashboard version 2.0'),

    html.Label(['Enter stock symbols separated by a comma: '], style={'font-weight': 'bold'}),

    html.Br(),

    dcc.Input(id='tickers',
              type='text',
              debounce=True,
              autoFocus=True,
              value='spy, gbtc, vnq, pltr',
              spellCheck=False,
              style={'width': "20%"}),

    html.Br(),

    html.Div([

        dbc.Row([
            dbc.Col(dcc.Graph(
                id='corr_chart',
                config={'displayModeBar': False}
            )),
            dbc.Col(dcc.Graph(
                id='performance_chart',
                config={'displayModeBar': False}
            ))
        ]),

        dbc.Row([
            dbc.Col(html.P(id='corr_desc', style={'width': '80%'})),
            dbc.Col(html.P('PLACEHOLDER'))
        ])
    ])

])


# -----------------------------------------------------

# callback to content
@app.callback(
    [Output('corr_chart', 'figure'),
     Output('corr_desc', 'children'),
     Output('performance_chart', 'figure')],
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

    return corr_matrix, statement, performance_chart


# -----------------------------------------------------
# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
