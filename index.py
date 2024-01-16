# Dash related dependencies
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import webbrowser
from app import app
from yzapps import commonmodules as cm
# navbar
from yzapps import home, login, signup
# modules
from yzapps.modules import job_orders, inventory, supplies, analytics, staff, customers, suppliers, category, services, users, status
from yzapps.modules import  users_profile , staff_profile, category_profile, services_profile, status_profile, suppliers_profile
from yzapps.modules import staff_report, staff_report_profile, material, material_profile, supplies_profile, purchase_profile
from yzapps.modules import customers_profile, occupation, occupation_profile, transaction, transaction_profile
CONTENT_STYLE = {
"margin-left": "12rem",
"margin-right": "2rem",
"padding": "2rem 1rem",
"overflow": "auto"
}

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=True),
        dcc.Store(id='sessionlogout', data=True, storage_type='session'),
        dcc.Store(id='currentuserid', data=-1, storage_type='session'),
        dcc.Store(id='currentrole', data=-1, storage_type='session'),
        html.Div(
            cm.navbar,
            id='navbar_div'
        ),
        html.Div(id='page-content', style=CONTENT_STYLE),
    ]
)

@app.callback(
    [
    Output('page-content', 'children'),
    Output('sessionlogout', 'data'),
    Output('navbar_div', 'className'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
    ]
)
def displaypage (pathname, sessionlogout, userid):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'url':
            if userid < 0 or pathname== '/signup': 
                if pathname == '/':
                    returnlayout = login.layout
                elif pathname == '/signup':
                    returnlayout = signup.layout
                else:
                    returnlayout = '404: request not found'
            else:
                if pathname == '/logout':
                    returnlayout = login.layout
                    sessionlogout = True
                elif pathname == '/' or pathname == '/home':
                    returnlayout = home.layout
                elif pathname =='/modules/job_orders':
                    returnlayout = job_orders.layout   
                elif pathname =='/modules/inventory':
                    returnlayout = inventory.layout
                elif pathname =='/modules/supplies':
                    returnlayout = supplies.layout
                elif pathname =='/modules/supplies_profile':
                    returnlayout = supplies_profile.layout
                elif pathname =='/modules/purchase_profile':
                    returnlayout = purchase_profile.layout
                elif pathname =='/modules/analytics':
                    returnlayout = analytics.layout
                elif pathname =='/modules/transaction':
                    returnlayout = transaction.layout
                elif pathname =='/modules/transaction_profile':
                    returnlayout = transaction_profile.layout
                elif pathname =='/modules/staff':
                    returnlayout = staff.layout
                elif pathname =='/modules/staff_report':
                    returnlayout = staff_report.layout
                elif pathname =='/modules/customers':
                    returnlayout = customers.layout
                elif pathname =='/modules/customers_profile':
                    returnlayout = customers_profile.layout
                elif pathname =='/modules/suppliers':
                    returnlayout = suppliers.layout
                elif pathname =='/modules/category':
                    returnlayout = category.layout
                elif pathname =='/modules/services':
                    returnlayout = services.layout
                elif pathname =='/modules/users':
                    returnlayout = users.layout
                elif pathname =='/modules/status':
                    returnlayout = status.layout
                elif pathname =='/modules/staff_profile':
                    returnlayout = staff_profile.layout    
                elif pathname =='/modules/users_profile':
                    returnlayout = users_profile.layout  
                elif pathname =='/modules/category_profile':
                    returnlayout = category_profile.layout  
                elif pathname =='/modules/services_profile':
                    returnlayout = services_profile.layout 
                elif pathname =='/modules/status_profile':
                    returnlayout = status_profile.layout  
                elif pathname =='/modules/suppliers_profile':
                    returnlayout = suppliers_profile.layout  
                elif pathname =='/modules/staff_report_profile':
                    returnlayout = staff_report_profile.layout 
                elif pathname =='/modules/material':
                    returnlayout = material.layout 
                elif pathname =='/modules/material_profile':
                    returnlayout = material_profile.layout 
                elif pathname =='/modules/occupation':
                    returnlayout = occupation.layout 
                elif pathname =='/modules/occupation_profile':
                    returnlayout = occupation_profile.layout
                else:
                    returnlayout = 'error404'
            logout_conditions = [
                pathname in ['/', '/logout'],
                userid == -1,
                not userid
            ]
            sessionlogout = any(logout_conditions)
            navbar_classname = 'd-none' if sessionlogout else ''
        else:
            raise PreventUpdate
	
        return [returnlayout, sessionlogout, navbar_classname]
    else:
        raise PreventUpdate


    
if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=False)

