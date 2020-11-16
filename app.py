import json
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
from dash.dependencies import Input, Output, State
import time
import dash_table
from flask import jsonify

app = dash.Dash()
app.title = "Unofficial RuneScape Hiscores"
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# the first 23 are both osrs and rs3 the last ones are just rs3
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
    20: 'Runecrafting',
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
        'color': colors['text'],
        'padding': '5px'
    }),
    html.Div(style={
        'text-align': 'center',
        'color': colors['text'],
        'width': '30%',
        'padding': '3px',
        'border': '3px solid white',
        'margin': 'auto',
        'align': 'center'
    }, children=[
        html.Button('GET USER', id='search_button', style={
            'align': 'center',
            'padding': '3px',
            'textColor': '#FFFFFF'
        }),
        dcc.Input(
            id='name1',
            placeholder='Enter name',
            style={
                'padding': '3px'
            }
        ),
        dcc.Input(
            id='name2',
            placeholder='Enter name',
            style={
                'padding': '3px'
            }
        ),
        dcc.Dropdown(
            id='data_type',
            options=[
                {'label': 'Level', 'value': 'level'},
                {'label': 'Experience', 'value': 'xp'}
            ],
            value='level',
            style={
                'padding': '3px'
            }
        ),
        dcc.Dropdown(
            id='graph_type',
            options=[
                {'label': 'Bar', 'value': 'bar'},
                {'label': 'Scatter', 'value': 'scatter'}
            ],
            value='bar',
            style={
                'padding': '3px'
            }
        ),
        dcc.Dropdown(
            id='game_type',
            options=[
                {'label': 'OSRS', 'value': 'osrs'},
                {'label': 'RS3', 'value': 'rs3'}
            ],
            value='osrs',
            style={
                'padding': '3px'
            }
        ),
        dcc.Dropdown(
            id='game_mode',
            options=[
                {'label': 'Normal', 'value': 'normal'},
                {'label': 'Ironman', 'value': 'ironman'},
                {'label': 'Ultimate Ironman', 'value': 'ultimate_ironman'}
            ],
            value='normal',
            style={
                'padding': '3px'
            }
        ),
        html.Div(
            "",
            id='output'
            # if we put the graph inside here we can update the title first
        )
    ]),
    html.Div(id='graph-div', children=[
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
        ),
        # ToDo add a table below displaying the players data
        # dash_table.DataTable(
        #     id='table',
        #     columns=[{"Skills", "Level", "Experience"}],
        # )
    ]),

])


# A call back which get the value from the text boxes, calls the rs API's converts the data and returns them as graphs
# ToDo make graph element invisible if empty
@app.callback(
    [Output('graph', 'figure'),
     Output('graph-div', 'style')],
    [Input('search_button', 'n_clicks')],
    [State('name1', 'value'), State('name2', 'value'), State('data_type', 'value'), State('graph_type', 'value'),
     State('game_type', 'value'), State('game_mode', 'value')])
def on_click(search_button, name1, name2, data_type, graph_type, game_type, game_mode):
    graph_type = "table"
    score = get_highscore(name1, game_type, game_mode)
    if name2:
        score2 = get_highscore(name2, game_type, game_mode)
    else:
        score2 = None
    if not score2:
        g, success = gen_level_graph(name1, score, None, None, data_type, graph_type, game_type, game_mode)
        if success:
            return g, {'display': 'block'}
        else:
            return g, {'display': 'none'}
    elif score2:
        g, success = gen_level_graph(name1, score, name2, score2, data_type, graph_type, game_type, game_mode)
        if success:
            return g, {'display':'block'}
        else:
            return g, {'display':'none'}
    # instead of returning a div, we want to return a dcc.Graph


def get_highscore(name, game, game_mode):
    if game == "rs3":
        if name:
            start = time.time()
            middle = ""
            if game_mode == "ironman" or "hardcore_ironman":
                middle = "_ironman"
            elif game_mode == "ultimate_ironman":
                middle = "_ultimate_ironman"
            response = requests.get(
                "http://services.runescape.com/m=hiscore" + middle + "/index_lite.ws?player=" + str(name))
            print("took: " + str(time.time() - start) + " seconds")
            content = str(response.content)
            content = content.split("\\n")
            content[0] = content[0][2:]
            # stored as rank, level, xp
            unf_hiscore = content[1:24]
            try:
                hiscore = []
                for n in range(len(unf_hiscore)):
                    values = unf_hiscore[n].split(",")
                    hiscore.append(
                        {'level': int(values[1]), 'xp': (int(values[2]) * 10), 'rank': int(values[0]), 'id': n})
                return hiscore
            except:
                return "Error: User not found"
        return "Error: User not found"
    else:
        if name:
            start = time.time()
            middle = ""
            if game_mode == "ironman" or "hardcore_ironman":
                middle = "_ironman"
            elif game_mode == "ultimate_ironman":
                middle = "_ultimate_ironman"
            response = requests.get(
                "http://services.runescape.com/m=hiscore_oldschool" + middle + "/index_lite.ws?player=" + str(name))
            print("took: " + str(time.time() - start) + " seconds")
            content = str(response.content)
            content = content.split("\\n")
            content[0] = content[0][2:]
            # stored as rank, level, xp
            unf_hiscore = content[1:24]
            try:
                hiscore = []
                for n in range(len(unf_hiscore)):
                    values = unf_hiscore[n].split(",")
                    hiscore.append({'level': int(values[1]), 'xp': (int(values[2]) * 10), 'rank': int(values[0]), 'id': n})
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


def gen_level_graph(name, data, name2, data2, graph_data_type, graph_type, game_type, game_mode):
    x = []
    y = []
    x2 = []
    y2 = []
    success = False
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
        success = True
    else:
        # ToDo add error handling if user now found
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
            # ToDo add other graph types
            data = [{'x': x, 'y': y, 'type': graph_type, 'name': name},
                    {'x': x2, 'y': y2, 'type': graph_type, 'name': name2}]
            # and concat the names into two
            if name and name2:
                name = name.lower() + " vs " + name2.lower()
            success = True
    # ToDo fix the fact that the different game modes show the same data (settled and swampletics)
    if game_mode == "ironman":
        game_mode == "Ironman"
    elif game_mode == "ultimate_ironman":
        game_mode = "Ultimate Ironman"
    else:
        game_mode = "Normal"
    figure = {
        'data': data,
        'layout': {
            'title': 'Graph of ' + graph_data_type + ' for ' + str(name) + " (" + str(game_type).upper() + " - " + game_mode + ")",
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            }
        }
    }
    return figure, success


if __name__ == "__main__":
    # get_highscore('torvesta', 'osrs')
    app.run_server(debug=True)
