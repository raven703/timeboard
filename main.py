from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)


# Function to save timers to a JSON file
def save_timers(timers):
    with open('timers.json', 'w') as file:
        json.dump(timers, file)

# Function to load timers from the JSON file
def load_timers():
    if os.path.exists('timers.json'):
        with open('timers.json', 'r') as file:
            return json.load(file)
    return []

def read_autocomplete_strings():
    with open('autocomplete_strings.txt', 'r') as file:
        return [line.strip() for line in file]

@app.route('/')
def index():
    timers = load_timers()  # Load timers from the server on page load
    return render_template('index.html', timers=timers)

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    autocomplete_strings = read_autocomplete_strings()
    return jsonify(autocomplete_strings), 200

@app.route('/api/timers', methods=['GET', 'POST'])
def timers():
    if request.method == 'POST':
        data = request.json
        timers = data.get('timers', [])
        save_timers(timers)  # Save timers to the server whenever a new timer is added or deleted
        return jsonify({'message': 'Timers saved successfully!'}), 200
    elif request.method == 'GET':
        timers = load_timers()
        return jsonify(timers), 200

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
    app.run()
