import dash
from dash import dcc
from dash import html
from dash.dcc.Dropdown import Dropdown
from dash.dependencies import Output, Input, State
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from yf_scraper import stock_data

# data = pd.read_csv("SummaryStore.csv")
# data.sort_values("endDate", inplace=True)
data = stock_data.extract_timeSeriesStore("CRWD")

# external_stylesheets = [
#     {
#         "href": "https://fonts.googleapis.com/css2?"
#                 "family=Lato:wght@400;700&display=swap",
#         "rel": "stylesheet"
#     },
# ]

app = dash.Dash(__name__)
app.title = "Stock Data Analytics"
server = app.server

# fig = px.bar(data, x="Ticker", y="TotalRevenue", color="Date", barmode="group")

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📊", className="header-emoji"),
                html.H1(children="Stock Data", className="header-title"),
                html.P(children="Analyze Stock Data", className="header-description")
                ],
                className="header",
            ),
        # html.Div(
        #     dcc.Dropdown(
        #         id='xaxis-column',
        #         options=[{'label': i, 'value': i} for i in data['Ticker'].unique()],
        #         value='CRWD'
        #     ),
        # ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Stock Ticker", className="menu-title"),
                        dcc.Input(
                            id='xaxis-column',
                            placeholder='Ticker Symbol',
                            value = 'TSLA',
                            style={'width': '80%', 'height': '25%', 'font-size': '16px', 'margin-top': '5px'},
                            type='text'
                        ),
                        html.Button('SUBMIT', id='text-submit-button', n_clicks=0, style = {'margin-top': '5px'}),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Metric", className="menu-title"),
                        dcc.Dropdown(
                            id='yaxis-column',
                            options=[{'label': i, 'value': i} for i in data.columns],
                            value='TotalRevenue',
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(dcc.Graph(id='stock-bar-chart'), className="card",)
                ],
                className="wrapper",
        ),
        html.Div(
            children=[
                html.Div(dcc.Graph(id='stock-bar-chart-2'), className="card",)
                ],
                className="wrapper",
        ),
    ]
)

@app.callback(
    Output('yaxis-column', 'options'),
    Output('stock-bar-chart', 'figure'),
    Output('stock-bar-chart-2', 'figure'),
    Input('text-submit-button', 'n_clicks'),
    State('xaxis-column', 'value'),
    Input('yaxis-column', 'value'))
def update_graph(n_clicks, selected_stock, selected_metric):
        dff = stock_data.extract_timeSeriesStore(str(selected_stock))
        data.sort_values(by=['Date'], ascending=True, inplace=True)

        fig = px.bar(dff, x="Date", y=selected_metric, color="Ticker", barmode="group")
        fig.update_xaxes(type='category')

        fig_2 = make_subplots(rows=1, cols=2, subplot_titles=["TotalRevenue","NetIncome"])
        fig_2.add_trace(go.Bar(x=dff["Date"], y=dff["TotalRevenue"], name="TotalRevenue"), row=1, col=1)
        fig_2.add_trace(go.Bar(x=dff["Date"], y=dff["NetIncome"], name="NetIncome"), row=1, col=2)
        fig_2.update_xaxes(type='category')

        options=[{'label': i, 'value': i} for i in dff.columns]
        return options, fig, fig_2

if __name__ == "__main__":
    app.run_server(debug=True)


