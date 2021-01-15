FROM python:3.8.7-buster

WORKDIR /usr/src/app

COPY dashboard/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ ./

CMD ["gunicorn", "-c", "guniconf.py", "run:server"]
