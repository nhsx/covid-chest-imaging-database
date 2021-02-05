bind = "%s:%s" % ("0.0.0.0", 80)

workers = 1
worker_class = "gthread"
threads = 4
timeout = 30

daemon = False

errorlog = "-"
loglevel = "info"
accesslog = "-"
capture_output = False
