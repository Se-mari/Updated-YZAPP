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
            dcc.Store(id='supplier_toload', storage_type='memory', data=0),
        ]),
        html.H2('Supplier Details'), 
        html.Hr(),
        dbc.Alert(id='supplier_alert', is_open=False), 
        dbc.Form(
            [
            dbc.Row(
                [
                    dbc.Label("Supplier Name", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='supplier_name', #id 1
                            placeholder="Supplier Name"
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Supplier Phone Number", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='supplier_phonenumber', #id 1.1
                            placeholder="Phone Number"
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Email", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='supplier_email', #id 2
                            placeholder='Email'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Province", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='supplier_province', #id3
                            placeholder='Province',
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("City", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='supplier_city', #id4
                            placeholder='City',
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Street", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='supplier_street', #id5
                            placeholder='Street',
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Building Number", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='supplier_number', #id6
                            placeholder='Building Number',
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
                            id='supplier_removerecord', #id4
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
            id='supplier_removerecord_div' # id5
        ),


        dbc.Button(
            'Submit',
            id='supplier_submit', # id6
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'supplier_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/suppliers', 
                    id= 'supplier_btn_modal'
                )
            )
        ],
        centered=True,
        id='supplier_successmodal',
        backdrop='static' 
    )
])
@app.callback(
[
    Output('supplier_toload', 'data'),
    Output('supplier_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def profile_load(pathname, search):
    if pathname == '/modules/suppliers_profile':
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None
        return [to_load, removediv_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('supplier_alert', 'color'),
        Output('supplier_alert', 'children'),
        Output('supplier_alert', 'is_open'),
        Output('supplier_successmodal', 'is_open'),
        Output('supplier_feedback_message', 'children'),
        Output('supplier_btn_modal', 'href')

    ],
    [
        Input('supplier_submit', 'n_clicks'),
        Input('supplier_btn_modal', 'n_clicks'),

    ],
    [
        State('supplier_name', 'value'),
        State('supplier_phonenumber', 'value'),
        State('supplier_email', 'value'),
        State('supplier_province', 'value'),
        State('supplier_city', 'value'),
        State('supplier_street', 'value'),
        State('supplier_number', 'value'),
        State('url', 'search'),
        State('supplier_removerecord', 'value'),
    ]
)
def profile_saveprofile(submitbtn, closebtn, name, phonenumber, email, province, 
                             city, street, number, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'supplier_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not name  : 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please insert supplier name.'
            elif not phonenumber  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the phone number.'
            elif not email :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the email.'
            elif not province :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input your province.'
            elif not city :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input city.'
            elif not street :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the street.'
            elif not number :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the building number.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into suppliers (suppliers_name, suppliers_phone, suppliers_email, 
                    suppliers_province, suppliers_city, suppliers_street, suppliers_number, suppliers_delete_ind)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    values = [name, phonenumber, email, province, city, street, number, False]
                    db.modifydatabase(sql, values)
                    feedbackmessage= "Suppliers detail has been saved"
                    okay_href='/modules/suppliers'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    supplierid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    UPDATE suppliers SET suppliers_name =%s , suppliers_phone =%s, suppliers_email =%s, 
                    suppliers_province =%s, suppliers_city =%s, suppliers_street =%s, suppliers_number =%s, suppliers_delete_ind =%s
                    WHERE suppliers_id = %s
                    """
                    to_delete = bool(removerecord)
                    values = [name, phonenumber, email, province, city, street, number ,to_delete, supplierid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Suppliers details has been updated."
                    okay_href = '/modules/suppliers'
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
    Output('supplier_name', 'value'),
    Output('supplier_phonenumber', 'value'),
    Output('supplier_email', 'value'),
    Output('supplier_province', 'value'),
    Output('supplier_city', 'value'),
    Output('supplier_street', 'value'),
    Output('supplier_number', 'value'),
],
[
    Input('supplier_toload', 'modified_timestamp')
],
[
    State('supplier_toload', 'data'),
    State('url', 'search'),
]
)
def profile_loadprofile(timestamp, toload, search):
    if toload:
        parsed = urlparse(search)
        supplierid = parse_qs(parsed.query)['id'][0]
        sql = """
        select suppliers_name, suppliers_phone, suppliers_email, 
        suppliers_province, suppliers_city, suppliers_street, suppliers_number
        from suppliers
		where suppliers_id = %s
        """
        values = [supplierid]
        col = ['name', 'phonenumber', 'email', 'province', 'city', 'street', 'number']
        df = db.querydatafromdatabase(sql, values, col)
        name = df['name'][0]
        phonenumber = df['phonenumber'][0]
        email = df['email'][0]
        province = df['province'][0]
        city = df['city'][0]
        street = df['street'][0]
        number = df['number'][0]
        return [name, phonenumber, email, province, city, street, number]
    else:
        raise PreventUpdate

