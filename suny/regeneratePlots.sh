#!/bin/bash

scp -i ~/.ssh/lrz_ed25519 ./simulations/potential_sweeping_varying_range.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./simulations/slurm_potential_sweeping_varying_range.sh Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./simulations/dipoletrapli.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./plotter.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
ssh -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev "/opt/slurm/bin/sbatch -p cip ~/FermiQP/simulations/slurm_potential_sweeping_varying_range.sh"

python3 ./simulations/potential_static_varying_angles.py
python3 ./simulations/potential_static.py
python3 ./simulations/potential_sweeping.py

python3 ./

DONE=0
while [ $DONE -neq 1 ]
do
    DONE=$(ssh -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev "/opt/slurm/bin/squeue -u Yudong.Sun" | wc -l)
done
scp -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/sweeping_potential_2D.pdf ./simulations/generated/

mv ./simulations/generated/* 0_allplots/

python3 ./final_sweeping.py