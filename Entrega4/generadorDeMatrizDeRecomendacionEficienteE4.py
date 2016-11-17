from scipy import sparse
from numpy import nan_to_num
from time import time
from pickle import dump, load
from sparseRecomendationMatrixE4 import crear_sparse_matrix

# TODO INVESTIGAR SOBRE TIPO DE MATRICES SPARSE PARA HACER MAS EFICAZ EL PRODUCTOPUNTO

CANTIDAD_DE_PRODUCTOS = 12750

t = time()

# TODO GENERAR MATRIZ DE RECOMENDACION
# LEER DATOS Y CREAR SPARSE MATRIX DE TAMANO BOLETAS X PRODUCTOS


def generar_matrices(inicio, termino, periodo):

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

    #print('Cantidad de productos vendidos: ', len(data))
    #print('Cantidad de boletas: ', cantidad_de_boletas)
    #print('Cantidad de productos distintos: ', len(productos_distintos))

    if len(productos_distintos) != 12750:
        print('caca')
        exit(-1)
    #print('hola')

    with open('Datos/calvesProductosP{}'.format(periodo), 'wb') as file:
        dump(mapeo_productos_indice, file)
    with open('Datos/valoresProductosP{}'.format(periodo), 'wb') as file:
        dump(mapeo_indice_productos, file)

    del mapeo_indice_productos
    del mapeo_productos_indice
    del productos_distintos

    A = sparse.coo_matrix((data, (row, col)), shape=(cantidad_de_boletas + 1, CANTIDAD_DE_PRODUCTOS), dtype='f')
    del data
    del row
    del col

    # VECTOR J DE TAMANO BOLETAS X 1 CON LOS DATOS FREQ(I) EN LA COLUMNA I
    row = [i for i in range(cantidad_de_boletas+1)]
    col = [i for i in range(cantidad_de_boletas+1)]
    data = [1 for i in range(cantidad_de_boletas+1)]

    J = sparse.coo_matrix([[1 for i in range(cantidad_de_boletas+1)] for j in range(CANTIDAD_DE_PRODUCTOS)], dtype='f')
    del data
    del row
    del col
    print('Tiempo de ejecucion J, A: ', time()-t)

    J = J.tocsc()
    A = A.tocsc()
    X = J.dot(A)
    del J

    print('Tiempo de ejecucion X: ', time()-t)

    # MATRIZ DE RELACIONES FREQ(I, J)
    M = A.transpose().dot(A)
    del A

    R = M._divide_sparse(X)
    del X

    R = nan_to_num(R)

    with open('Datos/matrizProbabilidadesP{}'.format(periodo), 'wb') as file:
        dump(R, file)
    with open('Datos/matrizRelacionesP{}'.format(periodo), 'wb') as file:
        dump(M, file)

    print('Tiempo de ejecucion : ', time()-t)
    crear_sparse_matrix(30, periodo)

