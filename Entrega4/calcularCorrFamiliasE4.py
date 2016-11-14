from pickle import load
import json
from scipy import sparse


def calcular_correlaciones(periodo, subfamilia=-1):

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

    with open('Datos/matrizProbabilidadesP{}'.format(periodo), 'rb') as file:
        R = load(file)

    if subfamilia == -1:
        with open('Datos/familiasP{}.json'.format(periodo), 'r') as file:
            familias = json.load(file)
    else:
        with open('Datos/subfamilias{}P{}.json'.format(subfamilia,periodo), 'r') as file:
            familias = json.load(file)

    correlaciones = {}

    for i in range(len(familias)):
        boleta = generar_boleta_de_familias(familias[i])
        corr = R.dot(boleta)
        for j in range(len(familias)):
            if i == j:
                continue
            vector_familia = generar_boleta_de_familias(familias[j])
            coef = corr.transpose().dot(vector_familia)
            correlaciones[(i,j)] = round(coef[0,0], 4)
            #correlaciones[str((i, j))] = str(round(coef[0,0], 4))
            #print((i, j), correlaciones[str((i, j))])
    # print(correlaciones)
    return correlaciones
    # if subfamilia == -1:
    #     with open('Datos/correlacionesFamiliasP{}.json'.format(periodo), 'w') as file:
    #         json.dump(correlaciones, file)
    # else:
    #     with open('Datos/correlacionesSubfamilia{}P{}.json'.format(subfamilia,periodo), 'w') as file:
    #         json.dump(correlaciones, file)
