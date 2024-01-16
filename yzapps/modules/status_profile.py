# Usual Dash dependencies
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
from urllib.parse import urlparse, parse_qs

layout = html.Div(
    [
        html.Div([
            dcc.Store(id='status_profile_toload', storage_type='memory', data=0),
        ]),
        html.H2('Status Details'), 
        html.Hr(),
        dbc.Alert(id='status_profile_alert', is_open=False), 
        dbc.Form(
            [
            dbc.Row(
                [
                    dbc.Label("Name", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='status_profile_name', #id 1
                            placeholder="Name"
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Description", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='status_profile_description', #id 2
                            placeholder='Description'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            ]
        ),

        html.Div(
            dbc.Row(
                [
                    dbc.Label("Wish to delete?", width=1),
                    dbc.Col(
                        dbc.Checklist(
                            id='status_profile_removerecord', #id4
                            options=[
                                {
                                    'label': "Mark for Deletion",
                                    'value': 1
                                }
                            ],
                            style={'fontWeight':'bold'},
                        ),
                        width=5,
                    ),
                ],
                className="mb-3",
            ),
            id='status_profile_removerecord_div' # id5
        ),


        dbc.Button(
            'Submit',
            id='status_profile_submit', # id6
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'status_profile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/status', 
                    id= 'status_profile_btn_modal'
                )
            )
        ],
        centered=True,
        id='status_profile_successmodal',
        backdrop='static' 
    )
])
@app.callback(
[

    Output('status_profile_toload', 'data'),
    Output('status_profile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def generate_profile (pathname, search):
    if pathname == '/modules/status_profile':
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None

        return [to_load, removediv_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('status_profile_alert', 'color'),
        Output('status_profile_alert', 'children'),
        Output('status_profile_alert', 'is_open'),
        Output('status_profile_successmodal', 'is_open'),
        Output('status_profile_feedback_message', 'children'),
        Output('status_profile_btn_modal', 'href')

    ],
    [
        Input('status_profile_submit', 'n_clicks'),
        Input('status_profile_btn_modal', 'n_clicks'),

    ],
[
State('status_profile_name', 'value'),
State('status_profile_description', 'value'),
State('url', 'search'),
State('status_profile_removerecord', 'value'),
]
)
def statusprofile_saveprofile(submitbtn, closebtn, name, description, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'status_profile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not name  : 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the Status name.'
            elif not description  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the description.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into status (status_name, status_description, status_delete_ind)
                    VALUES (%s, %s, %s)
                    '''
                    values = [name, description, False]
                    db.modifydatabase(sql, values)
                    feedbackmessage= "Status detail has been saved"
                    okay_href='/modules/status'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    profileid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    UPDATE status SET status_name = %s, status_description= %s, status_delete_ind = %s
                    WHERE status_id = %s
                    """
                    to_delete = bool(removerecord)
                    values = [name, description ,to_delete, profileid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Status details has been updated."
                    okay_href = '/modules/status'
                    modal_open = True
                    
                else:
                    raise PreventUpdate

            return [alert_color, alert_text, alert_open, modal_open, feedbackmessage, okay_href]
        else: 
            
            raise PreventUpdate
    else:
        raise PreventUpdate

@app.callback(
[
    Output('status_profile_name', 'value'),
    Output('status_profile_description', 'value'),
],
[
    Input('status_profile_toload', 'modified_timestamp')
],
[
    State('status_profile_toload', 'data'),
    State('url', 'search'),
]
)
def profile_loadprofile(timestamp, toload, search):
    if toload: 
        parsed = urlparse(search)
        profileid = parse_qs(parsed.query)['id'][0]
        sql = """
        Select status_name, status_description
        from status
		where status_id=%s
        """
        values = [profileid]
        col = ['name', 'description']
        df = db.querydatafromdatabase(sql, values, col)
        name = df['name'][0]
        description = df['description'][0]
        return [name, description]
    else:
        raise PreventUpdate

