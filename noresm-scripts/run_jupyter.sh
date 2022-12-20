#sshfs adelez@nird.sigma2.no:storage/ storage/
source ./pyenv/bin/activate
cd storage
jupyter notebook --NotebookApp.token='' --no-browser
#jupyter lab --LabApp.token='' --no-browser