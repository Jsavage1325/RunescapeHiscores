import json
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
from dash.dependencies import Input, Output, State
from flask import jsonify

app = dash.Dash()
app.title = "Unofficial RuneScape Hiscores"
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

level_names = {
    0: 'Attack',
    1: 'Defence',
    2: 'Strength',
    3: 'Hitpoints',
    4: 'Ranged',
    5: 'Prayer',
    6: 'Magic',
    7: 'Cooking',
    8: 'Woodcutting',
    9: 'Fletching',
    10: 'Fishing',
    11: 'Firemaking',
    12: 'Crafting',
    13: 'Smithing',
    14: 'Mining',
    15: 'Herblore',
    16: 'Agility',
    17: 'Thieving',
    18: 'Slayer',
    19: 'Farming',
    20: 'Runescrafting',
    21: 'Hunter',
    22: 'Construction',
    23: 'Summoning',
    24: 'Dungeoneering',
    25: 'Divination',
    26: 'Invention',
    27: 'Archaeology'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Unofficial RuneScape Highscores',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children='A web app to display and compare user stats using some cool graphics.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div(style={
        'textAlign': 'center',
        'color': colors['text'],
    }, children=[
        html.Button('Get User', id='search_button', style={
            'align': 'center'
        }),
        dcc.Input(
            id='name1',
            placeholder='Enter name',
        ),
        dcc.Input(
            id='name2',
            placeholder='Enter name',
        ),
        dcc.Dropdown(
            id='data_type',
            options=[
                {'label': 'Level', 'value': 'level'},
                {'label': 'Experience', 'value': 'xp'}
            ],
            value='level'
        ),
        dcc.Dropdown(
            id='graph_type',
            options=[
                {'label': 'Bar', 'value': 'bar'},
                {'label': 'Scatter', 'value': 'scatter'}
            ],
            value='bar'
        ),
        html.Div(
            "",
            id='output'
            # if we put the graph inside here we can update the title first
        )
    ]),
    dcc.Graph(
        id='graph',
        figure={
            'data': [
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    )
])


# A call back which get the value from the
@app.callback(
    Output('graph', 'figure'),
    [Input('search_button', 'n_clicks')],
    [State('name1', 'value'), State('name2', 'value'), State('data_type', 'value'), State('graph_type', 'value')])
def on_click(search_button, name1, name2, data_type, graph_type):
    # print("Name: {}").format(Name)
    score = get_highscore(name1)
    if name2:
        score2 = get_highscore(name2)
    else:
        score2 = None
    if not score2:
        return gen_level_graph(name1, score, None, None, data_type, graph_type)
    elif score2:
        return gen_level_graph(name1, score, name2, score2, data_type, graph_type)
    # instead of returning a div, we want to return a dcc.Graph


def get_highscore(name):
    if name:
        response = requests.get(
            "https://apps.runescape.com/runemetrics/profile/profile?user=" + name + "&activities=20")
        try:
            if json.loads(response.text)['skillvalues']:
                hiscore = json.loads(response.text)["skillvalues"]
                return hiscore
        except:
            return "Error: User not found"
    return "Error: User not found"


# gets id of object, used in sorting the data into correct order
def get_id(object):
    return object['id']


def remove_decimal_part(d, graph_data_type):
    if graph_data_type == "xp":
        try:
            d[graph_data_type] = int(str(d[graph_data_type])[:-1])
        except:
            d[graph_data_type] = 0


def gen_level_graph(name, data, name2, data2, graph_data_type, graph_type):
    x = []
    y = []
    x2 = []
    y2 = []
    if name2 is None:
        if str(data) == "Error: User not found" or type(data) != list:
            # dont think we can return none here, think we need to return empty graph component
            x = [0]
            y = [0]
        else:
            data.sort(key=get_id)
            # instead of doing this we need to do a loop which gets the id and the
            for d in data:
                x.append(level_names[int(d["id"])])
                # for some reason xp is displayed without a decimal point, so we need to remove last points
                remove_decimal_part(d, graph_data_type)
                y.append(d[graph_data_type])
        if name:
            name = name.lower()
        data = [{'x': x, 'y': y, 'type': graph_type, 'name': name}]
    else:
        if str(data) == "Error: User not found" or str(data2) == "Error: User not found" or type(data) != list:
            # dont think we can return none here, think we need to return empty graph component
            x = [0]
            y = [0]
        else:
            # sort both data into order
            data.sort(key=get_id)
            data2.sort(key=get_id)
            # loop through both data adding to x and y for graph
            for d in data:
                remove_decimal_part(d, graph_data_type)
                x.append(level_names[int(d["id"])])
                y.append(d[graph_data_type])
            for d2 in data2:
                remove_decimal_part(d2, graph_data_type)
                x2.append(level_names[int(d2["id"])])
                y2.append(d2[graph_data_type])
            data = [{'x': x, 'y': y, 'type': graph_type, 'name': name}, {'x': x2, 'y': y2, 'type': graph_type, 'name': name2}]
            # and concat the names into two
            if name and name2:
                name = name.lower() + " vs " + name2.lower()
    print(str(data))
    figure = {
        'data': data,
        'layout': {
            'title': 'Graph of ' + graph_data_type + ' for ' + str(name),
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            }
        }
    }
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
