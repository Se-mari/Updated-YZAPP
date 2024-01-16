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
            dcc.Store(id='users_profile_toload', storage_type='memory', data=0),
        ]),
        html.H2('User Details'), 
        html.Hr(),
        dbc.Alert(id='users_profile_alert', is_open=False), 
        dbc.Form(
            [
            dbc.Row(
                [
                    dbc.Label("Name", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='users_profile_name', #id 1
                            placeholder="Name"
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),

            dbc.Row(
                [
                    dbc.Label("Staff Name", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='users_profile_staffid', #id 2
                            placeholder='Staff'
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
                            id='users_profile_removerecord', #id4
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
            id='users_profile_removerecord_div' # id5
        ),


        dbc.Button(
            'Submit',
            id='users_profile_submit', # id6
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'users_profile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/users', 
                    id= 'users_profile_btn_modal'
                )
            )
        ],
        centered=True,
        id='users_profile_successmodal',
        backdrop='static' 
    )
])
@app.callback(
[
    Output('users_profile_staffid', 'options'),
    Output('users_profile_toload', 'data'),
    Output('users_profile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def users_profile(pathname, search):
    if pathname == '/modules/users_profile':
        sql = """
        SELECT concat(staff_fname,' ',staff_lname ) as label, staff_id as value
        FROM staff
        WHERE staff_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        staff_options = df.to_dict('records')

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None

        return [ staff_options,to_load, removediv_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('users_profile_alert', 'color'),
        Output('users_profile_alert', 'children'),
        Output('users_profile_alert', 'is_open'),
        Output('users_profile_successmodal', 'is_open'),
        Output('users_profile_feedback_message', 'children'),
        Output('users_profile_btn_modal', 'href')

    ],
    [
        Input('users_profile_submit', 'n_clicks'),
        Input('users_profile_btn_modal', 'n_clicks'),

    ],
[
State('users_profile_name', 'value'),
State('users_profile_staffid', 'value'),
State('url', 'search'),
State('users_profile_removerecord', 'value'),
]
)
def profile_saveprofile(submitbtn, closebtn, name, staffid, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'users_profile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''

            if not name  : 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put username.'
            elif not staffid :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put staff. If name not in list please add name to staff list first.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0] 
                if create_mode == 'edit':
                    parsed = urlparse(search)
                    usersid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    update users
                    set 
                    user_name=%s,
                    staff_id=%s,
                    user_delete_ind= %s
                    where user_id= %s
                    """
                    to_delete = bool(removerecord)
                    values = [name, staffid, to_delete, usersid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Users details has been updated."
                    okay_href = '/modules/users'
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
    Output('users_profile_name', 'value'),
    Output('users_profile_staffid', 'value'),
],
[
    Input('users_profile_toload', 'modified_timestamp'),
],
[
    State('users_profile_toload', 'data'),
    State('url', 'search'),
]
)
def users_profile_loadprofile(timestamp, toload, search):
    if toload:
        parsed = urlparse(search)
        userid = parse_qs(parsed.query)['id'][0]
        sql = """
        Select user_name, staff_id
        from users
        where user_id=%s
        """
        values = [userid]
        col = ['name',  'staffid']
        df = db.querydatafromdatabase(sql, values, col)
        name = df['name'][0]
        if not df['staffid'][0]:
            sql = """
            Select user_name
            from users
            where user_id=%s
            """
            values = [userid]
            col = ['name']
            df = db.querydatafromdatabase(sql, values, col)
            name = df['name'][0]
            return [name,'']
        else:
            staffid= int(df['staffid'][0])
            return [name, staffid]
    else:
        raise PreventUpdate

