# occupation
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
        html.H2('Occupation'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Occupation')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Occupation', color="secondary", href='/modules/occupation_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Occupation'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='occupation_filter',
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
                                    id='occupation_list'
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
    Output('occupation_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('occupation_filter', 'value'),
]
)
    
def occupation_loadlist(pathname, searchterm):
    if pathname == '/modules/occupation':
        sql = """
        select occupation_name, occupation_description, occupation_id
            from occupation
            where not occupation_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Name', 'Description',  'ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND occupation_name ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 

            buttons = []
            for profile_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/occupation_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action'] =buttons
            df= df[['Name', 'Description', "Action"]]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate