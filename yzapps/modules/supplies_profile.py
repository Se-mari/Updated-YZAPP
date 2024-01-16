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
            dcc.Store(id='suppliesprofile_toload', storage_type='memory', data=0),
        ]),
        html.H2('Supplies'), # Page Header
        html.Hr(),
        dbc.Alert(id='suppliesprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
            dbc.Row(
                [
                    dbc.Label("Sales Invoice", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='suppliesprofile_invoice',
                            placeholder='Sales Invoice'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Material Ordered", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='suppliesprofile_material',
                            placeholder='Material Name'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Supplier", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='suppliesprofile_supplier',
                            placeholder='Supplier Name'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Quantity Ordered", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='number',
                            id='suppliesprofile_quantity', #id 2
                            placeholder='Order Quantity'
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
                            id='suppliesprofile_removerecord',
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
            id='suppliesprofile_removerecord_div'
        ),


        dbc.Button(
            'Submit',
            id='suppliesprofile_submit',
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'suppliesprofile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/supplies', 
                    id= 'suppliesprofile_btn_modal'
                )
            )
        ],
        centered=True,
        id='suppliesprofile_successmodal',
        backdrop='static' 
    )
]
)

@app.callback(
[
    Output('suppliesprofile_invoice', 'options'),
    Output('suppliesprofile_material', 'options'),
    Output('suppliesprofile_supplier', 'options'),
    Output('suppliesprofile_toload', 'data'),
    Output('suppliesprofile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def suppliesprofile_populate(pathname, search):
    if pathname == '/modules/supplies_profile':
        
        sql = """
        SELECT concat( sales_invoice,' Date- ', purchase_order_date) as label, purchase_id as value
        FROM purchase_order
        WHERE purchase_order_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options1 = df.to_dict('records')
        
        sql = """
        SELECT material_name as label, material_id as value
        FROM material
        WHERE material_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options2 = df.to_dict('records')

        sql = """
        SELECT suppliers_name as label, suppliers_id as value
        FROM suppliers
        WHERE suppliers_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options3 = df.to_dict('records')

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None

        return [options1, options2, options3, to_load, removediv_style]
    else:
        raise PreventUpdate
    
@app.callback(
    [
        Output('suppliesprofile_alert', 'color'),
        Output('suppliesprofile_alert', 'children'),
        Output('suppliesprofile_alert', 'is_open'),
        Output('suppliesprofile_successmodal', 'is_open'),
        Output('suppliesprofile_feedback_message', 'children'),
        Output('suppliesprofile_btn_modal', 'href')

    ],
    [
        Input('suppliesprofile_submit', 'n_clicks'),
        Input('suppliesprofile_btn_modal', 'n_clicks'),

    ],
[
State('suppliesprofile_invoice', 'value'),    
State('suppliesprofile_material', 'value'),
State('suppliesprofile_supplier', 'value'),
State('suppliesprofile_quantity', 'value'),
State('url', 'search'),
State('suppliesprofile_removerecord', 'value'),
]
)
def suppliesprofile_saveprofile(submitbtn, closebtn, invoice, material, supplier, quantity, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'suppliesprofile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not invoice:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the sales invoice.'
            elif not material:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the material.'
            elif not supplier:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the supplier of the material.'
            elif not quantity:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the quantity of the material'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into supplies (material_id, suppliers_id, purchase_id, quantity, supplies_delete_ind)
                    values(%s, %s, %s, %s, %s)
                    '''
                    values = [material, supplier, invoice, quantity, False]
                    db.modifydatabase(sql, values)
                    
                    feedbackmessage= "Supply data has been saved"
                    okay_href='/modules/supplies'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    suppliesid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    update supplies set material_id=%s, suppliers_id=%s, purchase_id=%s, quantity=%s, supplies_delete_ind=%s
                    where supply_id=%s
                    """
                    to_delete = bool(removerecord)
                    values = [ material, supplier, invoice, quantity, to_delete, suppliesid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Supply data has been updated."
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
    Output('suppliesprofile_invoice', 'value'),
    Output('suppliesprofile_material', 'value'),
    Output('suppliesprofile_supplier', 'value'),
    Output('suppliesprofile_quantity', 'value'),
],
[
    Input('suppliesprofile_toload', 'modified_timestamp')
],
[
    State('suppliesprofile_toload', 'data'),
    State('url', 'search'),
]
)
def suppliesprofile_loadprofile(timestamp, toload, search):
    if toload: # check if toload = 1
        # Get movieid value from the search parameters
        parsed = urlparse(search)
        materialid = parse_qs(parsed.query)['id'][0]
        # Query from db
        sql = """
        select purchase_id, material_id, suppliers_id, quantity
        from supplies
        where supply_id=%s
        """
        values = [materialid]
        col = ['purchase', 'material', 'supply', 'quantity']
        df = db.querydatafromdatabase(sql, values, col)
        purchase = int(df['purchase'][0])
        material = int(df['material'][0])
        supply = int(df['supply'][0])
        amount = int(df['quantity'][0])
        return [purchase, material, supply, amount]
    else:
        raise PreventUpdate

