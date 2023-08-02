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

@app.route('/')
def index():
    timers = load_timers()  # Load timers from the server on page load
    return render_template('index.html', timers=timers)

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

if __name__ == '__main__':
    app.run()