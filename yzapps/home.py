# Usual Dash dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
# Let us import the app object in case we need to define
# callbacks here
from app import app

# store the layout objects into a variable named layout

layout = html.Div(
        [
            html.H2('Welcome to our app!'),
            html.Hr(),
            dbc.Card (
                [
                dbc.CardHeader(
                    [
                        html.H3('Quick Menu')
                    ]
                ),
                dbc.CardBody(
                    [
                    html.Div(
                                [
                                    dbc.Button('Make Staff Report', color="secondary", href='/modules/staff_report_profile?mode=add'),
                                ]
                                
                            ),
                    html.Hr(),
                    html.Div(
                                [
                                    dbc.Button('Generate Transaction', color="secondary", href='/modules/transaction_profile?mode=add'),
                                ]
                                
                            ),
                    html.Hr(),
                    html.Div(
                        [
                        html.H5(
                            "Thru this app, you can manage the inventory."
                        ),
                        ]
                    )
                ])
            ])
        ]
    )
