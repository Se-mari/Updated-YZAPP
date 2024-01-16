# Staff
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
        html.H2('Staff'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardHeader( 
                    [
                        html.H3('Manage Records of Staff')
                    ]
                ),
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Staff', color="secondary", href='/modules/staff_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div( 
                            [
                                html.H4('Find Staff'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='staff_filter',
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
                                    id='staff_list'
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
    Output('staff_list', 'children') 
],
[
    Input('url', 'pathname'),
    Input('staff_filter', 'value'),
]
)
    
def Staff_loadlist(pathname, searchterm):
    if pathname == '/modules/staff':
        sql = """ Select concat( staff_fname,' ',staff_lname) Name, role_name, staff_phone, staff_email, staff_id
        from staff s
		inner join staff_role r on s.role_id=r.role_id
		WHERE
        NOT staff_delete_ind
        """
        values = [] 
        cols = ['Name', 'Staff Role','Phone Number','Email', 'ID']
        if searchterm:
            sql += " AND concat( staff_fname,' ',staff_lname) ILIKE %s"
            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape:
            buttons = []
            for staff_id in df['ID']:
                buttons +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/staff_profile?mode=edit&id={staff_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ]
            df['Action'] =buttons
            df= df[['Name','Staff Role', 'Phone Number', 'Email', "Action"]]
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate