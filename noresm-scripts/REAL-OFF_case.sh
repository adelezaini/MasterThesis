#!/bin/bash

set -o errexit #like assert to check and quit program in case of error
set -o nounset

export CESM_ACCOUNT=nn8057k #NN8057K
export PROJECT=nn8057k
export NORESM_ROOT=/cluster/home/$USER/NorESM-sec
export CESM_DATA=/cluster/shared/noresm/inputdata
export CASE_NAME=IDEAL-ON_2000_sec_nudg_f19_f19 #NF2000secBgc #sec
export COMPSET=2000_CAM60%NORESM%SEC%NORPDDMSBC%SDYN_CLM50%BGC-CROP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV
export RES=f19_f19


cd $NORESM_ROOT

#TAG=$(git describe)
CASEROOT=~/cases/$CASE_NAME #-$RES #$COMPSET-$RES-$CASE_NAME

rm -rf $CASEROOT #remove previous cases

cd cime/scripts
./create_newcase --case $CASEROOT --compset $COMPSET --res $RES --machine betzy --run-unsupported --project $CESM_ACCOUNT --handle-preexisting-dirs r

cd $CASEROOT

./xmlchange CALENDAR=GREGORIAN
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=6
./xmlchange REST_N=1
./xmlchange JOB_WALLCLOCK_TIME=24:00:00
./xmlchange RUN_STARTDATE=2007-01-01
#./xmlchange CAM_CONFIG_OPTS=-offline_dyn

#./case.build --clean
./case.setup

