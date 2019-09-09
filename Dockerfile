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
ENV  PATH=.:/opt/HistoQC:$PATH
COPY quip_* /opt/HistoQC/ 
COPY run_*  /opt/HistoQC/ 
RUN  chmod 0755 run_quip_quality run_histoqc_update.sh && \
	 run_histoqc_update.sh 

CMD ["run_quip_quality"]

