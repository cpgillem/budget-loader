SHELL := /bin/bash

build:
	cp node_modules/bootstrap/dist/css/bootstrap.css budgetloader/static/bootstrap.css
	cp node_modules/bootstrap/dist/js/bootstrap.js budgetloader/static/bootstrap.js

env:
	source .env

debug: build env
	venv/bin/flask --app budgetloader run --debug --port=5009

server: build env
	venv/bin/gunicorn --bind 127.0.0.1:5009 wsgi:app