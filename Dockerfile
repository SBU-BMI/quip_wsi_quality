FROM python:3.6.9-slim
MAINTAINER "SBU BMI"

RUN apt-get update
RUN apt-get install -y git build-essential openslide-tools

WORKDIR /opt

RUN git clone https://github.com/choosehappy/HistoQC.git && \
    cd HistoQC && \
    pip3 install -r requirements.txt

WORKDIR /opt/HistoQC/

ENTRYPOINT ["python","qc_pipeline.py"]

