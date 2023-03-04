# Script to generate postprocessed data

#sshfs adelez@nird.sigma2.no:storage/ storage/
source ./pyenv/bin/activate
cd /cluster/home/adelez/storage/master-thesis/notebooks/output

for comp in atm lnd
do
    echo "Component: $comp"
    for casealias in CTRL IDEAL-ON IDEAL-OFF REAL-ON REAL-OFF
    do
        casename=${casealias}_2000_f19_f19
        echo "${casename} started"
        python3 postprocess.py $casename $casealias $comp h0
        echo "${casename} ended"
    done
done


