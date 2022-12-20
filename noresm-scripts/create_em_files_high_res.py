from subprocess import run
import numpy as np
import pathlib
from pathlib import Path

# Default settings

path_to_noresm_archive = '/cluster/home/adelez/storage/archive' #'/proj/bolinc/users/x_sarbl/noresm_archive'
outpath_default = '/cluster/home/adelez/noresm-inputdata' #'/proj/bolinc/users/x_sarbl/noresm_input_data'

# How to load nco on your system
load_nco_string = 'module load NCO/5.0.3-intel-2021b' #module load NCO/4.6.3-nsc1'

"""
Example usage: 
python create_em_files_high_res.py case_name 2015 2018 SFisoprene h2 /proj/bolinc/users/x_sarbl/noresm_archive /proj/bolinc/users/x_sarbl/noresm_input_data 

python3 create_em_files_high_res.py CTRL_2000_sec_nudg_f19_f19 2007 2012 [SFisoprene/SFmonoterp
] h1 /cluster/home/adelez/storage/archive /cluster/home/adelez/noresm-inputdata 
"""

Av = 6.022e23  # Avogadro's number
M_iso = 68.114200e-3  # Molar mass isoprene kg/mol
M_mono = 136.228400e-3  # Molar mass monoterpene kg/mol
path_this_file = str(pathlib.Path().absolute())

var_dic = dict(SFmonoterp='H10H16',
               SFisoprene='ISOP')
M_dic = dict(SFmonoterp=M_mono,
             SFisoprene=M_iso)


# %%
def main(case_name, startyear, endyear, var,
         history_field='h1',
         postfix='',
         path=path_to_noresm_archive,
         output_path=outpath_default
         ):
    path = Path(path)
    # %%
    path = Path(path)
    output_path = Path(output_path)
    # %%
    input_path = path / case_name / 'atm' / 'hist'
    startyear = int(startyear)
    endyear = int(endyear)
    # %%
    # Av = 6.022e23  # Avogadro's number
    # M_iso=68.114200e-3 #Molar mass isoprene kg/mol
    # M_mono=136.228400e-3 #Molar mass monoterpene kg/mol
    # %%
    comms = []

    for y in range(startyear, endyear + 1):
        print(y)
        filenames = str(input_path) + f'/{case_name}.cam.{history_field}.{y:04.0f}*.nc'
        print(filenames)
        outfile = output_path / f'tmp_{case_name}_{y:04.0f}_{var}.nc'
        # Creating yearly files of emissions
        co = f'ncrcat -O -v date,datesec,{var} {filenames} {outfile}'

        comms.append(co)
    # %%
    for y in range(startyear, endyear + 1):
        if y in np.arange(0, 2100, 4):
            print(f'{y} is leap year')
            outfile = output_path / f'tmp_{case_name}_{y:04.0f}_{var}.nc'
            tmpfile = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp.nc'
            tmpfile_slice1 = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp_slice1.nc'
            tmpfile_slice2 = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp_slice2.nc'
            tmpfile_slice3 = output_path / f'tmp_{case_name}_{y:04.0f}_{var}_tmp_slice3.nc'

            co = f'mv {outfile} {tmpfile}'
            comms.append(co)
            # pick out times until 28 feb
            co = f'ncks -O -F -d time,1,2832 {tmpfile} {tmpfile_slice1}'
            comms.append(co)
            # pick out times after 1 march
            co = f'ncks -O -F -d time,2881,17568 {tmpfile} {tmpfile_slice2}'
            comms.append(co)
            # Remove day in time array
            co = f'ncap2  -O -s "time=time-1."  {tmpfile_slice2}  {tmpfile_slice3}'
            comms.append(co)
            # Concartinate files
            co = f'ncrcat -O {tmpfile_slice1} {tmpfile_slice3} {tmpfile}'
            comms.append(co)

            co = f'mv {tmpfile} {outfile}'
            comms.append(co)

    # %%
    infiles = str(output_path) + f'/tmp_{case_name}_*_{var}.nc'
    outfile = output_path / f'avg_{case_name}_{startyear}-{endyear}_{var}.nc'

    # Creating emission output file with averaged emissions
    co = f'ncea -O {infiles} {outfile}'
    comms.append(co)

    # %%
    # #Change year of date in emission file to 2000 different months have different dates and requires different corrections
    # Change format:
    co = f'ncks -3 -O {outfile} {outfile}'
    comms.append(co)

    new_var = var_dic[var]
    M_var = M_dic[var]
    # Calculate emissions in molec/cm2/s
    co = f'ncap2 -A -O -s "{new_var}={var}*{Av}/{M_var}*1e-4" {outfile}'
    comms.append(co)
    # %%
    diff = (startyear - 2000) * 10000
    # Change date to 2000
    if diff > 0:
        co = f'ncap2 -A -O -s "date=date-{diff}."  {outfile}'
    else:
        co = f'ncap2 -A -O -s "date=date+{-diff}."  {outfile}'
    comms.append(co)

    # change units:
    co = f'ncatted -a units,{new_var},o,c,molecules/cm2/s {outfile}'
    comms.append(co)
    co = f'ncatted -a units,time,o,c,"days since 2000-01-01 00:00:00" {outfile}'
    comms.append(co)
    # Save date and new var to new file
    final_file = output_path / f'ems_{case_name}_{startyear}-{endyear}_{var}{postfix}.nc'
    co = f'ncks -O -v date,{new_var},datesec {outfile} {final_file}'
    comms.append(co)
    # Run all commands
    for co in comms:
        print(co)
        run(f'{load_nco_string} &&' + co, shell=True)
        # txt = input("Type something to test this out: ")

        # print(f"Is this what you just said? {txt}")
    # Finally add extra days:
    comms = add_extra_day(case_name,
                          startyear, endyear, output_path, var,
                          postfix)
    for co in comms:
        print(co)
        run(f'{load_nco_string} &&' + co, shell=True)


