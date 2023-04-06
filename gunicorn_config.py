import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = '127.0.0.1:5009'
umask = 0o007
reload = True

accesslog = '-'
errorlog = '-'