import sys
import pandas as pd

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

