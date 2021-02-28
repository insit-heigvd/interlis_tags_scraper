#!/bin/bash

python3 ${HOME}/interlis_tag_scraping.py

echo "Job finished successfully!"
echo "Number of tags found per file:"
find ./output/*/ -type f -iname '*.ili.csv' -exec sh -c 'printf "%s %s\n" "$(tail -n +2 "${1}" | wc -l)" "${1}"' sh1 {} \;

cd output && awk -v OFS=';' ' NR==1 {print $0, "filename"}  FNR==1 {next} {print $0, FILENAME} ' */*.csv > merged.csv

echo "Merged all single files into 'merged.csv' successfully!"
echo "Number of tags in 'merged.csv' file:"
tail -n +2 `find ./ -name 'merged.csv'` | wc -l



