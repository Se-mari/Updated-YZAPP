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
            dcc.Store(id='materialprofile_toload', storage_type='memory', data=0),
        ]),
        html.H2('Material'), # Page Header
        html.Hr(),
        dbc.Alert(id='materialprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
            dbc.Row(
                [
                dbc.Label("Material Name", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='materialprofile_name', #id 2
                            placeholder='Material'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Category Name", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='materialprofile_category',
                            placeholder='Category Name'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Unit Price", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='number',
                            id='materialprofile_price', #id 2
                            placeholder='Price'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Reorder Point", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='number',
                            id='materialprofile_reorder', #id 2
                            placeholder='Reorder Point'
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
                            id='materialprofile_removerecord',
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
            id='materialprofile_removerecord_div'
        ),


        dbc.Button(
            'Submit',
            id='materialprofile_submit',
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'materialprofile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/material', 
                    id= 'materialprofile_btn_modal'
                )
            )
        ],
        centered=True,
        id='materialprofile_successmodal',
        backdrop='static' 
    )
])

@app.callback(
[
    Output('materialprofile_category', 'options'),
    Output('materialprofile_toload', 'data'),
    Output('materialprofile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def materialprofile_populate(pathname, search):
    if pathname == '/modules/material_profile':
        sql = """
        SELECT category_name as label, category_id as value
        FROM category
        WHERE category_delete_ind = False
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
        Output('materialprofile_alert', 'color'),
        Output('materialprofile_alert', 'children'),
        Output('materialprofile_alert', 'is_open'),
        Output('materialprofile_successmodal', 'is_open'),
        Output('materialprofile_feedback_message', 'children'),
        Output('materialprofile_btn_modal', 'href')

    ],
    [
        Input('materialprofile_submit', 'n_clicks'),
        Input('materialprofile_btn_modal', 'n_clicks'),

    ],
[
State('materialprofile_name', 'value'),
State('materialprofile_category', 'value'),
State('materialprofile_price', 'value'),
State('materialprofile_reorder', 'value'),
State('url', 'search'),
State('materialprofile_removerecord', 'value'),
]
)
def materialprofile_saveprofile(submitbtn, closebtn, material, category, price, reorder, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'materialprofile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not material: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please put material name.'
            elif not category:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the material category.'
            elif not price:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please input the unit price of the material.'
            elif not reorder:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the reorder point of the material.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into material (material_name, category_id, unit_price, reorder_point, material_delete_ind	)
                    values ( %s, %s , %s, %s, %s)
                    '''
                    values = [material, category, price, reorder, False]
                    db.modifydatabase(sql, values)
                    feedbackmessage= "Material data has been saved"
                    okay_href='/modules/material'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    materialid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    UPDATE material SET material_name=%s, category_id=%s, unit_price=%s, reorder_point=%s, material_delete_ind=%s
                    WHERE material_id = %s
                    """
                    to_delete = bool(removerecord)
                    values = [material, category, price, reorder, to_delete, materialid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Material data has been updated."
                    okay_href = '/modules/material'
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
    Output('materialprofile_name', 'value'),
    Output('materialprofile_category', 'value'),
    Output('materialprofile_price', 'value'),
    Output('materialprofile_reorder', 'value'),
],
[
    Input('materialprofile_toload', 'modified_timestamp')
],
[
    State('materialprofile_toload', 'data'),
    State('url', 'search'),
]
)
def materialprofile_loadprofile(timestamp, toload, search):
    if toload: # check if toload = 1
        # Get movieid value from the search parameters
        parsed = urlparse(search)
        materialid = parse_qs(parsed.query)['id'][0]
        # Query from db
        sql = """
        Select material_name, category_id, unit_price, reorder_point
        from material
        where material_id=%s
        """
        values = [materialid]
        col = ['material_name', 'category_id', 'unit_price', 'reorder_point']
        df = db.querydatafromdatabase(sql, values, col)
        material_name=df['material_name'][0]
        category_id = int(df['category_id'][0])
        unit_price = int(df['unit_price'][0])
        reorder_point = int(df['reorder_point'][0])
        return [material_name, category_id, unit_price, reorder_point]
    else:
        raise PreventUpdate

