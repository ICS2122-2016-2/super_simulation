from numpy import argsort
from scipy import sparse
from pickle import dump, load
from time import time

# ASUME QUE TYPE(R) = NP.ARRAY
def crear_sparse_matrix(N, periodo):
    with open('Datos/matrizProbabilidadesP{}'.format(periodo), 'rb') as file:
        R = load(file)

    for i in range(R.shape[0]):
        r = R[i, :]
        a = argsort(r)
        for j in a[0, :-(N+1)]:
            R[i, j] = float(0)
        R[i, i] = float(0)

    R = sparse.csc_matrix(R)

    with open('Datos/matrizProbabilidadesP{}'.format(periodo), 'wb') as file:
        dump(R, file)
