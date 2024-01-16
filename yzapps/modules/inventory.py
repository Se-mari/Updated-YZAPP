# Usual Dash dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app

# store the layout objects into a variable named layout
layout = html.Div(
        [
            html.H2('Inventory'),
            html.Hr(),
            html.Div(
                [
                    html.Span(
                        "Add tables, etc",
                    ),
                    html.Br(),
                    html.Br(),
                    html.Span(
                        "Still a WIP",
                        style={'font-style':'italic'}
                    ),
                ]
                )
            ]
        )