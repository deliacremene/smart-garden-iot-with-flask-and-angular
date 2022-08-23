# smart-garden-iot-with-flask-and-angular

This is an irrigation system management project that has:
- a REST API using C++ for the board, sensors and pump with the purpose of connecting the board to the internet and to the Flask app, reading sensor data and turning the pump on and off
- a main REST API Flask app that interacts with the board's REST API for saving the board details, for pinging the board to update its connectivity status, for getting sensor data and changing the pump state, for defining objects such as board, sensor reading, pump history and plant and storing them in the database using SQLAlchemy ORM and Postgres RDBMS
- a frontend consisting of an Angular app that allows the user to view all boards and all plants, add/update/delete plants, add a plant to a board, see the status of the board, change the pump state and visualize sensor readings in a plot that is updated in real time

## the circuit diagram of the irrigation system
![image](https://user-images.githubusercontent.com/50794133/186075312-da9b0bfc-7186-4d36-bccc-f52db0898a6b.png)

## board visualization in the web app
![image](https://user-images.githubusercontent.com/50794133/186075551-3fcc9e74-6e7b-46a3-bfa0-b4ee7b258f37.png)

## plant visualization in the web app 
![image](https://user-images.githubusercontent.com/50794133/186075594-12b4422e-209d-497e-a826-c7858bb72bb4.png)

## the database schema
![image](https://user-images.githubusercontent.com/50794133/186077498-ce99c5ee-eff7-4f72-93f8-e6ce855c2b94.png)
