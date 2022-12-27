# noresm-inputdata: folder that gathers all the input files needed to run my own cases

- `surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc`: input surface data for CTRL run (optional - the original path is `/cluster/shared/noresm/inputdata/lnd/clm2/surfdata_map/release-clm5.0.18/surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304.nc`)
- `surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304_edited.nc`: input surface data for IDEAL-ON/OFF run (edited from the previous)
- `surfdata_1.9x2.5_hist_78pfts_CMIP6_simyr2000_c190304_GFDL.nc`: input surface data for REAL-ON/OFF run (edited from the previous)
- `CTRL_2000_sec_nudg_f19_f19.clm2.r.2013-01-01-00000.nc`: restart file from CTRL run used for all the other simulations (needed to match the surface data file - by Kjetil)
- `preprocessorDefinitions.h`: edited file from original path `~/cases/case-name/SourceMods/src.cam/preprocessorDefinitions.h`, in order to decompose aersol direct/semi-direct/indirect effects and run an aerosol diagnostics https://noresm-docs.readthedocs.io/en/latest/output/aerosol_output.html. See `CTRL_case.sh` for details.
- `BVOCfromCTRL` folder: contains output from script create_em_files_high_res.py, that prepares the high time resolution BVOC output from the CTRL run ready for IDEAL-OFF and REAL-OFF.