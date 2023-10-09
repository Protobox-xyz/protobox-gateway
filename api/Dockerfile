FROM python:3.11

ENV PYTHONPATH /app
EXPOSE 8000

WORKDIR /app
COPY ./requirements.txt .

RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt

COPY . /app

CMD uvicorn app:app --host 0.0.0.0 --port 8000
