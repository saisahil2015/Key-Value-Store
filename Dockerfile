# start by pulling the python image
FROM python:3.10-alpine

# copy the requirements and server file into the image
COPY ./requirements.txt /app/requirements.txt
COPY ./server.py /app/server.py


# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

EXPOSE 80

CMD ["gunicorn", "server:app", "-b", "0.0.0.0:80"]

