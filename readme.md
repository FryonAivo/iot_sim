### IoT simulation for the TU-Sofia course "Network Security in IoT- and Edge-based networks"

This project is made after the curriculum of the course and is designed to demonstrate the operation of virtual sensor devices and their operation inside a netowork with limited access, data processing through Node Red, as well as monitoring by Suricata, an IDS.

At this point in time the project only simulates the sensor (made with Python and paho-mqtt), Mosquitto for the MQTT broker and Node Red for logs.

To run the simulation, you'll need Docker and Docker Compose. Simply go into the directory of the project and run:
`docker compose up -d'

This will start up the simulated sensor, MQTT broker and Node Red. Node Red should be accessible on <device_ip_or_localhost>:1880