def add_extra_day(case_name,
                  startyear, endyear, output_path, var,
                  postfix):
    """
    Copies 28th feb and inserts as 29th feb
    :param case_name:
    :param startyear:
    :param endyear:
    :param output_path:
    :param var:
    :param postfix:
    :return:
    """
    print('hey')
    """
    ds = xr.open_dataset(file_in, decode_cf=False)
    ds_last_day = ds.isel(time=slice(-48,None))
    ds_last_day['time'] =ds_last_day['time'] + 1
    ds_concat = xr.concat([ds, ds_last_day], dim='time')
    ds_concat.to_netcdf(file_out)
    """

    comms = []
    infile = output_path / f'ems_{case_name}_{startyear}-{endyear}_{var}{postfix}.nc'
    final_file = output_path / f'ems_{case_name}_{startyear}-{endyear}_{var}{postfix}_addleapyear.nc'

    tmpfile_slice1 = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp_slice1.nc'
    tmpfile_slice2 = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp_slice2.nc'
    tmpfile_slice3 = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp_slice3.nc'
    tmpfile = output_path / f'tmp_{case_name}_{startyear}-{endyear}_{var}_tmp.nc'

    co = f'ncks -O -F -d time,1,2832 {infile} {tmpfile_slice1}'
    comms.append(co)
    co = f'ncks -O -F -d time,2833,17520 {infile} {tmpfile_slice2}'
    comms.append(co)
    co = f'ncap2  -O -s "time=time+1."  {tmpfile_slice2}  {tmpfile_slice2}'
    comms.append(co)

    co = f'ncks -O -F -d time,2833,2881 {infile} {tmpfile_slice3}'
    comms.append(co)
    co = f'ncap2  -O -s "date=date-301+229"  {tmpfile_slice3}  {tmpfile_slice3}'

    comms.append(co)

    co = f'ncrcat -O {tmpfile_slice1} {tmpfile_slice3} {tmpfile_slice2} {final_file}'
    comms.append(co)

    return comms


# %%
if __name__ == '__main__':
    import sys

    args = sys.argv
    main(*args[1:])
