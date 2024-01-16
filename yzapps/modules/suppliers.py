# suppliers
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
from yzapps.modules import staff_profile



layout = html.Div(
    [
        html.H2('Categories'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Supplier Records')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Suppliers', color="secondary", href='/modules/suppliers_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Supplier'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Suppliers", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='suppliers_filter',
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
                                    id='suppliers_list'
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
    Output('suppliers_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('suppliers_filter', 'value'),
]
)
    
def suppliers_loadlist(pathname, searchterm):
    if pathname == '/modules/suppliers':
        sql = """
        select suppliers_name, suppliers_phone, suppliers_email, concat( suppliers_province,', ', suppliers_city,', ', suppliers_street,', ', suppliers_number) Address, suppliers_id
        from suppliers
        where not suppliers_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Name', 'Phone', 'Email',' Adress', 'ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND suppliers_name ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 
            buttons = []
            for profile_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/suppliers_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action'] =buttons
            df= df[['Name', 'Phone', 'Email',' Adress', "Action"]]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate