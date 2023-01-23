#!/bin/bash

# This script automatizes the copy of files to the GitHub repo master-thesis

path_tomaster=/cluster/home/adelez/nird/master-thesis #or storage/master-thesis

#rsync -avP --ignore-existing adelez@nird.sigma2.no:~/storage/archive/$1/ ~/Desktop/master-thesis/data/$1/


# Copy scripts to noresm-scripts
path_noresmscripts=$path_tomaster/noresm-scripts

cp ~/cases-scripts/* $path_noresmscripts/cases-scripts/
cp ~/*.py $path_noresmscripts
cp ~/*.sh $path_noresmscripts
rsync -avP --exclude 'master-backup.sh' ~/*.sh $path_noresmscripts
cp /cluster/home/adelez/NorESM-sec/Externals.cfg $path_noresmscripts

# Copy simulation input files to noresm-inputdata
rsync -avP --delete --exclude '*/*.nc' ~/noresm-inputdata/ $path_tomaster/noresm-inputdata

