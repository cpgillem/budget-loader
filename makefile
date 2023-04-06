server_debug:
	flask --app src/server run --debug

server:
	gunicorn --bind 127.0.0.1:5009 wsgi:app