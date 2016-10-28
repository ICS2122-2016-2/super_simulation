from scipy import sparse
from numpy import dot, transpose, matrix as npmatrix, sort, array
from time import time
from pickle import dump

# TODO INVESTIGAR SOBRE TIPO DE MATRICES SPARSE PARA HACER MAS EFICAZ EL PRODUCTOPPUNTO

INDICES_BOLETAS = (0, 32904)
CANTIDAD_DE_PRODUCTOS = 12750


cantidad_de_boletas = INDICES_BOLETAS[1] - INDICES_BOLETAS[0] + 1
t = time()

''' Matriz periodo n '''
# LEER DATOS Y CREAR SPARSE MATRIX DE TAMANO BOLETAS X PRODUCTOS
with open('retail.dat', 'r') as file:
    row = []
    col = []
    data = []
    for i in range(INDICES_BOLETAS[0], INDICES_BOLETAS[1] + 1):
        boleta = [int(j) for j in file.readline().split()]
        for producto in boleta:
            row.append(i)
            col.append(producto)
            data.append(1)

A = sparse.coo_matrix((data, (row, col)), shape=(cantidad_de_boletas, CANTIDAD_DE_PRODUCTOS), dtype='f')

# MATRIZ DE RELACIONES FREQ(I, J)
M = dot(transpose(A), A)
M = M.tolil()

# VECTOR J DE TAMANO BOLETAS X 1 CON LOS DATOS FREQ(I) EN LA COLUMNA I
J = sparse.coo_matrix([[1] for i in range(cantidad_de_boletas)], shape=(32905, 1), dtype='f')
J = dot(transpose(A), J)


for i in range(M.shape[0]):
    if i%100==0:
        print(i/100)
        print('Timepo de ejecucion : ', time() - t)
    for j in range(M.shape[1]):
        M[i, j] = M[i, j]/M[i, i]

with open('Datos/matrizDeProbabilidadesPeriodo1', 'wb') as file:
    dump(M, file)

print('Timepo de ejecucion : ', time()-t)

