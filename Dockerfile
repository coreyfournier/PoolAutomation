FROM node:20.5-slim AS NODE_BASE
#Only copy over the packages so we don't change the layer unless the packages change.
WORKDIR /app
COPY www/package.json package.json
COPY www/package-lock.json package-lock.json
ENV NODE_PATH=/node_modules
#Disable the progress bar to hopefully decrease build times
RUN npm set progress=false
#Perform a clean install from the lock file
RUN npm ci
#Get all of the angular files so it will be ready to build
COPY www/ /app

#Create a new layer that is only for the final build that very light weight
FROM node_base AS NODE_FINAL
WORKDIR /app
RUN npm run build --prod
#remove all of the node modules as it's no longer need in the final layer. This makes the file really small.
RUN rm -r /app/node_modules

FROM arm32v7/python:3.10.10-slim AS PYTHON_BASE
WORKDIR /app/
RUN pip install --upgrade pip setuptools wheel

RUN apt update
RUN apt-get -y install cmake
##############################################################
#Necessary for pillow (images for display)
##############################################################
RUN apt -y install build-essential libwrap0-dev libssl-dev libc-ares-dev uuid-dev xsltproc
RUN apt-get update -qq \
    && apt-get install --no-install-recommends --yes \
        build-essential \
        gcc \
        python3-dev \
        mosquitto \
        mosquitto-clients
RUN apt-get install libjpeg-dev -y
RUN apt-get install zlib1g-dev -y
RUN apt-get install libfreetype6-dev -y
RUN apt-get install libopenjp2-7 -y
RUN apt-get install libtiff5 -y
RUN apt-get install unzip

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY --from=NODE_FINAL /app /app/www
#Set the directory that contains the built angular app
ENV STATIC_DIRECTORY=/app/www/dist/www

#copy all of the code
COPY *.py /app/

COPY IO/*.py /app/IO/
COPY Services/*.py /app/Services/
COPY lib/*.py /app/lib/
COPY data/*.json /app/data/
COPY Devices/*.py /app/Devices/
COPY Plugins/*.py /app/Plugins/

EXPOSE 8080

ENV NODE_PATH=/packages/node_modules
ENV DATA_PATH=/app/data/
ENV FONT_PATH=/app/www/fonts/
ENV ROOT_FOLDER=/app

RUN cd /app
#Use for troubleshooting
#ENTRYPOINT ["tail", "-f", "/dev/null"]

ENTRYPOINT ["python3","-u","/app/startup.py"]