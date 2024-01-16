#For YZAPP
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate

from app import app

navlink_style = {
    'color': '#000000'
}
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "2rem 1rem",
    "background-color": "#ADD8E6",
    "overflow": "Auto"
}
# the styles for the main content position it to the right of the sidebar and
# add some padding.

navbar = html.Div(
    [
        html.H2("YZApp", className="display-5"),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", style=navlink_style),
                dbc.NavLink("Transaction", href="/modules/transaction", style=navlink_style),
                dbc.NavLink("Supplies", href="/modules/supplies", style=navlink_style),
                dbc.NavLink("Analytics", href="/modules/analytics", style=navlink_style),
                dbc.NavLink("Staff", href="/modules/staff", style=navlink_style),
                dbc.NavLink("Staff Report", href="/modules/staff_report", style=navlink_style),
                dbc.NavLink("Customers", href="/modules/customers", style=navlink_style),
                dbc.NavLink("Occupation", href="/modules/occupation", style=navlink_style),
                dbc.NavLink("Suppliers", href="/modules/suppliers", style=navlink_style),
                dbc.NavLink("Category", href="/modules/category", style=navlink_style),
                dbc.NavLink("Material", href="/modules/material", style=navlink_style),
                dbc.NavLink("Status", href="/modules/status", style=navlink_style),
                dbc.NavLink("Services", href="/modules/services", style=navlink_style),
                dbc.NavLink("Users", href="/modules/users", style=navlink_style),
                dbc.NavLink("Logout", href="/logout", style=navlink_style),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)