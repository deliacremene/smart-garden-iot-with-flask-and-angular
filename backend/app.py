import string
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import requests
from datetime import datetime
from dataclasses import dataclass
from apscheduler.schedulers.background import BackgroundScheduler
from ping3 import ping

# database settings (should be hidden)
db_url = 'localhost:5432'
db_name = 'smartgarden'
db_user = 'root'
db_password = '230499'

# initializing a flask app
app = Flask(__name__)
# allow cors (cross-origin resource sharing) to be able to make requests over different domains
CORS(app)
# silence tracking sqlalchemy modifications to save system resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# config postgresql db uri
# the chosen db is postgresql which is a popular open source relational db management system
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_url}/{db_name}'
# configure our db by binding the instance to our flask app; sqlalchemy is an object-relational mapper
# automatically translates python classes and relationships to tables in db, converts function calls to sql statements
# standard interface that allows the creation of db agnostic code that can communicate to a large variety of db
db = SQLAlchemy(app)
# use migrate to be able to make db migrations to update db
# flask migrate is an extension that handles sqlalchemy db migrations for flask apps using alembic
migrate = Migrate(app, db)


# the dataclass decorator implicitly creates __init__ (constructor), __str__, __eq__ methods
# provides astuple() and asdisct() methods
# and also helps with object serialization
# in the future maybe use marshmallow schemas to serialize/deserialize data
# it's an orm to convert complex datatypes such as objects to and from python native datatypes
@dataclass
class PumpStateHistory(db.Model):
    id: int
    status: string
    time: datetime
    board_id: int

    __tablename__ = 'pump_state_history'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=True)
    time = db.Column(db.DateTime, nullable=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=True)


@dataclass
class Plant(db.Model):
    id: int
    name: string
    optimal_moisture: float
    optimal_humidity: float
    optimal_temperature: float
    image: string

    __tablename__ = 'plant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    optimal_moisture = db.Column(db.Float, nullable=False)
    optimal_humidity = db.Column(db.Float, nullable=False)
    optimal_temperature = db.Column(db.Float, nullable=False)
    image = db.Column(db.String, nullable=True)


@dataclass
class Board(db.Model):
    id: int
    ip: string
    plant_id: int
    status: string

    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=True)
    status = db.Column(db.String, nullable=True)


@dataclass
class SensorReading(db.Model):
    id: int
    moisture: float
    humidity: float
    temperature: float
    time: datetime
    board_id: int

    __tablename__ = 'sensor_readings'
    id = db.Column(db.Integer, primary_key=True)
    moisture = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    time = db.Column(db.DateTime, nullable=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=True)


@app.route('/')
def hello_world():
    return 'welcome to smart garden'


# this endpoint is called by the nodemcu board to "connect" with the flask app
# the board will be saved in the db
@app.post('/connectBoard')
def get_boards():
    board_data = request.json
    board = Board.query.get(board_data['board_id'])
    print('----------------------------------')
    print('board with id', board_data['board_id'], 'is online')
    if board is None:
        print('board does not exist yet, added a new board')
        board = Board(board_data['board_id'], board_data['ip'], None, 'Active')
        db.session.add(board)
        db.session.commit()
    else:
        if board.ip != board_data['ip']:
            print('board already exists, updated ip and status to Active')
            board.ip = board_data['ip']  # update ip in case it is different for the same board
        print('board already exists, updated status to Active')
        board.status = 'Active'
        db.session.add(board)
        db.session.commit()
    print(board)
    return board_data


# this method calls the board's rest api to retrieve sensor data
@app.get('/getSensorData/<int:board_id>')
def get_sensor_data(board_id):
    board = Board.query.get(board_id)
    if board is None:
        abort(404)
    else:
        # use the board's ip to make request
        board_ip = board.ip
        response = requests.get('http://%s/getSensorReadings' % board_ip).json()

        # unpack the response json like a dictionary and provide the data to the constructor
        sensor_reading = SensorReading(**response)

        # save a new sensor_reading object in the db
        db.session.add(sensor_reading)
        db.session.commit()
        return response


