## Backup for files in the home directory of Betzy


\# Copy scripts to noresm-scripts
path_tomaster=/cluster/home/adelez/nird/master-thesis
path_noresmscripts=$path_tomaster/noresm-scripts

cp ~/cases-scripts/* $path_noresmscripts/cases-scripts/
cp ~/*.py $path_noresmscripts
cp ~/*.sh $path_noresmscripts
rsync -avP --exclude 'master-backup.sh' ~/*.sh $path_noresmscripts
cp /cluster/home/adelez/NorESM-sec/Externals.cfg $path_noresmscripts
