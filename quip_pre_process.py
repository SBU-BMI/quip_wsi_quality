import sys
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Convert WSI images to multires, tiff images.")
parser.add_argument("--inpmeta",nargs="?",default="quip_manifest.csv",type=str,help="input manifest (metadata) file.")
parser.add_argument("--errfile",nargs="?",default="quip_wsi_error_log.json",type=str,help="error log file.")
parser.add_argument("--inpdir",nargs="?",default="/data/images",type=str,help="input folder.")
parser.add_argument("--outdir",nargs="?",default="/data/output",type=str,help="output folder.")

def main(argv):
    inp_folder = "/data/images/"
    out_folder = "/data/output/"
    inp_manifest = "manifest.csv"
    out_images_tsv = "input_images.tsv"
    if len(argv)==1:
       inp_manifest = argv[0]
    if len(argv)==2:
       inp_manifest = argv[0]
       out_images_tsv = argv[1]

    inp_file = open(inp_folder + "/" + inp_manifest);
    pf = pd.read_csv(inp_file,sep=',')
    if "path" not in pf.columns:
        print("ERROR: Header is missing in file: ",inp_manifest)
        inp_file.close()
        sys.exit(1);

    out_tsv  = open(out_folder + "/" + out_images_tsv,"w");
    pf["path"].to_csv(out_tsv,index=False,header=False);

    inp_file.close();
    out_tsv.close();
    sys.exit(0);

if __name__ == "__main__":
   main(sys.argv[1:])