# this method calls the board's rest api to change the pump state (turn on or off)
@app.put('/changePumpState/<int:board_id>/<string:pump_state>')
def change_pump_state(board_id, pump_state):
    board = Board.query.get(board_id)
    if board is None:
        abort(404)
    else:
        board_ip = board.ip
        if pump_state == 'on':
            response = requests.get('http://%s/turnPumpOn' % board_ip).json()
            pump_state_history = PumpStateHistory('on', response['board_id'])
            db.session.add(pump_state_history)
            db.session.commit()
        else:
            response = requests.get('http://%s/turnPumpOff' % board_ip).json()
            pump_state_history = PumpStateHistory('off', response['board_id'])
            db.session.add(pump_state_history)
            db.session.commit()
        return response


@app.get('/getPumpState/<int:board_id>')
def get_pump_state(board_id):
    board = Board.query.get(board_id)
    if board is None:
        abort(404)
    else:
        board_ip = board.ip
        response = requests.get('http://%s/getPumpState' % board_ip).json()
        return response


@app.get('/getAllBoards')
def get_all_boards():
    boards = Board.query.all() or []
    return jsonify(boards)


# some CRUD operations to add plants that have a one to many relationship with the board
# one board/irrigation system can only be connected to a plant/crop at a time
# a plant/crop can have multiple board/irrigation systems

@app.post('/addPlant')
def create_plant():
    plant_data = request.json
    if "id" in plant_data:
        del plant_data["id"]
    plant = Plant(**plant_data)
    db.session.add(plant)
    db.session.commit()
    return jsonify(plant), 201


@app.get('/getPlant/<int:plant_id>')
def get_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if plant is None:
        abort(404)
    else:
        return jsonify(plant)


@app.get('/getAllPlants')
def get_all_plants():
    plants = Plant.query.all() or []
    return jsonify(plants)


@app.patch('/updatePlant/<int:plant_id>')
def update_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if plant is None:
        abort(404)
    else:
        if 'name' in request.json:
            plant.name = request.json['name']
        if 'optimal_temperature' in request.json:
            plant.optimal_temperature = request.json['optimal_temperature']
        if 'optimal_humidity' in request.json:
            plant.optimal_humidity = request.json['optimal_humidity']
        if 'optimal_moisture' in request.json:
            plant.optimal_moisture = request.json['optimal_moisture']
        if 'image' in request.json:
            plant.image = request.json['image']

        db.session.commit()
        return '', 204


@app.delete('/deletePlant/<int:plant_id>')
def delete_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if plant is None:
        abort(404)
    else:
        db.session.delete(plant)
        db.session.commit()
        return '', 204


# every board in our database, while active, will be pinged to make sure that it is still connected
# if not connected anymore, we change its status to inactive, and we do not ping it anymore
# when the board reconnects, it calls the /connectBoard endpoint and the status is made active again
def scheduled_board_pings():
    boards = Board.query.all()
    print('----------------------------------')
    print('checking boards')
    for board in boards:
        if board.status == 'Active':
            ping_result = pingBoards(board.ip)
            print(board, '-> Ping result: ', ping_result)
            if not ping_result:
                print('board with id', board.id, 'went offline, updated status to Inactive')
                board.status = 'Inactive'
                db.session.add(board)
                db.session.commit()


# a ping (packet internet groper)
# allows testing if a particular destination exists and can accept requests
# sends a signal and listens for a response
# we want this so that we can keep track of the board's uptime/connectivity
def pingBoards(host):
    for i in range(3):
        print(f'trying to ping {host}')
        resp = ping(host)
        if resp:
            return True
    return False


# define a background scheduler that at a time interval pings the board server to see if it is on
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_board_pings, 'interval', seconds=10)
scheduler.start()

db.create_all()

if __name__ == '__main__':
    app.run()
