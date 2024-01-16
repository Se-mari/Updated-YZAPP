# Staff_report
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
        html.H2('Staff Report'), 
        html.Hr(),
        dbc.Card( 
            [
                dbc.CardBody( 
                [   
                        html.Div( 
                            [
                                dbc.Button('Add Staff', color="secondary", href='/modules/staff_report_profile?mode=add'),
                            ]
                        ),
                        html.Hr(),
                        html.Div( 
                            [
                                html.H4('Find Staff Report'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='report_filter',
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
                                    id='report_list'
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
    Output('report_list', 'children') 
],
[
    Input('url', 'pathname'),
    Input('report_filter', 'value'),
]
)
    
def Staff_loadlist(pathname, searchterm):
    if pathname == '/modules/staff_report':
        sql = """ select concat( staff_fname,' ',staff_lname) Name, report_date, report_id 
        from staff s
		inner join staff_report r on s.staff_id=r.staff_id
		WHERE
        NOT report_delete_ind
        """
        values = [] 
        cols = ['Name','Date','ID']
        if searchterm:
            sql += " AND concat( staff_fname,' ',staff_lname) ILIKE %s"
            values += [f"%{searchterm}%"]
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape:
            buttons1 = []
            buttons2=[]
            for report_id in df['ID']:
                buttons1 +=  [
                    html.Div(
                        dbc.Button('Edit',href=f'/modules/staff_report_profile?mode=edit&id={report_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ],
                buttons2 +=  [
                    html.Div(
                        dbc.Button('View',href=f'/modules/staff_report_profile?mode=view&id={report_id}',
                                   size='sm', color='warning'),
                                   style={'text-align': 'center'}
                    )
                ],
            df['Action'] =buttons1
            df['View'] =buttons2
            df= df[['Name','Date', "Action", "View"]]
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
            hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate