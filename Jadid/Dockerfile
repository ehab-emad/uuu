FROM python:3.10

ENV DATABASE_HOST=""
ENV DATABASE_NAME=""
ENV DATABASE_USER=""
ENV DATABASE_PASS=""
ENV QLCA_URL="https://qlca.example.de"

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
# port where the Django app runs
EXPOSE 8000