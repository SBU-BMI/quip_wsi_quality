# quip_wsi_quality
Docker image for WSI quality control using HistoQC (https://github.com/choosehappy/HistoQC). 

The docker container can be built as follows:

docker build -t quip_wsi_quality . 

The container can be run as follows: 

docker run --rm --name wsi-quality -v <path-to-images>:/data/images -v <output-folder>:/data/output -d quip_wsi_quality run_quality /data/images/manifest.tsv

manifest.tsv contains the list of images in /data/images to be processed. 

