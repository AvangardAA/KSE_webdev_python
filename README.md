## Project description

My project topic is cryptocurrency data aggregator, for its implementation here Django and Nodejs are used.
Django serves as a web-server which handles user interaction, database operations and channel with microservice.
Nodejs here is used to implement standalone microservice functionality, it receives data from Django and processes it, then communicates with database.

# Installation:

As my PC is Linux-based (Ubuntu), there is a path to correctly install this app.
```
sudo apt install npm
sudo npm install -g n
sudo n 16
```
Listed requirements are for node, then you must have Python version 3.10+.
Inside root of this project you should:
```
sudo apt install python3-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
After that you will have run-ready environment for this project.

# Execution:

To correctly run this project you should go from root directory to:
```
cd webdevkse
```
And execute server startup (Important! Make sure you are inside activated python Venv, we activated it before):
```
python3 manage.py runserver
```
Wait a little bit, then open another terminal window and go for:
```
cd webdevkse/nodejs/
npm install
```
After that you will have ready to-go nodejs service, run it with:
```
n use 16 index.js
```
> Important comment: execution showed above is recommended, because application requires node version 16+

Great, now you have a fully working application, log files are located in
```
rootdir/webdev/webdev/nodejs/logs/ws_service.log - for Nodejs
rootdir/webdev/python_logs.log - for Django
```
## Application usage:

To begin with application, visit in your browser http://localhost:8000/

This application is single-page, so everything user-oriented located here.
