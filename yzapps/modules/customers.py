# material
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
        html.H2('Customers'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Customer')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Customer Data', color="secondary", href='/modules/customers_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find customer'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='customer_filter',
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
                                    id='customer_list'
                                )
                            ]
                        )   
                    ]
                )
            ]   
        )
    ],

)

@app.callback(
[
    Output('customer_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('customer_filter', 'value'),
]
)
    
def customer_loadlist(pathname, searchterm):
    if pathname == '/modules/customers':
        sql = """
        select concat (customer_fname, ' ', customer_lname ) name, occupation_name, customer_phone, customer_email, customer_id
            from customer cu
	        inner join occupation oc on oc.occupation_id=cu.occupation_id
	    where not customer_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Name', 'Occupation',  'Phone', 'Email', 'ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND concat (customer_fname, ' ', customer_lname ) ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 
            buttons = []
            for profile_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/customers_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action'] =buttons
            df= df[['Name', 'Occupation',  'Phone', 'Email', 'Action']]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate