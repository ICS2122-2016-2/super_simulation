from pickle import dump, load
from numpy import argsort, nonzero
from scipy import sparse
from sys import getsizeof

BOLETA = 30

with open('Datos/matrizDeProbabilidadesPeriodo1', 'rb') as file:
    R = load(file)

data = []
row = []
col = []

with open('retail.dat', 'r') as file:
    boleta = [int(j) for j in file.readlines()[BOLETA].split()]
    for p in boleta:
        data.append(1)
        row.append(p)
        col.append(0)

b = sparse.coo_matrix((data, (row, col)), shape=(12750, 1), dtype='f')

print(b.nonzero())

print(boleta)

recomendacion = R.dot(b)
print(recomendacion)



# TODO GENERAR HISTOGRAMAS DE CANTIDAD DE PRODUCTOS, Y MAS COSAS
# TODO INTENTAR CARACTERIZAR FAMILIAS DE ALGUNA FORMA
# TODO GRAFICAR LAS RELACIONES ENTRE PRODUCTOS Y LOS PRODUCTOS TENTADOS EN UNA BOLETA