import sys
import pandas as pd

def main(argv):
    inp_folder = "/data/images/"
    out_folder = "/data/output/"
    inp_manifest = "manifest.csv"
    inp_results  = "results.tsv"
    if len(argv)==1:
       inp_manifest = argv[0]
    if len(argv)==2:
       inp_manifest = argv[0]
       inp_results  = argv[1]
    out_manifest = inp_manifest

    inp_file = open(inp_folder + "/" + inp_manifest);
    pf_manifest = pd.read_csv(inp_file,sep=',')
    if "path" not in pf_manifest.columns:
        print("ERROR: Header is missing in file: ",inp_manifest)
        inp_file.close()
        sys.exit(1);

    inp_rslt = open(out_folder + "/" + inp_results);
    dst = 0
    c_result  = None
    pf_result = None
    for x in inp_rslt:
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

    inp_file.close();
    inp_rslt.close();
    out_csv.close();
    sys.exit(0);

if __name__ == "__main__":
   main(sys.argv[1:])

