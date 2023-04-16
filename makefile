SHELL := /bin/bash

include .env
export $(shell sed 's/=.*//' .env)

build:
	cp node_modules/bootstrap/dist/css/bootstrap.css budgetloader/static/bootstrap.css
	cp node_modules/bootstrap/dist/js/bootstrap.js budgetloader/static/bootstrap.js

debug: build
	venv/bin/flask --app budgetloader run --debug --port=5009

server: build
	venv/bin/gunicorn --bind 127.0.0.1:5009 wsgi:app