# Change input files
echo -e "&clm_inparm\n finidat = '/cluster/home/adelez/noresm-inputdata/CTRL_2000_sec_nudg_f19_f19.clm2.r.2013-01-01-00000.nc'\n fsurdat = '/cluster/home/adelez/noresm-inputdata/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304_GFDL.nc'">> user_nl_clm
# Set interpolation for initial file to "fit" the surface data file
echo -e " use_init_interp = .true." >> user_nl_clm
# Nudging ERA-Interrim
echo -e  "&metdata_nl\n met_nudge_only_uvps = .true.\n met_data_file= \"/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/ERA_f19_tn14/2007-01-01.nc\"\n met_filenames_list = \"/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/AZ/ERA_f19_tn14/fileList.txt\"\n met_rlx_time = 6\n&cam_initfiles_nl\n bnd_topo = \"/cluster/shared/noresm/inputdata/noresm-only/inputForNudging/ERA_f19_tn14/ERA_bnd_topo.nc\"\n" >> user_nl_cam
# Aerosol diagnostic
echo -e  "&phys_ctl_nl\n history_aerosol = .true.\n" >> user_nl_cam
cp ~/noresm-inputdata/preprocessorDefinitions.h SourceMods/src.cam
# Atmospheric output
echo -e "&cam_inparam\n mfilt = 1, 48\n nhtfrq = 0, 1\n avgflag_pertape='A','I'\n fincl1 = 'NNAT_0','FSNT','FLNT','FSNT_DRF','FLNT_DRF','FSNTCDRF','FLNTCDRF','FLNS','FSNS','FLNSC','FSNSC','FSDSCDRF','FSDS_DRF','FSUTADRF','FLUTC','FSUS_DRF','FLUS','CLOUD','FCTL','FCTI','NUCLRATE', 'FORMRATE','GRH2SO4', 'GRSOA', 'GR', 'COAGNUCL','H2SO4','SOA_LV','PS','LANDFRAC','COAGNUCL','FORMRATE','NUCLRATE','SOA_LV','H2SO4','SOA_NA','SO4_NA','NCONC01','NCONC02','NCONC03','NCONC04','NCONC05','NCONC06','NCONC07','NCONC08','NCONC09','NCONC10','NCONC11','NCONC12','NCONC13','NCONC14','SIGMA01','SIGMA02','SIGMA03','SIGMA04','SIGMA05','SIGMA06','SIGMA07','SIGMA08','SIGMA09','SIGMA10','SIGMA11','SIGMA12','SIGMA13','SIGMA14','NMR01','NMR02','NMR03','NMR04','NMR05','NMR06','NMR07','NMR08','NMR09','NMR10','NMR11','NMR12','NMR13','NMR14','FSNS','FSDS_DRF','GR','GRH2SO4','GRSOA','CCN1','CCN2','CCN3','CCN4','CCN5','CCN6','CCN7','CCN_B','TGCLDCWP','cb_H2SO4','cb_SOA_LV','cb_SOA_NA','cb_SO4_NA','CLDTOT','CDNUMC','SO2','isoprene','monoterp','SOA_SV','OH_vmr','AOD_VIS','CAODVIS','CLDFREE','CDOD550','CDOD440','CDOD870','AEROD_v','CABS550','CABS550A','SOA_SEC01','SOA_SEC02','SOA_SEC03','SOA_SEC04','SOA_SEC05','SO4_SEC01','SO4_SEC02','SO4_SEC03','SO4_SEC04','SO4_SEC05','nrSOA_SEC01','nrSOA_SEC02','nrSOA_SEC03','nrSOA_SEC04','nrSOA_SEC05','nrSO4_SEC01','nrSO4_SEC02','nrSO4_SEC03','nrSO4_SEC04','nrSO4_SEC05','SOA_SEC01','SOA_SEC02','SOA_SEC03','SOA_SEC04','SOA_SEC05','SO4_SEC01','SO4_SEC02','SO4_SEC03','SO4_SEC04','SO4_SEC05','nrSOA_SEC01','nrSOA_SEC02','nrSOA_SEC03','nrSOA_SEC04','nrSOA_SEC05','nrSO4_SEC01','nrSO4_SEC02','nrSO4_SEC03','nrSO4_SEC04','nrSO4_SEC05','cb_SOA_SEC01','cb_SOA_SEC02','cb_SOA_SEC03','cb_SOA_SEC04','cb_SOA_SEC05','cb_SO4_SEC01','cb_SO4_SEC02','cb_SO4_SEC03','cb_SO4_SEC04','cb_SO4_SEC05'\n fincl2='SFisoprene','SFmonoterp'" >> user_nl_cam
# BVOC controlled
echo -e  "&megan_emis_nl\n megan_specifier = ''\n" >> user_nl_cam
echo -e  "&chem_inparm\n srf_emis_specifier = 'BC_AX  ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20180512/emissions_cmip6_noresm2_BC_AX_anthrosurfALL_surface_1849-2015_1.9x2.5_version20180512.nc',\n'BC_N   ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20180512/emissions_cmip6_noresm2_BC_N_anthrosurfALL_surface_1849-2015_1.9x2.5_version20180512.nc',\n'OM_NI  ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20180512/emissions_cmip6_noresm2_OM_NI_anthrosurfALL_surface_1849-2015_1.9x2.5_version20180512.nc',\n'SO2    ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20180512/emissions_cmip6_noresm2_SO2_anthrosurfALL_surface_1849-2015_1.9x2.5_version20180512.nc',\n'SO4_PR ->  /cluster/shared/noresm/inputdata/atm/cam/chem/emis/cmip6_emissions_version20180512/emissions_cmip6_noresm2_SO4_PR_anthrosurfALL_surface_1849-2015_1.9x2.5_version20180512.nc'\n'isoprene -> /cluster/home/adelez/noresm-inputdata/BVOCfromCTRL/ems_CTRL_2000_sec_nudg_f19_f19_2007-2012_SFisoprene_addleapyear.nc',\n'monoterp -> /cluster/home/adelez/noresm-inputdata/BVOCfromCTRL/ems_CTRL_2000_sec_nudg_f19_f19_2007-2012_SFmonoterp_addleapyear.nc'" >> user_nl_cam

#./case.build
#./case.submit