FROM python:latest
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

EXPOSE 5000
ENV FLASK_APP conscience.py
RUN flask initdb
ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]
