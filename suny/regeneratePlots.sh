#!/bin/bash

scp -i ~/.ssh/lrz_ed25519 ./simulations/potential_sweeping_varying_range.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./simulations/slurm_potential_sweeping_varying_range.sh Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./simulations/dipoletrapli.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./plotter.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
ssh -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev "/opt/slurm/bin/sbatch -p cip ~/FermiQP/simulations/slurm_potential_sweeping_varying_range.sh"

cd ./simulations/
python3 potential_static_varying_angles.py
python3 potential_static.py
python3 potential_sweeping.py
cd ..

cd ./spectrum_analyser
python3 AOM-Driver-Bandwidth.py
cd ..

python3 ./final_sweeping.py

DONE=0
while [ $DONE -ne 1 ]
do
    echo "Polling Physik Slurm"
    DONE=$(ssh -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev "/opt/slurm/bin/squeue -u Yudong.Sun" | wc -l)
    sleep 1
done
echo "Polling Physik Slurm DONE"
scp -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/sweeping_potential_2D.pdf ./simulations/generated/

mv ./simulations/generated/* 0_allplots/
mv ./spectrum_analyser/generated/* 0_allplots/

echo "ALL PLOTS GENERATED"