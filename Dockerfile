#The angular output is plain html/js, so build it on the machine doing the build instead of emulating the pi
FROM --platform=$BUILDPLATFORM node:20.5.0-slim AS node_base
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
FROM node_base AS node_final
WORKDIR /app

RUN npm run build -- --configuration production
#remove all of the node modules as it's no longer need in the final layer. This makes the file really small.
RUN rm -r /app/node_modules

##############################################################
#Compiles the python packages. The compilers stay in this stage and never reach the pi.
##############################################################
FROM python:3.13-slim AS python_build
#The -dev packages are the headers pillow needs to build with jpeg, png and font support (images for the display)
RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
        build-essential \
        cmake \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

#Slow packages first, in their own layer, so a change to requirements.txt doesn't recompile them
COPY requirements-compiled.txt /app/
RUN pip install --no-cache-dir -r /app/requirements-compiled.txt

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

##############################################################
#What runs on the pi
##############################################################
FROM python:3.13-slim AS python_base
WORKDIR /app/
#Libraries pillow links against at runtime. These match the -dev packages in python_build.
RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
        libjpeg62-turbo \
        zlib1g \
        libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python_build /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY --from=node_final /app /app/www
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
COPY Events/*.py /app/Events/

EXPOSE 8080

ENV NODE_PATH=/packages/node_modules
ENV DATA_PATH=/app/data/
ENV FONT_PATH=/app/www/fonts/
ENV ROOT_FOLDER=/app

RUN cd /app
#Use for troubleshooting
#ENTRYPOINT ["tail", "-f", "/dev/null"]

ENTRYPOINT ["python3","-u","/app/startup.py"]