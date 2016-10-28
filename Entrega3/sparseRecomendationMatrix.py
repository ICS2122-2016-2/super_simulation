from numpy import argsort
from scipy import sparse
from pickle import dump, load
from time import time

N = 30
# ASUME QUE TYPE(R) = NP.ARRAY

def crear_sparse_matrix(N):
    with open('Datos/matrizDeProbabilidadesPeriodo1', 'rb') as file:
        R = load(file)

    for i in range(R.shape[0]):
        r = R[i, :]
        a = argsort(r)
        for j in a[0, :-(N+1)]:
            R[i, j] = float(0)
        R[i, i] = float(0)

    R = sparse.csc_matrix(R)

    with open('Datos/matrizDeProbabilidadesPeriodo1', 'wb') as file:
        dump(R, file)

t = time()
# crear_sparse_matrix(N)
t = time() - t
print('tiempo ejecucion:', t)