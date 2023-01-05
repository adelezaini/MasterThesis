########## Code inspired by Astrid BG ############
import numpy as np
import xarray as xr
import sys; sys.path.append("..")
from dataset_manipulation.postprocess import *

"""
Example usage:
python3 postprocess.py casename casealias component history_field

python3 postprocess.py IDEAL-ON_2000_sec_nudg_f19_f19 IDEAL-ON atm h0
"""

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Path to import and export
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

raw_path = '../../../archive/' #Betzy: /cluster/home/adelez/nird/ #Nird: /nird/home/adelez/storage/
processed_path = '../../processed-data/postprocessing/'

#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Import, fix units and names, apply Ghan's scomposition, save processed ds
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def main(casename, casealias, component, history_field='h0'):#, startyear, endyear, var,history_field='h2',postfix='',path=path_to_noresm_archive, output_path=outpath_default):
    
    ds = create_dataset(raw_path, casename, component, pressure_vars=True)
    ds = fix_names(fix_units(ds))
    ds = aerosol_cloud_forcing_scomposition_Ghan(ds)
    save_postprocessed(ds, component, processed_path, casealias)
    
#––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
if __name__ == '__main__':
    import sys

    args = sys.argv
    main(*args[1:])
