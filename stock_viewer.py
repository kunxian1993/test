import dash
from dash import dcc
from dash import html
from dash.dcc.Dropdown import Dropdown
from dash.dependencies import Output, Input, State
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
                        html.Div(children="Stock Ticker", className="menu-title", style={'margin': 10 }),
                        dcc.Textarea(
                            id='xaxis-column',
                            value='CRWD',
                            style={'width': '100%', 'height': 20},
                        ),
                        html.Button('Submit', id='textarea-state-example-button', n_clicks=0),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Metric", className="menu-title", style={'margin': 10 }),
                        dcc.Dropdown(
                            id='yaxis-column',
                            options=[{'label': i, 'value': i} for i in data.columns],
                            value='TotalRevenue',
                            className="dropdown",
                            style={'margin': 10 },
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
    ]
)

@app.callback(
    Output('stock-bar-chart', 'figure'),
    Input('textarea-state-example-button', 'n_clicks'),
    State('xaxis-column', 'value'),
    Input('yaxis-column', 'value'))
def update_graph(n_clicks, selected_stock, selected_metric):
    if n_clicks > 0:
        dff = stock_data.main(str(selected_stock))
        dff.sort_values(by=['Date'], ascending=True, inplace=True)
        fig = px.bar(dff, x="Date", y=selected_metric, color="Ticker", barmode="group")
        fig.update_xaxes(type='category')
        return fig
    else:
        data.sort_values(by=['Date'], ascending=True, inplace=True)
        fig = px.bar(data, x="Date", y=selected_metric, color="Ticker", barmode="group")
        fig.update_xaxes(type='category')
        return fig

if __name__ == "__main__":
    app.run_server(debug=True)


