#!/bin/bash
#
#SBATCH --job-name=SweepPotential
#SBATCH --comment="Process Sweeping Potentials"
#SBATCH --ntasks=8
#SBATCH --partition=cip
#SBATCH --mem-per-cpu=32768
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=Yudong.Sun@physik.uni-muenchen.de
#SBATCH --chdir=/home/y/Yudong.Sun/FermiQP/simulations/
#SBATCH --output=/home/y/Yudong.Sun/FermiQP/slurm/slurm.%j.%N.out
#SBATCH --error=/home/y/Yudong.Sun/FermiQP/slurm/slurm.%j.%N.err.out

# source /etc/profile.d/modules.sh
# module load openmpi

mpiexec -n $SLURM_NTASKS python3 potential_sweeping_varying_range.py