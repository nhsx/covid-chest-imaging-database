FROM python:3.8.7-buster

WORKDIR /usr/src/app

COPY dashboard/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ ./

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:80 --workers=1"

CMD ["gunicorn", "run:server"]
