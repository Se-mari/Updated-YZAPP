# Users
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
        html.H2('Users'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Records of Users')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div(
                            [
                                dbc.Button('Add User', color="secondary", href='/signup'),
                            ]
                            
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H5('Please make sure that each user account has an attached staff name')
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find users'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='users_filter_name',
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
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Staff", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='users_filter_staff',
                                                        placeholder='Staff'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                            className = 'mb-3'
                                        )
                                    )
                                ),
                                    html.Div(
                                    id='users_list'
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
    Output('users_list', 'children') #make sure outputs have unique names
],
[
    Input('url', 'pathname'),
    Input('users_filter_name', 'value'),
    Input('users_filter_staff', 'value'),
]
)
    
def Staff_loadlist(pathname, searchname, searchstaff):
    if pathname == '/modules/users':
        sql = """ Select user_name, concat (staff_fname,' ', staff_lname) Name, user_id
        from users u
        LEFT JOIN staff s ON u.staff_id=s.staff_id
        WHERE
        NOT user_delete_ind
        """
        #include not delete or else search will not work
        values = [] 
        cols = ['Name', 'Staff Name', 'ID'] #make sure column number of data matches sql

        if searchname:
            sql += "AND user_name ILIKE %s"

            values += [f"%{searchname}%"]
        df = db.querydatafromdatabase(sql, values, cols)

        if searchstaff:
            sql += "AND concat(staff_fname, staff_lname) ILIKE %s"

            values += [f"%{searchstaff}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape: 

            buttons = []
            for profile_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/users_profile?mode=edit&id={profile_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action'] =buttons
            df= df[['Name', 'Staff Name',"Action"]]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate