from scipy import sparse
from numpy import nan_to_num
from time import time
from pickle import dump
from sparseRecomendationMatrixE4 import crear_sparse_matrix

# TODO INVESTIGAR SOBRE TIPO DE MATRICES SPARSE PARA HACER MAS EFICAZ EL PRODUCTOPUNTO

CANTIDAD_DE_PRODUCTOS = 12750




# TODO GENERAR MATRIZ DE RECOMENDACION
# LEER DATOS Y CREAR SPARSE MATRIX DE TAMANO BOLETAS X PRODUCTOS


def generar_matrices(inicio, termino, periodo):
    t = time()
    cantidad_de_boletas = termino - inicio

    mapeo_productos_indice = {}
    mapeo_indice_productos = {}

    productos_distintos = set()
    with open('retail.dat', 'r') as file:
        row = []
        col = []
        data = []
        for k in range(inicio):
            file.readline()
        l = 0
        for i in range(inicio, termino + 1):
            boleta = [int(j) for j in file.readline().split()]
            for producto in boleta:
                if producto not in productos_distintos:
                    productos_distintos.add(producto)
                    mapeo_productos_indice.update({l: producto})
                    mapeo_indice_productos.update({producto: l})
                    l += 1
                row.append(i - inicio)

                col.append(mapeo_indice_productos[producto])

                data.append(1)

    print('Cantidad de productos vendidos: ', len(data))
    print('Cantidad de boletas: ', cantidad_de_boletas)
    print('Cantidad de productos distintos: ', len(productos_distintos))

    if len(productos_distintos) != 12750:
        print('caca')
    print('hola')

    del productos_distintos

    A = sparse.coo_matrix((data, (row, col)), shape=(cantidad_de_boletas + 1, CANTIDAD_DE_PRODUCTOS), dtype='f')

    t = time() - t
    print('Tiempo de ejecucion A: ', t)
    del data
    del row
    del col

    A = A.tocsc()
    M = A.transpose().dot(A)
    R = A.transpose().dot(A)
    t = time() - t

    print('Tiempo de ejecucion M: ', t)
    del A
    non_zeros = M.nonzero()

    for i in range(len(non_zeros[0])):
        R[non_zeros[0][i], non_zeros[1][i]] = R[non_zeros[0][i], non_zeros[0][i]]

    print('Tiempo de ejecucion R: ', t)

    with open('Datos/matrizDeProbabilidadesPeriodo{}'.format(periodo), 'wb') as file:
        dump(R, file)

    with open('Datos/matrizDeRelacionesPeriodo{}'.format(periodo), 'wb') as file:
        dump(M, file)

    print('Timepo de ejecucion : ', time() - t)

    crear_sparse_matrix(30)



