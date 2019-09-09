#!/bin/bash

sed -i 's/os.path.realpath/str/g' qc_pipeline.py
sed -i 's/os.path.normpath/str/g' qc_pipeline.py
