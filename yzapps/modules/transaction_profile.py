#wip
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

CONTENT_STYLE = {
    "margin-left": "10rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "overflow": "scroll"
}

layout = html.Div(
    [
        html.Div([
            dcc.Store(id='transactionprofile_toload', storage_type='memory', data=0),
        ]),
        html.H2('transaction'), # Page Header
        html.Hr(),
        dbc.Alert(id='transactionprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
            dbc.Row(
                [
                dbc.Label("Staff", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='transactionprofile_staff', #id 2
                            placeholder='Staff'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Customer Name", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='transactionprofile_customer', #id 2
                            placeholder='Customer Name'
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
                            id='transactionprofile_type', #id 2
                            placeholder='Payment Method'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Service Availed", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='transactionprofile_service', #id 2
                            placeholder='Service Type'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Quantity", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='number',
                            id='transactionprofile_quantity', #id 2
                            placeholder='Quantity of service availed'
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
                dbc.Label("Status", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='transactionprofile_status', #id 2
                            placeholder='Status'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            id='transactionprofile_status_div'
        ),

        html.Div(
            dbc.Row(
                [
                    dbc.Label("Wish to delete?", width=1),
                    dbc.Col(
                        dbc.Checklist(
                            id='transactionprofile_removerecord',
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
            id='transactionprofile_removerecord_div'
        ),


        dbc.Button(
            'Submit',
            id='transactionprofile_submit',
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'transactionprofile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/transaction', 
                    id= 'transactionprofile_btn_modal'
                )
            )
        ],
        centered=True,
        id='transactionprofile_successmodal',
        backdrop='static' 
    )
],
style=CONTENT_STYLE
)

@app.callback(
[
    Output('transactionprofile_staff', 'options'),
    Output('transactionprofile_customer', 'options'),
    Output('transactionprofile_type', 'options'),
    Output('transactionprofile_service', 'options'),
    Output('transactionprofile_status', 'options'),
    Output('transactionprofile_toload', 'data'),
    Output('transactionprofile_removerecord_div', 'style'),
    Output('transactionprofile_status_div', 'style')
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def purchaseprofile_populate(pathname, search):
    if pathname == '/modules/transaction_profile':
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
        select concat (customer_fname,' ', customer_lname) as label, customer_id as value
        from customer
        where customer_delete_ind = false
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options2 = df.to_dict('records')

        sql = """
        select type_name as label, type_id as value
        from payment_type
        where type_delete_ind = false
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options3 = df.to_dict('records')

        sql = """
        select service_name as label, service_id as value
        from service
        where service_delete_ind = false
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options4 = df.to_dict('records')

        sql = """
        select status_name as label, status_id as value
        from status
        where status_delete_ind = false
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options5 = df.to_dict('records')
        
        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' or 'status' else 0
        removediv_style = {'display': 'none'} if not to_load else None
        statusdiv_style= {'display': 'none'} if not create_mode== 'status' else None

        return [options1, options2, options3, options4, options5, to_load, removediv_style, statusdiv_style]
    else:
        raise PreventUpdate
    
@app.callback(
    [
        Output('transactionprofile_alert', 'color'),
        Output('transactionprofile_alert', 'children'),
        Output('transactionprofile_alert', 'is_open'),
        Output('transactionprofile_successmodal', 'is_open'),
        Output('transactionprofile_feedback_message', 'children'),
        Output('transactionprofile_btn_modal', 'href')

    ],
    [
        Input('transactionprofile_submit', 'n_clicks'),
        Input('transactionprofile_btn_modal', 'n_clicks'),

    ],
[
State('transactionprofile_staff', 'value'),
State('transactionprofile_customer', 'value'),
State('transactionprofile_type', 'value'),
State('transactionprofile_service', 'value'),
State('transactionprofile_quantity', 'value'),
State('transactionprofile_status', 'value'),
State('url', 'search'),
State('transactionprofile_removerecord', 'value'),
]
)
def transactionprofile_saveprofile(submitbtn, closebtn, staff, customer, type, service, quantity, status, search, removerecord):
    ctx = dash.callback_context  
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'transactionprofile_submit' and submitbtn:
            parsed = urlparse(search)
            create_mode = parse_qs(parsed.query)['mode'][0]
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
            elif not customer: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put customer name.'
            elif not type: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put payment type.'
            elif not service: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put service received.'
            elif not quantity: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put service quantity.'
            elif create_mode=='status' and not status:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put the status.'
            else: 
                if create_mode == 'add':
                    sql = '''
                    insert into transaction ( staff_id, customer_id, created_date, type_id, service_id, quantity, status_id, transaction_delete_ind)
                    values(%s, %s, current_timestamp, %s, %s, %s, '3', %s);

                    update transaction ta
                    set amount=s.service_price*ta.quantity
                    from service s
                    Where ta.service_id=s.service_id;
                    '''
                    values = [staff, customer, type, service, quantity, False]
                    db.modifydatabase(sql, values)
                    feedbackmessage= "Transaction data has been saved"
                    okay_href='/modules/transaction'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    transactionid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    update transaction SET staff_id=%s, customer_id=%s, type_id=%s, service_id=%s, quantity=%s, transaction_delete_ind=%s
                    where transaction_id=%s
                    """
                    to_delete = bool(removerecord)
                    values = [staff, customer, type, service, quantity, to_delete, transactionid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Transaction data has been updated."
                    okay_href = '/modules/transaction'
                    modal_open = True
                  
                elif create_mode == 'status':
                    parsed = urlparse(search)
                    transactionid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    update transaction SET  last_modified=current_timestamp, status_id=%s
                    where transaction_id=%s
                    """
                    values = [status, transactionid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Status has been updated data has been updated."
                    okay_href = '/modules/transaction'
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
    Output('transactionprofile_staff', 'value'),
    Output('transactionprofile_customer', 'value'),
    Output('transactionprofile_type', 'value'),
    Output('transactionprofile_service', 'value'),
    Output('transactionprofile_quantity', 'value'),
    Output('transactionprofile_status', 'value')
],
[
    Input('transactionprofile_toload', 'modified_timestamp')
],
[
    State('transactionprofile_toload', 'data'),
    State('url', 'search'),
]
)
def transactionprofile_loadprofile(timestamp, toload, search):
    if toload: # check if toload = 1
        # Get movieid value from the search parameters
        parsed = urlparse(search)
        purchaseid = parse_qs(parsed.query)['id'][0]
        # Query from db
        sql = """
        select staff_id, customer_id, type_id, service_id, quantity, status_id
        from transaction
        where transaction_id=%s
        """
        values = [purchaseid]
        col = ['staff', 'customer', 'type', 'service', 'quantity', 'status']
        df = db.querydatafromdatabase(sql, values, col)
        customer = int(df['customer'][0])
        type = int(df['type'][0])
        staff = int(df['staff'][0])
        service = int(df['service'][0])
        quantity = int(df['quantity'][0])
        status = int(df['status'][0])
        return [staff, customer, type, service, quantity, status]
    else:
        raise PreventUpdate

