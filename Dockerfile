# pull official base image
FROM python:3.8
RUN mkdir /code
WORKDIR /code

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./service/requirements.txt /code/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
ADD app-entrypoint.sh /
RUN chmod +x /app-entrypoint.sh

ENTRYPOINT ["/app-entrypoint.sh"]
