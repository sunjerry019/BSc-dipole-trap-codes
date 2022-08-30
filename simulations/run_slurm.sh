#!/bin/bash

scp -i ~/.ssh/lrz_ed25519 ./potential_sweeping_varying_range.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./slurm_potential_sweeping_varying_range.sh Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ./dipoletrapli.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
scp -i ~/.ssh/lrz_ed25519 ../plotter.py Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/
ssh -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev "/opt/slurm/bin/sbatch -p cip ~/FermiQP/simulations/slurm_potential_sweeping_varying_range.sh"

DONE=0
while [ $DONE -ne 1 ]
do
    echo "Polling Physik Slurm"
    DONE=$(ssh -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev "/opt/slurm/bin/squeue -u Yudong.Sun" | wc -l)
    sleep 1
done
echo "Polling Physik Slurm DONE"
scp -i ~/.ssh/lrz_ed25519 Yudong.Sun@physik.ssh.yudong.dev:~/FermiQP/simulations/sweeping_potential_2D.pdf ./generated/