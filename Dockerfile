FROM node:18.15.0 as node
RUN mkdir /app
#copy all of the code
COPY *.py /app/
COPY www/ /app/www/
COPY IO/*.py /app/IO/
COPY Services/*.py /app/Services/
COPY lib/*.py /app/lib/
COPY data/*.json /app/data/
COPY Devices/*.py /app/Devices/

WORKDIR /app/www
RUN npm install
RUN npm run build --prod
#Set the directory that contains the built angular app
ENV STATIC_DIRECTORY=/app/www/dist/www


FROM arm32v7/python:3.10.10-slim AS BASE
EXPOSE 8080

RUN pip install --upgrade pip setuptools wheel

##############################################################
#Necessary for pillow (images for display)
##############################################################
RUN apt update
RUN apt -y install build-essential libwrap0-dev libssl-dev libc-ares-dev uuid-dev xsltproc
RUN apt-get update -qq \
    && apt-get install --no-install-recommends --yes \
        build-essential \
        gcc \
        python3-dev \
        mosquitto \
        mosquitto-clients
RUN apt-get update
RUN apt-get install libjpeg-dev -y
RUN apt-get install zlib1g-dev -y
RUN apt-get install libfreetype6-dev -y
#RUN apt-get install liblcms1-dev -y
RUN apt-get install libopenjp2-7 -y
RUN apt-get install libtiff5 -y
RUN apt-get install unzip


COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt



ENV DATA_PATH=/app/data/
ENV FONT_PATH=/app/www/fonts/
ENV ROOT_FOLDER=/app
#docker build -f "Dockerfile" . -t "pool-automation:latest"

RUN cd /app
#ENTRYPOINT ["tail", "-f", "/dev/null"]

ENTRYPOINT ["python3","-u","/app/startup.py"]