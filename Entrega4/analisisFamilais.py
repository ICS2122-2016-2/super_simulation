from pickle import load
from numpy import argsort
from scipy import sparse
from random import choice
from time import time
from random import choice
import json

a = [1,2,3]
a.reverse()
print(a)
exit()

print('correlaciones: ')
with open('Analisis Familias/familiasP1_aleatorea.json', 'r') as file:
   familias = json.load(file)

with open('Datos/matrizProbabilidadesP1', 'rb') as file:
    R = load(file)

with open('Datos/matrizRelacionesP1', 'rb') as file:
    matriz_relaciones = load(file)


class Familias:

    def __init__(self, familias):
        self.subfamilias = {i: [] for i in range(8)}
        productos_gondola = (i for i in familias)

        for y in range(1, 8 * 5 + 1):
            for z in range(1, 6):
                id = int(next(productos_gondola))
                self.subfamilias[((y-1) // 5)].append(id)

        for y in range(1, 8 * 5 + 1):
            for z in range(1, 6):
                id = int(next(productos_gondola))
                self.subfamilias[((y-1) // 5) ].append(id)

    def generar_boleta_de_familias(self, subfam):
        data = []
        row = []
        col = []
        for p in subfam:
            data.append(1)
            row.append(p)
            col.append(0)

        boleta = sparse.coo_matrix((data, (row, col)), shape=(12750, 1), dtype='f')
        return boleta

    def corr_subfamilas(self):
        s = self.generar_boleta_de_familias(self.subfamilias[1])
        d = self.generar_boleta_de_familias(self.subfamilias[2])
        suma = 0
        for i in range(8):
            boleta = self.generar_boleta_de_familias(self.subfamilias[i])
            corr = boleta.transpose().dot(R).dot(boleta)
            suma+=corr[0,0]
        return suma



s1 = 0
for j in range(len(familias)):
    f = Familias(familias[j])
    suma = f.corr_subfamilas()
    s1 += suma
print('armadas aleatorieas:', s1)

# ordenadas
with open('Analisis Familias/familiasP1_ordenadas.json', 'r') as file:
   familias = json.load(file)

s2 = 0
for j in range(len(familias)):
    f = Familias(familias[j])
    suma = f.corr_subfamilas()
    s2 += suma
print('ordenadas:', s2)


with open('Analisis Familias/familiasP1_mas_frecuentes.json', 'r') as file:
   familias = json.load(file)

s2 = 0
for j in range(len(familias)):
    f = Familias(familias[j])
    suma = f.corr_subfamilas()
    s2 += suma
print('mas frecuentes:', s2)

with open('Analisis Familias/familiasP1_menos_frecuentes.json', 'r') as file:
   familias = json.load(file)

s2 = 0
for j in range(len(familias)):
    f = Familias(familias[j])
    suma = f.corr_subfamilas()
    s2 += suma
print('menos frecuentes:', s2)

# al azar

prods = list(range(12750))
familias = []
for i in range(30):
    f = []
    for j in range(400):
        p = choice(prods)
        prods.remove(p)
        f.append(p)
    familias.append(f)

extras = []
for i in range(15):
    e = []
    for j in range(50):
        p = choice(prods)
        prods.remove(p)
        e.append(p)
    extras.append(e)

with open('Analisis Familias/familiasP1_al_azar.json', 'w') as file:
   json.dump(familias, file)

with open('Analisis Familias/extras_P1_al_azar.json', 'w') as file:
    json.dump(extras, file)

s2 = 0
for j in range(len(familias)):
    f = Familias(familias[j])
    suma = f.corr_subfamilas()
    s2 += suma
print('al azar:', s2)


