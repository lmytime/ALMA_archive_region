import argparse
from astropy.coordinates import SkyCoord
import astropy.units as u
try:
    from astroquery.alma import Alma
except ImportError:
    print("Please install astroquery and astropy:")
    print("pip install astroquery astropy")
    exit(1)

def query_alma_archive(ra, dec, radius_deg):
    """
    Query the ALMA archive for observations around a specific coordinate.
    
    Args:
        ra (str/float): Right Ascension.
        dec (str/float): Declination.
        radius_deg (float): Search radius in degrees.
    """
    print(f"Searching ALMA archive around RA={ra}, Dec={dec} with radius={radius_deg} deg...")
    
    try:
        # Parse coordinates
        # SkyCoord is very flexible and can take strings like "12h34m56s -12d34m56s" or degrees
        if isinstance(ra, str) and ('h' in ra or ':' in ra):
            c = SkyCoord(ra, dec, frame='icrs')
        else:
            c = SkyCoord(ra, dec, unit=(u.deg, u.deg), frame='icrs')
    except Exception as e:
        print(f"Error parsing coordinates: {e}")
        return

    # Query the ALMA archive
    # ALMA query_region returns an astropy table
    try:
        results = Alma.query_region(c, radius=radius_deg * u.deg, public=None)
    except Exception as e:
        print(f"Error querying ALMA archive: {e}")
        return

    if results is None or len(results) == 0:
        print("No observations found in this region.")
        return

    # Save results to a file
    output_filename = "alma_query_results.csv"
    try:
        results.write(output_filename, format='csv', overwrite=True)
        print(f"\nSuccessfully saved all {len(results)} raw results to {output_filename}")
    except Exception as e:
        print(f"\nCould not save results to file: {e}")

    print(f"\nFound {len(results)} observations. Extracting core info...\n")
    
    # The ALMA archive table contains many columns. 's_region' usually specifies the spatial footprint in TAP.
    # Other common column names: 'proposal_id' (Project code), 'target_name'
    
    print(f"{'Project Code':<15} | {'Source Name':<20} | {'Band':<5} | {'Footprint (s_region)'}")
    print("-" * 100)
    
    for row in results:
        project_code = row['proposal_id'] if 'proposal_id' in row.colnames else (row['project_code'] if 'project_code' in row.colnames else 'N/A')
        source_name = row['target_name'] if 'target_name' in row.colnames else (row['source_name'] if 'source_name' in row.colnames else 'N/A')
        band_list = row['band_list'] if 'band_list' in row.colnames else 'N/A'
        footprint = row['s_region'] if 's_region' in row.colnames else (row['footprint'] if 'footprint' in row.colnames else 'N/A')
        
        # Truncate footprint string if it's too long
        footprint_str = str(footprint)
        if len(footprint_str) > 50:
            footprint_str = footprint_str[:47] + "..."
            
        print(f"{str(project_code):<15} | {str(source_name):<20} | {str(band_list):<5} | {footprint_str}")
        
    print(f"\nQuery complete. Full results saved to {output_filename}")
    print("Note: 's_region' or 'footprint' returns the polygon coordinates mapping the observation field.")

if __name__ == "__main__":
    print("=== ALMA Archive Footprint Query ===")
    ra_in = input("Enter Right Ascension (e.g., 266.4168 or '17h45m40s'): ")
    dec_in = input("Enter Declination (e.g., -29.0078 or '-29d00m28s'): ")
    rad_in = input("Enter Search Radius in degrees (e.g., 0.01): ")
    
    try:
        rad_val = float(rad_in)
        query_alma_archive(ra_in, dec_in, rad_val)
    except ValueError:
        print("Invalid radius. Please enter a numerical value for degrees.")
