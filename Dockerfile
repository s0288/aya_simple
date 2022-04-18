FROM python:3.9.7-slim

WORKDIR '/app'

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# set time zone
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# mount relevant directories
COPY ./src .

CMD python run_telegram.py