# services
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
        html.H2('Service'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Service')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Service', color="secondary", href='/modules/services_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Service'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='service_filter',
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
                                    id='service_list'
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
    Output('service_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('service_filter', 'value'),
]
)
    
def service_loadlist(pathname, searchterm):
    if pathname == '/modules/services':
        sql = """
        select service_name, service_description, service_price, material_name, quantity, service_id
            from service s
			inner join material ma on s.material_id=ma.material_id
            where not service_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Name', 'Description', 'Price', 'Material Name', 'Material Quantity Used', 'ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND service_name ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 
            buttons = []
    
            for profile_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/services_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action'] =buttons
            df= df[['Name', 'Description', 'Price', 'Material Name', 'Material Quantity Used', "Action"]]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate