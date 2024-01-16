#transaction WIP
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app

from yzapps import dbconnect as db
from yzapps.modules import services_profile
layout = html.Div(
    [
        html.H2('Transaction'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Transaction')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Transactions', color="secondary", href='/modules/transaction_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find transaction'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='transaction_filter',
                                                        placeholder='Name'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                            className = 'mb-3'
                                        )
                                    )
                                ),
                                    html.Div(
                                    id='transaction_list'
                                )
                            ]
                        )   
                    ]
                )
            ]   
        )
    ]
)

@app.callback(
[
    Output('transaction_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('transaction_filter', 'value'),
]
)
    
def transaction_loadlist(pathname, searchterm):
    if pathname == '/modules/transaction':
        sql = """
        select concat (staff_fname,' ', staff_lname) ,concat (customer_fname,' ', customer_lname) , created_date, type_name, service_name, amount, status_name, transaction_id
            from transaction ta
             inner join staff st on st.staff_id=ta.staff_id
             inner join customer cu on cu.customer_id=ta.customer_id
             inner join payment_type pt on pt.type_id=ta.type_id
             inner join service se on se.service_id=ta.service_id
             inner join status s on s.status_id=ta.status_id
        where not transaction_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Staff Name', 'Customer Name', 'Date', 'Payment Type', 'Service Availed', 'Amount', 'Status', 'ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND concat (customer_fname,' ', customer_lname) ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 
            buttons1 = []
            buttons2 = []
            for profile_id in df['ID']:
                buttons1 +=  [
                    html.Div(
                        dbc.Button('Edit Transaction',href=f'/modules/transaction_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
                buttons2 +=  [
                    html.Div(
                        dbc.Button('Update Status',href=f'/modules/transaction_profile?mode=status&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action1'] = buttons1
            df['Action2'] = buttons2
            df= df[['Staff Name', 'Customer Name', 'Date', 'Payment Type', 'Service Availed', 'Amount', 'Status', 'Action1', 'Action2']]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate