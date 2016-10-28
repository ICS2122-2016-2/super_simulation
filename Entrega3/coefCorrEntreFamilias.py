from pickle import load
import json
from scipy import sparse


def generar_boleta_de_familias(familia):

    data = []
    row = []
    col = []
    for p in familia:
        data.append(1)
        row.append(p)
        col.append(0)

    boleta = sparse.coo_matrix((data, (row, col)), shape=(12750, 1), dtype='f')
    return boleta

with open('Datos/matrizDeProbabilidadesPeriodo1', 'rb') as file:
    R = load(file)

with open('Familias/familias_mas_sobrantes2.json', 'r') as file:
    familias = json.load(file)
    familias = familias[0]

correlaciones = {}

for i in range(len(familias)):
    boleta = generar_boleta_de_familias(familias[i])
    corr = R.dot(boleta)
    for j in range(len(familias)):
        if i == j:
            continue
        vector_familia = generar_boleta_de_familias(familias[j])
        coef = corr.transpose().dot(vector_familia)
        correlaciones[str((i,j))] = str(round(coef[0,0], 4))
        print((i,j), correlaciones[str((i,j))])


with open('Familias/correlacionesF2.json', 'w') as file:
    json.dump(correlaciones, file)

with open('Escenarios/correlacionesF2.json', 'w') as file:
    json.dump(correlaciones, file)