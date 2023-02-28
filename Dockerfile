FROM arm32v7/python:3.10.10-slim AS BASE
RUN pip install duckdb

EXPOSE 8080

RUN pip install --upgrade pip setuptools wheel
#RUN python3 -m pip install Cmake

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

RUN pip install CherryPy==18.6.1 
RUN pip install dataclasses_json==0.5.7
RUN pip install dataclass_wizard==0.22.2
RUN pip install dataclasses==0.6
RUN pip install smbus2==0.4.2
RUN pip install adafruit-circuitpython-ssd1306==2.12.12
RUN pip install board==1.0
RUN pip install pillow==9.4.0
RUN pip install duckdb
#RUN pip install odata-query==2.8.2

#No package available for odata, so we must manually build it
ADD https://files.pythonhosted.org/packages/74/a2/8d6f309aecc294888f4d9fe9de3c158f5a5cc76118573ccd5f0663bf092f/odata_query-0.8.1-py3-none-any.whl /odata/odata_query-0.8.1-py3-none-any.whl
RUN pip install /odata/odata_query-0.8.1-py3-none-any.whl

#Duckdb CLI
#ADD https://github.com/duckdb/duckdb/releases/download/v0.7.0/duckdb_cli-linux-rpi.zip /duckdb/duckdb_cli-linux-rpi.zip
#RUN unzip /duckdb/duckdb_cli-linux-rpi.zip -d /duckdb/duckdb_cli
#ADD https://github.com/duckdb/duckdb/archive/refs/heads/master.zip /duckdb/master.zip
#RUN unzip /duckdb/master.zip -d /duckdb/
#RUN cd /duckdb/master/tools/pythonpkg
#RUN python3 setup.py install
#RUN cd /

RUN mkdir /app

#copy all of the code
COPY *.py /app/
COPY www/ /app/www/
COPY IO/*.py /app/IO/
COPY Services/*.py /app/Services/
COPY lib/*.py /app/lib/
COPY data/*.json /app/data/
COPY Devices/*.py /app/Devices/

#docker build -f "Dockerfile" . -t "pool-automation:latest"

ENTRYPOINT ["tail", "-f", "/dev/null"]

#ENTRYPOINT ["python3","-u","/app/startup.py"]