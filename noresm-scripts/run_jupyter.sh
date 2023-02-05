# Script to run Jupyter in Betzy, working on local browser 
# If this is run in VSCode then a message will appear asking to open local browser,
# otherwise follow indications at: https://towardsdatascience.com/remote-computing-with-jupyter-notebooks-5b2860f761e8

#sshfs adelez@nird.sigma2.no:storage/ storage/
source ./pyenv/bin/activate
cd storage
jupyter notebook --NotebookApp.token='' --no-browser
#jupyter lab --LabApp.token='' --no-browser