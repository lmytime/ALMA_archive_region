import csv
import re
import argparse
import sys

def parse_s_region(s_region_str, target_name, color="red"):
    """
    Parse the ADQL s_region string into a list of DS9 region strings.
    Handles multiple geometries like 'Union Polygon ... Polygon ...'
    """
    if not s_region_str or str(s_region_str).strip() == '' or str(s_region_str).lower() in ('na', 'n/a'):
        return []

    regions = []
    # Split the string by 'Polygon' or 'Circle' (case-insensitive) to handle unions
    tokens = re.split(r'(?i)\b(polygon|circle)\b', str(s_region_str))
    
    current_geom = None
    for token in tokens:
        token_lower = token.strip().lower()
        if token_lower in ('polygon', 'circle'):
            current_geom = token_lower
        elif current_geom:
            # Extract coordinates for the previously matched geometry
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', token)
            if current_geom == 'polygon' and len(numbers) >= 6: # At least 3 points (RA, Dec pairs)
                coords = ','.join(numbers)
                regions.append(f"polygon({coords}) # color={color} text={{{target_name}}}")
            elif current_geom == 'circle' and len(numbers) >= 3:
                # circle is usually center_ra, center_dec, radius
                regions.append(f"circle({numbers[0]},{numbers[1]},{numbers[2]}) # color={color} text={{{target_name}}}")
            
            # Reset current geometry after processing its numbers
            current_geom = None
            
    return regions

def convert_csv_to_ds9(input_csv, output_reg):
    try:
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Determine the correct column names based on the CSV headers
            headers = reader.fieldnames
            s_region_col = 's_region' if 's_region' in headers else ('footprint' if 'footprint' in headers else None)
            target_col = 'target_name' if 'target_name' in headers else ('source_name' if 'source_name' in headers else None)
            
            if not s_region_col:
                print("Error: Could not find 's_region' or 'footprint' column in the CSV.")
                return
            
            regions = []
            for row in reader:
                s_region = row.get(s_region_col, '')
                target_name = row.get(target_col, 'Unknown')
                
                # Get a list of regions for this row
                ds9_regs = parse_s_region(s_region, target_name)
                regions.extend(ds9_regs)
                    
        if not regions:
            print("No valid spatial regions found to convert.")
            return
            
        # Write to region file
        with open(output_reg, 'w', encoding='utf-8') as f:
            f.write("# Region file format: DS9 version 4.1\n")
            f.write("global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n")
            f.write("fk5\n") # Assume coords are ICRS/J2000 which is roughly fk5
            for reg in regions:
                f.write(f"{reg}\n")
                
        print(f"Successfully converted {len(regions)} regions into {output_reg}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_csv}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert ALMA CSV results to DS9 region file.")
    parser.add_argument('-i', '--input', default='alma_query_results.csv', help='Input CSV file (default: alma_query_results.csv)')
    parser.add_argument('-o', '--output', default='alma_regions.reg', help='Output DS9 region file (default: alma_regions.reg)')
    
    args = parser.parse_args()
    
    convert_csv_to_ds9(args.input, args.output)