import sys
import pandas as pd
import argparse
import uuid
import subprocess

error_info = {}
error_info["no_error"] = { "code":"0", "msg":"no-error" }
error_info["missing_file"] = { "code":"401", "msg":"input-file-missing" }
error_info["file_format"] = { "code":"402", "msg":"file-format-error" }
error_info["missing_columns"] = { "code":"403", "msg":"missing-columns" }
error_info["showinf_failed"] = { "code":"404", "msg":"showinf-failed" }
error_info["fconvert_failed"] = { "code":"405", "msg":"fconvert-failed" }
error_info["vips_failed"] = { "code":"406", "msg":"vips-failed" }

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
        ierr = error_info["missing_file"]
        ierr["msg"] = ierr["msg"]+": " + str(inp_manifest_fname);
        all_log["error"].append(ierr)
        json.dump(all_log,out_error_fd)
        out_error_fd.close()
        sys.exit(1)

    pf = pd.read_csv(inp_metadata_fd,sep=',')
    if "path" not in pf.columns:
        ierr = error_info["missing_columns"]
        ierr["msg"] = ierr["msg"]+ ": "+ "path."
        all_log["error"].append(ierr)
        json.dump(all_log,out_error_fd)
        out_error_fd.close()
        inp_metadata_fd.close() 
        sys.exit(1)

    if "file_uuid" not in pf.columns:
        iwarn = error_info["missing_columns"]
        iwarn["msg"] = iwarn["msg"]+": "+"file_uuid. Will generate."
        all_log["warning"].append(iwarn)
        fp["file_uuid"] = "" 
        for idx, row in pf.iterrows(): 
            filename, file_extension = path.splitext(row["path"]) 
            pf.at[idx,"file_uuid"] = str(uuid.uuid1()) + file_extension
            
    if "error_code" not in pf.columns:
        iwarn = error_info["missing_columns"]
        iwarn["msg"] = iwarn["msg"]+": "+"error_code. Will generate."
        all_log["warning"].append(iwarn)
        fp["error_code"] = error_info["no_error"]["code"] 

    if "error_msg" not in pf.columns:
        iwarn = error_info["missing_columns"]
        iwarn["msg"] = iwarn["msg"]+": "+"error_msg. Will generate."
        all_log["warning"].append(iwarn)
        fp["error_msg"] = error_info["no_error"]["msg"] 

    # Pre-processing: create input manifest file for HistoQC
    folder_uuid = out_folder + "/" + "images-" + str(uuid.uuid1());  
    os.makedirs(folder_uuid);
    images_tmp_fd  = open(out_folder + "/" + images_tmp_fname,"w");
    for idx, row in pf.iterrows():
        os.symlink(inp_folder+"/"+row["path"],folder_uuid+"/"+row["file_uuid"])
        images_tmp_fd.write(folder_uuid+"/"+row["file_uuid"]);
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
        ierr["code"] = str(process.returncode)
        ierr["msg"]  = "HistoQC error."
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

    pf_output = pd.merge(pf_manifest,pf_result,how='inner', left_on=['file_uuid'], right_on=['filename'])
    out_csv  = open(out_folder + "/" + out_manifest,"w");
    pf_output.to_csv(out_csv,index=False)

if __name__ == "__main__": 
    args = parser.parse_args(sys.argv[1:]); 
    main(args)

