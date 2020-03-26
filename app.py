from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from secret import api_key
import requests
import json

app = Flask(__name__)

app.config['SECRET_KEY']='jkfds'
#debug = DebugToolbarExtension(app)

@app.route('/')
def index():
    with open('data.json') as file:
        data = json.load(file)
    return render_template('hello.html', data=data)

@app.route('/matches')
def matches():
    r=get_matches('exso763')
    json_data = json.loads(r)
    return render_template('matches.html', data=json_data)

@app.route('/players')
def players():
    r=get_players('exso763')
    json_data = json.loads(r)
    return render_template('players.html', data=json_data)

@app.route('/matchups')
def matchups():
    m=get_matches('exso763')
    matches = json.loads(m)
    p=get_players('exso763')
    players = json.loads(p)
    player_refs = get_player_names(players)
    #player_refs = {117770544 : "ebomb", 117770547:"Kriss"}
    
    
    return render_template('matchups.html', matches=matches, players=players, x=player_refs)

@app.route('/report_win/<int:match_id>/<int:winner_id>/<int:score>', methods=['POST'])
def report_match(match_id, winner_id, score):
    # limited to two score reports
    # int:score represents loser score. report win as 2-0 or 2-1
    update_score('exso763', match_id, winner_id, score)
    return redirect('/matchups')



### API STUFF
def get_api_data():

    API_KEY = api_key
    url = 'https://api.challonge.com/v1/tournaments.json'
    params = {
        "api_key" : API_KEY,
        "subdomain" : "akg",
    }

    r = requests.get(url, params=params)
    return r

def get_matches(tournament_id):

    API_KEY = api_key
    url = f'https://api.challonge.com/v1/tournaments/akg-{tournament_id}/matches.json'
    params = {
        "api_key" : API_KEY,
        "subdomain" : "akg",
    }

    r = requests.get(url, params=params)
    return r.text

def get_players(tournament_id):

    API_KEY = api_key
    url = f'https://api.challonge.com/v1/tournaments/akg-{tournament_id}/participants.json'
    params = {
        "api_key" : API_KEY,
        "subdomain" : "akg",
    }

    r = requests.get(url, params=params)
    return r.text

def get_player_names(players):
    # pass in API response from participants of tournament
    # return dict with key of player id and value of player name:
    # {player_id:"display_name"}
    # {123456:"playerone", 345678:"playertwo", ...}
    player_dict = {}
    for player in players:
        player_dict[player['participant']['id']] = player['participant']['display_name']
    return player_dict

def update_score(tournament_id, match_id, winner_id, score):

    score_string = '2-0' if score == 0 else '2-1'
    
    API_KEY = api_key
    url = f'https://api.challonge.com/v1/tournaments/akg-{tournament_id}/matches/{match_id}.json'
    params = {
        "api_key" : API_KEY,
        "subdomain" : "akg",
        "match[winner_id]" : winner_id,
        "match[scores_csv]" : score_string,
    }

    r = requests.put(url, data=params)
    
    
    return r.text