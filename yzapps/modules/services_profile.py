# service profile
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
            dcc.Store(id='service_profile_toload', storage_type='memory', data=0),
        ]),
        html.H2('Service Details'), 
        html.Hr(),
        dbc.Alert(id='service_profile_alert', is_open=False), 
        dbc.Form(
            [
            dbc.Row(
                [
                    dbc.Label("Name", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='service_profile_name', #id 1
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
                            id='service_profile_description', #id 2
                            placeholder='Description'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Service Price", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='number',
                            id='service_profile_price', #id 2
                            placeholder='Price'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Material Used", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='service_profile_material', #id 2
                            placeholder='Material'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Material Quantity", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='number',
                            id='service_profile_quantity', #id 2
                            placeholder='Quantity'
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
                            id='service_profile_removerecord', #id4
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
            id='service_profile_removerecord_div' # id5
        ),


        dbc.Button(
            'Submit',
            id='service_profile_submit', # id6
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'service_profile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/services', 
                    id= 'service_profile_btn_modal'
                )
            )
        ],
        centered=True,
        id='service_profile_successmodal',
        backdrop='static'
    )
])
@app.callback(
[
    Output('service_profile_material', 'options'),
    Output('service_profile_toload', 'data'),
    Output('service_profile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def serviceprofile_populate(pathname, search):
    if pathname == '/modules/services_profile':
        sql = """
        SELECT material_name as label, material_id as value
        FROM material
        WHERE material_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options = df.to_dict('records')

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' or "material" else 0
        removediv_style = {'display': 'none'} if not to_load else None

        return [options, to_load, removediv_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('service_profile_alert', 'color'),
        Output('service_profile_alert', 'children'),
        Output('service_profile_alert', 'is_open'),
        Output('service_profile_successmodal', 'is_open'),
        Output('service_profile_feedback_message', 'children'),
        Output('service_profile_btn_modal', 'href')

    ],
    [
        Input('service_profile_submit', 'n_clicks'),
        Input('service_profile_btn_modal', 'n_clicks'),

    ],
[
State('service_profile_name', 'value'),
State('service_profile_description', 'value'),
State('service_profile_price', 'value'),
State('service_profile_material', 'value'),
State('service_profile_quantity', 'value'),
State('url', 'search'),
State('service_profile_removerecord', 'value'),
]
)
def profile_saveprofile(submitbtn, closebtn, name, description, price, material, quantity, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'service_profile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not name  : 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the service name.'
            elif not description  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the description.'
            elif not price  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the price.'
            elif not material  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the material used.'
            elif not quantity  :
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the quantity of materials used.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into service (service_name, service_description, service_price, material_id, quantity, service_delete_ind)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    '''
                    values = [name, description, price, material, quantity, False]
                    db.modifydatabase(sql, values)
                    
                    okay_href='/modules/services'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    profileid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    UPDATE service SET service_name = %s, service_description= %s, service_price=%s, material_id=%s, quantity=%s, service_delete_ind = %s
                    WHERE service_id = %s
                    """
                    to_delete = bool(removerecord)
                    values = [name, description, price, material, quantity ,to_delete, profileid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Service details has been updated."
                    okay_href = '/modules/services'
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
    Output('service_profile_name', 'value'),
    Output('service_profile_description', 'value'),
    Output('service_profile_price', 'value'),
    Output('service_profile_material', 'value'),
    Output('service_profile_quantity', 'value'),
],
[
    Input('service_profile_toload', 'modified_timestamp')
],
[
    State('service_profile_toload', 'data'),
    State('url', 'search'),
]
)
def profile_loadprofile(timestamp, toload, search):
    if toload:
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        if create_mode == 'edit':
            parsed = urlparse(search)
            profileid = parse_qs(parsed.query)['id'][0]
            sql = """
            Select service_name, service_description, service_price, material_id, quantity
            from service
            where service_id=%s
            """
            values = [profileid]
            col = ['name', 'description', 'price', 'material', 'quantity']
            df = db.querydatafromdatabase(sql, values, col)
            name = df['name'][0]
            description = df['description'][0]
            price = int(df['price'][0])
            material = int(df['material'][0])
            quantity = int(df['quantity'][0])
            return [name, description, price, material, quantity]
    else:
        raise PreventUpdate
