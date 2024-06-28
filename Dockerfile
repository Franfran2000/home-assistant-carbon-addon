FROM python:latest

COPY src /src

WORKDIR /src

RUN pip install -r requirements.txt

#CMD [ "ls" ]

CMD [ "python", "main.py" ]