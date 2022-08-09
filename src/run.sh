gunicorn -c gconfig.py main:app && tail -F -n 100 /cabits/logs/cabits-converter-log-svr/server/cabits-converter-log-svr.log
