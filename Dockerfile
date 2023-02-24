FROM python:3.9.10-buster

COPY . /project
WORKDIR /project

RUN python3.9 -m pip install -r requirements.txt 

CMD [ "python", "./__main__.py" ]
