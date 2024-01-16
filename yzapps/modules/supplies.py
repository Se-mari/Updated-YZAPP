# supplies
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
        html.H2('Supplies'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Supplies')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Supplies', color="secondary", href='/modules/purchase_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find supplies'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='supplies_filter',
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
                                    id='supplies_list'
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
    Output('supplies_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('supplies_filter', 'value'),
]
)
    
def material_loadlist(pathname, searchterm):
    if pathname == '/modules/supplies':
        sql = """
        select sales_invoice, material_name, suppliers_name, quantity, supply_id, po.purchase_id
        from supplies s
	        inner join purchase_order po on po.purchase_id=s.purchase_id
			inner join material ma on ma.material_id=s.material_id
			inner join suppliers sup on sup.suppliers_id=s.suppliers_id
	        where not supplies_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Sales Invoice', 'Material ordered',  'Name of Supplier', 'Quantity Ordered', 'ID', 'PO_ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND suppliers_name ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 
            buttons1 = []
            buttons2 = []
            for profile_id in df['ID']:
                buttons1 +=  [
                    html.Div(
                        dbc.Button('Edit Purchase Data',href=f'/modules/purchase_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            for purchase_id in df['ID']:
                buttons2 +=  [
                    html.Div(
                        dbc.Button('Edit Supply Data',href=f'/modules/supplies_profile?mode=edit&id={purchase_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action1'] = buttons1
            df['Action2'] = buttons2
            df= df[['Sales Invoice', 'Material ordered',  'Name of Supplier', 'Quantity Ordered', 'Action1', 'Action2']]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate