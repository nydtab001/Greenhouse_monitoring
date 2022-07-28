# Greenhouse Monitoring

The aim of this project was to implement an IoT environment logger for a greenhouse using a raspberry pi 3B+. The system collects various measurement data using analogue sensors at regular intervals. The data being collected for measrurement were light, temperature and humidity. the sensors used to collect these measurements interaacted with the raspberry pi through an ADC to convert the analogue sensor readings to values. In order to view these measurements remotely, Blynk(an IoT platform) was used to allow these mesurements to be monitored in real-time on an Android smartphone. An RTC was used to determine the intervals aat which measuremnets were taken and sent to the Blynk server.

## Features

* ability to change the frequency of monitoring on button press
* ability to start and sto monitoring on button press
* ability to view live logging information(system time and measurement values) locally and remotely though Blynk
* abilty to reset the timer
* signals an LED alarm when values are outside acceptaable thresholds
* alarm can be switched off on button press once triggered
