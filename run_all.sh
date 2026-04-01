#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "========================================================"
echo "Step 1: Querying the ALMA archive"
echo "Target coordinates: RA = 53.154958, Dec = -27.815844"
echo "Search radius: 0.0001 degrees"
echo "========================================================"

# We use a heredoc (<<EOF) to automatically feed the inputs 
# to the interactive prompt of search_alma.py
python search_alma.py <<EOF
53.15495833333333
-27.815844444444444
0.0001
EOF

echo ""
echo "========================================================"
echo "Step 2: Converting CSV output to DS9 region file"
echo "========================================================"

python csv_to_ds9.py -i alma_query_results.csv -o alma_regions.reg

echo ""
echo "All done! You can now open your FITS file in DS9 and load 'alma_regions.reg'."
