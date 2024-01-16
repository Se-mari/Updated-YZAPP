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
            dcc.Store(id='purchaseprofile_toload', storage_type='memory', data=0),
        ]),
        html.H2('Purchase'), # Page Header
        html.Hr(),
        dbc.Alert(id='purchaseprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
            dbc.Row(
                [
                dbc.Label("Staff", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='purchaseprofile_staff', #id 2
                            placeholder='Staff'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Sales Invoice Number", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='purchaseprofile_invoice', #id 2
                            placeholder='Sales Invoice Number'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Payment Method", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='purchaseprofile_type', #id 2
                            placeholder='Payment Method'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Payment Amount", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='number',
                            id='purchaseprofile_amount', #id 2
                            placeholder='Payment Amount'
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
                            id='purchaseprofile_removerecord',
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
            id='purchaseprofile_removerecord_div'
        ),


        dbc.Button(
            'Proceed to next page',
            id='purchaseprofile_submit',
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'purchaseprofile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed to supply input",
                    href='/modules/supplies_profile', 
                    id= 'purchaseprofile_btn_modal'
                )
            )
        ],
        centered=True,
        id='purchaseprofile_successmodal',
        backdrop='static' 
    )
])

@app.callback(
[
    Output('purchaseprofile_staff', 'options'),
    Output('purchaseprofile_type', 'options'),
    Output('purchaseprofile_toload', 'data'),
    Output('purchaseprofile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def purchaseprofile_populate(pathname, search):
    if pathname == '/modules/purchase_profile':
        sql = """
        SELECT concat(staff_fname,' ',staff_lname ) as label, staff_id as value
        FROM staff
        WHERE staff_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options1 = df.to_dict('records')

        sql = """
        select type_name as label, type_id as value
        from payment_type
        where type_delete_ind = false
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options2 = df.to_dict('records')
        
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None

        return [options1, options2, to_load, removediv_style]
    else:
        raise PreventUpdate
    
@app.callback(
    [
        Output('purchaseprofile_alert', 'color'),
        Output('purchaseprofile_alert', 'children'),
        Output('purchaseprofile_alert', 'is_open'),
        Output('purchaseprofile_successmodal', 'is_open'),
        Output('purchaseprofile_feedback_message', 'children'),
        Output('purchaseprofile_btn_modal', 'href')

    ],
    [
        Input('purchaseprofile_submit', 'n_clicks'),
        Input('purchaseprofile_btn_modal', 'n_clicks'),

    ],
[
State('purchaseprofile_staff', 'value'),
State('purchaseprofile_invoice', 'value'),
State('purchaseprofile_type', 'value'),
State('purchaseprofile_amount', 'value'),
State('url', 'search'),
State('purchaseprofile_removerecord', 'value'),
]
)
def purchaseprofile_saveprofile(submitbtn, closebtn, staff, invoice, type, amount, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'purchaseprofile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not staff: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put staff.'
            elif not invoice: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put invoice.'
            elif not type: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put payment type.'
            elif not amount: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put purchase amount.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into purchase_order (staff_id, sales_invoice, type_id, purchase_order_date, amount, purchase_order_delete_ind)
                    values(%s, %s, %s, current_timestamp, %s, %s)
                    '''
                    values = [staff, invoice, type, amount, False]
                    db.modifydatabase(sql, values)

                    feedbackmessage= "Purchase data has been saved"
                    okay_href='/modules/supplies_profile?mode=add'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    purchaseid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    update purchase_order SET staff_id=%s, sales_invoice=%s, type_id=%s, amount=%s, purchase_order_delete_ind=%s
                    where purchase_id=%s
                    """
                    to_delete = bool(removerecord)
                    values = [staff, invoice, type, amount, to_delete, purchaseid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Purchase data has been updated."
                    okay_href = '/modules/supplies'
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
    Output('purchaseprofile_staff', 'value'),
    Output('purchaseprofile_invoice', 'value'),
    Output('purchaseprofile_type', 'value'),
    Output('purchaseprofile_amount', 'value'),
],
[
    Input('purchaseprofile_toload', 'modified_timestamp')
],
[
    State('purchaseprofile_toload', 'data'),
    State('url', 'search'),
]
)
def purchaseprofile_loadprofile(timestamp, toload, search):
    if toload: # check if toload = 1
        # Get movieid value from the search parameters
        parsed = urlparse(search)
        purchaseid = parse_qs(parsed.query)['id'][0]
        # Query from db
        sql = """
        select staff_id, sales_invoice, type_id, amount
        from purchase_order
        where purchase_id=%s
        """
        values = [purchaseid]
        col = ['staff', 'invoice', 'type', 'amount']
        df = db.querydatafromdatabase(sql, values, col)
        invoice = int(df['invoice'][0])
        type = int(df['type'][0])
        staff = int(df['staff'][0])
        amount = int(df['amount'][0])
        return [staff, invoice, type, amount]
    else:
        raise PreventUpdate

