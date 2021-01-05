FROM python:3.8.7-alpine3.12

WORKDIR /usr/src/app

COPY dashboard/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ ./

ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

CMD ["flask", "run"]