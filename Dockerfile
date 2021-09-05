FROM python:3.8
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=works.settings
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/