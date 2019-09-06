FROM python:3.6.9-slim
MAINTAINER "SBU BMI"

RUN apt-get update && \
	apt-get install -y git build-essential openslide-tools

WORKDIR /opt

RUN git clone https://github.com/choosehappy/HistoQC.git && \
    cd HistoQC && \
    pip3 install -r requirements.txt && \
	pip3 install pandas

WORKDIR /opt/HistoQC/
COPY quip_* /opt/HistoQC/ 
RUN  chmod 0755 quip_run_quality
ENV  PATH=.:/opt/HistoQC:$PATH

CMD ["./quip_run_quality","manifest.csv","input_images.tsv","results.tsv","config_first.ini"]

