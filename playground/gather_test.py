from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
mpisize = comm.Get_size()
mpirank = comm.Get_rank()

mypotentials  = np.ones((1, 700, 700), dtype = np.float64) * mpirank
print(f"Rank {mpirank}", mypotentials)
allpotentials = np.empty((mpisize, *np.shape(mypotentials)), dtype = np.float64)

split_counts  = [np.size(mypotentials)] * mpisize
displacements = np.insert(np.cumsum(split_counts),0,0)[0:-1]
comm.Barrier()

comm.Gatherv(sendbuf = mypotentials, recvbuf = [allpotentials, split_counts, displacements, MPI.DOUBLE], root = 0)

if mpirank == 0:
    print(np.shape(allpotentials))

