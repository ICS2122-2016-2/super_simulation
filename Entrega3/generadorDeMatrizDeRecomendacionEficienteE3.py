from scipy import sparse
from numpy import nan_to_num
from time import time
from pickle import dump
from sparseRecomendationMatrix import crear_sparse_matrix

# TODO INVESTIGAR SOBRE TIPO DE MATRICES SPARSE PARA HACER MAS EFICAZ EL PRODUCTOPUNTO

INDICES_BOLETAS = (0, 36081)
CANTIDAD_DE_PRODUCTOS = 12750


cantidad_de_boletas = INDICES_BOLETAS[1] - INDICES_BOLETAS[0] + 1
t = time()

# TODO GENERAR MATRIZ DE RECOMENDACION
# LEER DATOS Y CREAR SPARSE MATRIX DE TAMANO BOLETAS X PRODUCTOS
productos_distintos = set()
with open('retail.dat', 'r') as file:
    row = []
    col = []
    data = []
    for i in range(INDICES_BOLETAS[0], INDICES_BOLETAS[1] + 1):
        boleta = [int(j) for j in file.readline().split()]
        for producto in boleta:
            row.append(i)
            col.append(producto)
            productos_distintos.add(producto)
            data.append(1)

print('Cantidad de productos vendidos: ', len(data))
print('Cantidad de boletas: ', max(row))
print('Cantidad de productos distintos: ', len(productos_distintos))

if len(productos_distintos) != 12750:
    exit(-1)

del productos_distintos

A = sparse.coo_matrix((data, (row, col)), shape=(cantidad_de_boletas, CANTIDAD_DE_PRODUCTOS), dtype='f')
del data
del row
del col

# VECTOR J DE TAMANO BOLETAS X 1 CON LOS DATOS FREQ(I) EN LA COLUMNA I
row = [i for i in range(cantidad_de_boletas)]
col = [i for i in range(cantidad_de_boletas)]
data = [1 for i in range(cantidad_de_boletas)]
J = sparse.coo_matrix([[1 for i in range(cantidad_de_boletas)] for j in range(CANTIDAD_DE_PRODUCTOS)], dtype='f')

del data
del row
del col

print('Timepo de ejecucion J, A: ', time()-t)

J = J.tocsc()
A = A.tocsc()
X = J.dot(A)
del J

print('Timepo de ejecucion X: ', time()-t)

# MATRIZ DE RELACIONES FREQ(I, J)
M = A.transpose().dot(A)
del A

R = M._divide_sparse(X)

R = nan_to_num(R)

with open('Datos/matrizDeProbabilidadesPeriodo1', 'wb') as file:
    dump(R, file)

with open('Datos/matrizDeRelacionesPeriodo1', 'wb') as file:
    dump(M, file)

print('Timepo de ejecucion : ', time()-t)

crear_sparse_matrix(30)
