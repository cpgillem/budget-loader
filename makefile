activate:
	. venv/bin/activate

server_debug: activate
	flask --app src/server run --debug

server: activate
	gunicorn --bind 127.0.0.1:5009 wsgi:app