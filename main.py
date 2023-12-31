from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import requests
import json
import os
from user_db import UsersDb

app = Flask(__name__)
usersDB = UsersDb()

app.secret_key = os.urandom(24)  # Set a secret key for session management

EVE_SSO_CLIENT_ID = "e4213c0567c74e25b322140565be55b6 "
EVE_SSO_CLIENT_SECRET = "89NNXp8UqfsmrCsjLgaQr3KV2qOpuC5mXMVjjAEd"
EVE_SSO_CALLBACK_URL = "http://localhost/sso/callback"


# Function to save timers to a JSON file
@app.route('/login')
def login():
    # Redirect the user to EVE Online's SSO login page

    sso_url = f"https://login.eveonline.com/v2/oauth/authorize?response_type=code&redirect_uri={EVE_SSO_CALLBACK_URL}" \
              f"&client_id={EVE_SSO_CLIENT_ID}&scope=esi-characters.read_notifications.v1&state=ssdfghhtf34"


    return redirect(sso_url)


@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('index'))


@app.route('/sso/callback')
def sso_callback():
    code = request.args.get('code')

    if code:
        # Exchange the authorization code for an access token
        token_url = "https://login.eveonline.com/v2/oauth/token"
        token_payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": EVE_SSO_CLIENT_ID,
            "client_secret": EVE_SSO_CLIENT_SECRET,
        }
        response = requests.post(token_url, data=token_payload)

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            session['access_token'] = access_token  # Store the access token in the session

            # get char ID from CCP
            url = "https://login.eveonline.com/oauth/verify"
            headers = {
                "Authorization": f"Bearer {session['access_token']}"
            }
            result = json.loads(requests.get(url, headers=headers).text)

            url = f"https://esi.evetech.net/latest/characters/{result['CharacterID']}/?datasource=tranquility"
            headers = {
                "accept": "application/json",
                "Cache-Control": "no-cache"
            }
            response = requests.get(url, headers=headers).json()  # get alliance info from ccp with char ID

            if not usersDB.get(result['CharacterID']):
                usersDB.add(result['CharacterID'], result['CharacterName'], response['alliance_id'])

            session['CharacterID'] = str(result['CharacterID'])
            session['char_alliance'] = str(response['alliance_id'])
            session['CharacterName'] = str(result['CharacterName'])



            return redirect(url_for('index'))
        else:
            return "Authentication failed."
    else:
        return jsonify("Authentication failed.")


@app.route('/auth', methods=['GET'])
def auth():
    with open("users.json", "r") as json_file:
        allowed_users = json.load(json_file)

    if 'access_token' not in session:
        return jsonify({'data': 'False'}), 401
    else:
        usersDB.load()

        if usersDB.get(session['CharacterID'])['char_name'] in allowed_users:
            return jsonify({'data': '1'}), 200
            print(jsonify({'data': '1'}))

        if usersDB.get(session['CharacterID'])['char_alliance'] in allowed_users:
            return jsonify({'data': 'True'}), 200



        else:
            return jsonify({'data': 'False'}), 401


@app.route('/api/structures', methods=['GET', 'POST'])
def get_structure_info():
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    ESI_BASE_URL = 'https://esi.evetech.net/latest'
    ID = '91704704'
    # endpoint = f'/corporations/98524122/structures/'
    endpoint = f'/characters/{ID}/notifications/'
    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    response = requests.get(ESI_BASE_URL + endpoint, headers=headers)

    return jsonify(response.text), 200



@app.route('/api/create_timer', methods=['POST']) # method for discord post
def send_discord_notification():
    webhook_url = "place webhook here"
    data2 = request.json['timer_name']
    timer_name = data2['name']
    type = data2['type']
    category = data2['timerCat']
    date = data2['countdownDate']
    author = data2['authUserName']


    content = f'New timer created:\n**System:** {timer_name}\n**Type:** {type}' \
              f'\n**Category:** {category}\n**Date:** {date}\n**Created:** {author} '
    data = {
        'content': content
    }
    response = requests.post(webhook_url, json=data)


    if response.status_code == 204:
        print("Notification sent successfully")
        return jsonify({'message': 'Timer send to discord channel.'}), 200
    else:
        print("Failed to send notification")
        return jsonify({'message': 'Timer failed.'}), 501



@app.route('/api/timers', methods=['GET', 'POST'])
def timers():
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if request.method == 'POST':
        data = request.json
        timers = data.get('timers', [])
        save_timers(timers)  # Save timers to the server whenever a new timer is added or deleted
        return jsonify({'message': 'Timers saved successfully!'}), 200
    elif request.method == 'GET':
        timers = load_timers()
        return jsonify(timers), 200


def save_timers(timers):
    with open('timers.json', 'w') as json_file:
        sorted_data = sorted(timers, key=lambda x: x["countdownDate"])

        json.dump(sorted_data, json_file)


# Function to load timers from the JSON file
def load_timers():
    if os.path.exists('timers.json'):
        with open('timers.json', 'r') as file:
            data_list = json.load(file)
            sorted_data = sorted(data_list, key=lambda x: x["countdownDate"])
            return sorted_data
    return []


def read_autocomplete_strings():
    with open('autocomplete_strings.txt', 'r') as file:
        return [line.strip() for line in file]


@app.route('/')
def index():

    with open("users.json", "r") as json_file:
        allowed_users = json.load(json_file)

    if 'access_token' not in session:
        authenticated = False
        return render_template('index.html', timers=None, authenticated=authenticated,
                               CharacterName="Please login to view timers.")
    else:

        usersDB.load()

        if usersDB.get(session['CharacterID'])['char_alliance'] in allowed_users:
            authenticated = True
            timers = load_timers()  # Load timers from the server on page load

            return render_template('index.html', timers=timers, authenticated=authenticated,
                                   CharacterName=session['CharacterName'])
        else:
            authenticated = False
            return render_template('index.html', timers=None, authenticated=authenticated,
                                   CharacterName=f"{session['CharacterName']} is not allowed to view timers.")


@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    autocomplete_strings = read_autocomplete_strings()
    return jsonify(autocomplete_strings), 200


# Function to get the dropdown options for the structure_type field
def get_structure_type_options():
    options = [
        "Astrahus",
        "Raitaru",
        "Athanor",
        "Fortizar",
        "Keepstar",
        "Azbel",
        "Sotiyo",
        "Tatara"
    ]
    return options


structure_type_options = [
    {
        "name": "Astrahus",
        "image_link": "/static/astrahus.jpg",
    },
    {
        "name": "Raitaru",
        "image_link": "/static/astrahus.jpg",
    },
    {
        "name": "Athanor",
        "image_link": "/static/astrahus.jpg",
    },
    {
        "name": "Fortizar",
        "image_link": "/static/astrahus.jpg",
    },
    {
        "name": "Keepstar",
        "image_link": "/static/astrahus.jpg",
    },
    {
        "name": "Azbel",
        "image_link": "/static/astrahus.jpg",
    },
    {
        "name": "Sotiyo",
        "image_link": "/static/astrahus.jpg",
    },
    {
        "name": "Tatara",
        "image_link": "/static/astrahus.jpg",
    }

]


@app.route('/api/structure_type_options', methods=['GET'])
def structure_type_options():
    options = get_structure_type_options()
    return jsonify(options), 200


def get_radio_button_options():
    options = ["Offensive", "Defensive"]
    return options


@app.route('/api/radio_button_options', methods=['GET'])
def radio_button_options():
    options = get_radio_button_options()
    return jsonify(options), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
