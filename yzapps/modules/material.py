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
        html.H2('Materials'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Materials')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Materials', color="secondary", href='/modules/material_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find materials'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='material_filter',
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
                                    id='material_list'
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
    Output('material_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('material_filter', 'value'),
]
)
    
def material_loadlist(pathname, searchterm):
    if pathname == '/modules/material':
        sql = """
        select material_name, category_name, in_stock, unit_price, reorder_point, material_id
        from material ma
	        inner join category ca on ma.category_id=ca.category_id
	        where not material_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Name', 'Category',  'Number in Stock', 'Price per unit', 'Reorder point', 'ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND material_name ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 

            buttons = []
            for profile_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/material_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action'] =buttons
            df= df[['Name', 'Category',  'Number in Stock', 'Price per unit', 'Reorder point', 'Action']]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate