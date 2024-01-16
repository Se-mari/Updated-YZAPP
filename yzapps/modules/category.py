# categories
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
                        html.H3('Manage Category')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Category', color="secondary", href='/modules/category_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Category'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='category_filter',
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
                                    id='category_list'
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
    Output('category_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('category_filter', 'value'),
]
)
    
def category_loadlist(pathname, searchterm):
    if pathname == '/modules/category':
        sql = """
        select category_name, category_description, category_id
            from category
            where not category_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Name', 'Description',  'ID'] #make sure column number of data matches sql

        if searchterm:
            sql += "AND category_name ILIKE %s"

            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 

            buttons = []
            for profile_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/category_profile?mode=edit&id={profile_id}',
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