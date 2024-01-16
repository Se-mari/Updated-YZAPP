#Customers profile
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
        html.Div( 
                            [
                                dbc.Button('Add Occupation', color="secondary", href='/modules/occupation_profile?mode=add'),
                            ]
                        ),
        html.Div([
            dcc.Store(id='customer_profile_toload', storage_type='memory', data=0),
        ]),
        html.H2('Customer Details'), 
        html.Hr(),
        dbc.Alert(id='customer_profile_alert', is_open=False), 
        dbc.Form(
            [
            dbc.Row(
                [
                    dbc.Label("First Name", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='customer_profile_fname', #id 1
                            placeholder="First Name"
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Last Name", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='customer_profile_lname', #id 2
                            placeholder='Last Name'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Occupation", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='customer_profile_occupation', #id 2
                            placeholder='Occupation'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Phone Number", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='customer_profile_phone', #id 2
                            placeholder='Phone Number'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Eamil", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='customer_profile_email', #id 2
                            placeholder='Email'
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
                            id='customer_profile_removerecord', #id4
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
            id='customer_profile_removerecord_div' # id5
        ),


        dbc.Button(
            'Submit',
            id='customer_profile_submit', # id6
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'customer_profile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/customers', 
                    id= 'customer_profile_btn_modal'
                )
            )
        ],
        centered=True,
        id='customer_profile_successmodal',
        backdrop='static'
    )
])
@app.callback(
[
    Output('customer_profile_occupation', 'options'),
    Output('customer_profile_toload', 'data'),
    Output('customer_profile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def serviceprofile_populate(pathname, search):
    if pathname == '/modules/customers_profile':
        sql = """
        SELECT occupation_name as label, occupation_id as value
        FROM occupation
        WHERE occupation_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options = df.to_dict('records')

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None

        return [options, to_load, removediv_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('customer_profile_alert', 'color'),
        Output('customer_profile_alert', 'children'),
        Output('customer_profile_alert', 'is_open'),
        Output('customer_profile_successmodal', 'is_open'),
        Output('customer_profile_feedback_message', 'children'),
        Output('customer_profile_btn_modal', 'href')

    ],
    [
        Input('customer_profile_submit', 'n_clicks'),
        Input('customer_profile_btn_modal', 'n_clicks'),

    ],
[
State('customer_profile_fname', 'value'),
State('customer_profile_lname', 'value'),
State('customer_profile_occupation', 'value'),
State('customer_profile_phone', 'value'),
State('customer_profile_email', 'value'),
State('url', 'search'),
State('customer_profile_removerecord', 'value'),
]
)
def profile_saveprofile(submitbtn, closebtn, fname, lname, occupation, phone, email, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'customer_profile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not fname  : 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the first name.'
            elif not lname  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the last name.'
            elif not occupation  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input customer occupation.'
            elif not phone :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input phone number.'
            elif not email  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the email of customer.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into customer (customer_fname, customer_lname, occupation_id, customer_phone, customer_email, customer_delete_ind)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    '''
                    values = [fname, lname, occupation, phone, email, False]
                    db.modifydatabase(sql, values)
                    feedbackmessage= "Customer detail has been saved"
                    okay_href='/modules/customers'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    profileid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    UPDATE customer SET customer_fname = %s, customer_lname= %s, occupation_id=%s, customer_phone=%s, customer_email=%s, customer_delete_ind = %s
                    WHERE customer_id = %s
                    """
                    to_delete = bool(removerecord)
                    values = [fname, lname, occupation, phone, email ,to_delete, profileid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Customer details has been updated."
                    okay_href = '/modules/customers'
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
    Output('customer_profile_fname', 'value'),
    Output('customer_profile_lname', 'value'),
    Output('customer_profile_occupation', 'value'),
    Output('customer_profile_phone', 'value'),
    Output('customer_profile_email', 'value'),
],
[
    Input('customer_profile_toload', 'modified_timestamp')
],
[
    State('customer_profile_toload', 'data'),
    State('url', 'search'),
]
)
def profile_loadprofile(timestamp, toload, search):
    if toload:
        parsed = urlparse(search)
        profileid = parse_qs(parsed.query)['id'][0]
        sql = """
        select customer_fname, customer_lname, occupation_id, customer_phone, customer_email
        from customer
            where customer_id = %s
        """
        values = [profileid]
        col = ['fname', 'lname', 'occupation', 'phone', 'email']
        df = db.querydatafromdatabase(sql, values, col)
        fname = df['fname'][0]
        lname = df['lname'][0]
        occupation = int(df['occupation'][0])
        phone = df['phone'][0]
        email = df['email'][0]
        return [fname, lname, occupation, phone, email]
    
    else:
        raise PreventUpdate

