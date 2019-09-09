import sys
import pandas as pd
import argparse
import uuid
import subprocess

parser = argparse.ArgumentParser(description="Convert WSI images to multires, tiff images.")
parser.add_argument("--inpmeta",nargs="?",default="quip_manifest.csv",type=str,help="input manifest (metadata) file.")
parser.add_argument("--outmeta",nargs="?",default="quip_manifest.csv",type=str,help="output manifest (metadata) file.")
parser.add_argument("--errfile",nargs="?",default="quip_wsi_error_log.json",type=str,help="error log file.")
parser.add_argument("--cfgfile",nargs="?",default="config_first.ini",type=str,help="HistoQC config file.")
parser.add_argument("--inpdir",nargs="?",default="/data/images",type=str,help="input folder.")
parser.add_argument("--outdir",nargs="?",default="/data/output",type=str,help="output folder.")

def main(args):
    inp_folder = args.inpdir 
    out_folder = args.outdir 
    inp_manifest_fname = args.inpmeta
    out_manifest_fname = args.outmeta
    out_error_fname = args.errfile 

    # HistoQC related files
    images_tmp_fname  = str(uuid.uuid1())+".tsv"
    histoqc_results_fname = "results.tsv"
    histoqc_config_fname = args.cfgfile

    out_error_fd = open(out_folder + "/" + out_error_fname,"w");
    all_log = {}
    all_log["error"] = []
    all_log["warning"] = [] 
    try:
        inp_metadata_fd = open(inp_folder + "/" + inp_manifest_fname);
    except OSError:
        ierr = {}
        ierr["error_code"] = 1
        ierr["error_msg"] = "missing manifest file: " + str(inp_manifest_fname);
        all_log["error"].append(ierr)
        json.dump(all_log,out_error_fd)
        out_error_fd.close()
        sys.exit(1)

    pf = pd.read_csv(inp_metadata_fd,sep=',')
    if "path" not in pf.columns:
        ierr = {}
        ierr["error_code"] = 2
        ierr["error_msg"] = "column path is missing."
        all_log["error"].append(ierr)
        json.dump(all_log,out_error_fd)
        out_error_fd.close()
        inp_metadata_fd.close() 
        sys.exit(1)

    if "file_uuid" not in pf.columns:
        iwarn = {}
        iwarn["warning_code"] = 1
        iwarn["warning_msg"] = "column file_uuid is missing. Will generate."
        all_log["warning"].append(iwarn)
        fp["file_uuid"] = "" 
        for idx, row in pf.iterrows(): 
            filename, file_extension = path.splitext(row["path"]) 
            pf.at[idx,"file_uuid"] = str(uuid.uuid1()) + file_extension

    if "row_status" not in pf.columns:
        iwarn = {}
        iwarn["warning_code"] = 3
        iwarn["warning_msg"] = "column row_status is missing. Will generate."
        all_log["warning"].append(iwarn)
        fp["row_status"] = "ok"

    # Pre-processing: create input manifest file for HistoQC
    images_tmp_fd  = open(out_folder + "/" + images_tmp_fname,"w");
    pf["path"].to_csv(images_tmp_fd,index=False,header=False);
    images_tmp_fd.close()

    # Execute HistoQC process
    histoqc_log_fname = str(uuid.uuid1())+"-histoqc.log"
    cmd = "python qc_pipeline.py -s --force"
    cmd = cmd + "-o " + out_folder 
    cmd = cmd + "-p " + inp_folder 
    cmd = cmd + "-c " + histoqc_config_fname 
    cmd = cmd + out_folder + "/" + images_tmp_fname 
    cmd = cmd + ">" + histoqc_log_fname + "2>&1"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    if process.returncode != 0:
        ierr = {}
        ierr["error_code"] = process.returncode
        ierr["error_msg"] = "HistoQC error."
        all_log["error"].append(ierr)
 

    # Post-process: 
    histoqc_results_fd = open(out_folder + "/" + histoqc_results_fname);
    dst = 0
    c_result  = None
    pf_result = None
    for x in histoqc_results_fd:
        if dst==0:
           a = x.split(':')
           if a[0]=='#dataset':
              dst=1
              a[1] = a[1].replace("\n","")
              c_result = a[1].split('\t')
              pf_result = pd.DataFrame(columns=c_result)
        else:
           a = x.replace("\n","")
           pt = pd.DataFrame([a.split("\t")],columns=c_result)
           pf_result = pf_result.append(pt,ignore_index=True)

    pf_output = pd.merge(pf_manifest,pf_result,how='inner', left_on=['path'], right_on=['filename'])
    out_csv  = open(out_folder + "/" + out_manifest,"w");
    pf_output.to_csv(out_csv,index=False)

if __name__ == "__main__":
   main(sys.argv[1:])

