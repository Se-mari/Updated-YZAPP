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
            dcc.Store(id='reportprofile_toload', storage_type='memory', data=0),
        ]),
        html.H2('Report'), # Page Header
        html.Hr(),
        dbc.Alert(id='reportprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
            dbc.Row(
                [
                    dbc.Label("Staff Name", width=1),
                    dbc.Col(
                        dcc.Dropdown(
                            id='reportprofile_name',
                            placeholder='Staff Name'
                        ),
                        width=5
                    )
                ],
                className = 'mb-3'
            ),
            dbc.Row(
                [
                dbc.Label("Report", width=1),
                    dbc.Col(
                        dbc.Input(
                            type='text',
                            id='reportprofile_report', #id 2
                            placeholder='Report'
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
                            id='reportprofile_removerecord',
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
            id='reportprofile_removerecord_div'
        ),


        dbc.Button(
            'Submit',
            id='reportprofile_submit',
            n_clicks=0 
        ),
        dbc.Modal( 
[
            dbc.ModalHeader(
                html.H4('Save Success')
            ),
            dbc.ModalBody(
                id= 'reportprofile_feedback_message'
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Proceed",
                    href='/modules/staff_report', 
                    id= 'reportprofile_btn_modal'
                )
            )
        ],
        centered=True,
        id='reportprofile_successmodal',
        backdrop='static' 
    )
])

@app.callback(
[
   
    Output('reportprofile_name', 'options'),
    Output('reportprofile_toload', 'data'),
    Output('reportprofile_submit', 'style'),
    Output('reportprofile_removerecord_div', 'style'),
],
[
    Input('url', 'pathname')
],
[
    State('url', 'search')
]
)
def reportprofile_populate(pathname, search):
    if pathname == '/modules/staff_report_profile':
        sql = """
        SELECT concat(staff_fname,' ',staff_lname ) as label, staff_id as value
        FROM staff
        WHERE staff_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options = df.to_dict('records')

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' or 'view' else 0
        show_submit= {'display': 'none'} if create_mode =='view' else None
        removediv_style = {'display': 'none'} if not to_load or create_mode=='view' else None

        return [options, to_load, show_submit, removediv_style]
    else:
        raise PreventUpdate
    
@app.callback(
    [
        Output('reportprofile_alert', 'color'),
        Output('reportprofile_alert', 'children'),
        Output('reportprofile_alert', 'is_open'),
        Output('reportprofile_successmodal', 'is_open'),
        Output('reportprofile_feedback_message', 'children'),
        Output('reportprofile_btn_modal', 'href')

    ],
    [
        Input('reportprofile_submit', 'n_clicks'),
        Input('reportprofile_btn_modal', 'n_clicks'),

    ],
[
State('reportprofile_name', 'value'),
State('reportprofile_report', 'value'),
State('url', 'search'),
State('reportprofile_removerecord', 'value'),
]
)
def reportprofile_saveprofile(submitbtn, closebtn, name, report, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'reportprofile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''
            feedbackmessage=''
            okay_href=''
            if not name: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply staff name.'
            elif not report:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the report.'
            else: 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                    insert into staff_report (staff_id, report, report_date, report_delete_ind	)
                    values ( %s, %s , current_timestamp,  %s)
                    '''
                    values = [name, report,False]
                    db.modifydatabase(sql, values)
                    feedbackmessage= "report has been saved"
                    okay_href='/modules/staff_report'
                    modal_open = True
                
                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    reportid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """
                    UPDATE staff_report SET staff_id=%s, report=%s, report_date=current_timestamp,  report_delete_ind=%s 
                    WHERE report_id = %s
                    """
                    to_delete = bool(removerecord)
                    values = [name, report, to_delete, reportid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Report has been updated."
                    okay_href = '/modules/staff_report'
                    modal_open = True
                elif create_mode == 'View':
                    parsed = urlparse(search)
                    reportid = parse_qs(parsed.query)['id'][0]
                    to_delete = bool(removerecord)
                    values = [name, report, to_delete, reportid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Report has been updated."
                    okay_href = '/modules/staff_report'
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
    Output('reportprofile_name', 'value'),
    Output('reportprofile_report', 'value'),
],
[
    Input('reportprofile_toload', 'modified_timestamp')
],
[
    State('reportprofile_toload', 'data'),
    State('url', 'search'),
]
)
def reportprofile_loadprofile(timestamp, toload, search):
    if toload: # check if toload = 1
        # Get movieid value from the search parameters
        parsed = urlparse(search)
        reportid = parse_qs(parsed.query)['id'][0]
        # Query from db
        sql = """
        Select staff_id, report
        from staff_report
		where report_id = %s
        """
        values = [reportid]
        col = ['staffid', 'report']
        df = db.querydatafromdatabase(sql, values, col)
        staffid = int(df['staffid'][0])
        report = df['report'][0]
        return [staffid, report]
    else:
        raise PreventUpdate

