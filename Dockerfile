FROM node:20.5-slim AS NODE_BASE
#Only copy over the packages so we don't change the layer unless the packages change.
COPY www/package-lock.json /app/www/package-lock.json
COPY www/package.json /app/www/package.json
WORKDIR /app/www
#Disable the progress bar to hopefully decrease build times
RUN npm set progress=false
RUN npm install -g modclean
RUN npm install-clean
#Try to reduce the size of the node modules
RUN modclean -n default:safe -r

#Now build the application
COPY www/ /app/www/
RUN npm run build --prod

FROM arm32v7/python:3.10.10-slim AS PYTHON_BASE
WORKDIR /app/
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
RUN apt-get install libjpeg-dev -y
RUN apt-get install zlib1g-dev -y
RUN apt-get install libfreetype6-dev -y
#RUN apt-get install liblcms1-dev -y
RUN apt-get install libopenjp2-7 -y
RUN apt-get install libtiff5 -y
RUN apt-get install unzip

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY --from=NODE_BASE /app/www /app/www
#Set the directory that contains the built angular app
ENV STATIC_DIRECTORY=/app/www/dist/www

#copy all of the code
COPY *.py /app/

COPY IO/*.py /app/IO/
COPY Services/*.py /app/Services/
COPY lib/*.py /app/lib/
COPY data/*.json /app/data/
COPY Devices/*.py /app/Devices/

EXPOSE 8080

ENV DATA_PATH=/app/data/
ENV FONT_PATH=/app/www/fonts/
ENV ROOT_FOLDER=/app
#docker build -f "Dockerfile" . -t "pool-automation:latest"

RUN cd /app
#Use for troubleshooting
#ENTRYPOINT ["tail", "-f", "/dev/null"]

ENTRYPOINT ["python3","-u","/app/startup.py"]