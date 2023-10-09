FROM python:3.11

ENV PYTHONPATH /app
EXPOSE 8000

WORKDIR /app
ADD ./requirements.txt .

RUN pip install -r requirements.txt

ADD . /app

CMD uvicorn app:app --host 0.0.0.0 --port 8000
