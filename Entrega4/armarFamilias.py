from pickle import load
from numpy import argsort
from time import time
import json


def armar_familias(periodo):
    t = time()
    with open('Datos/matrizProbabilidadesP{}'.format(periodo), 'rb') as file:
        matriz_probabilidad = load(file)

    with open('Datos/matrizRelacionesP{}'.format(periodo), 'rb') as file:
        matriz_relaciones = load(file)

    # Obtener productos mas y menos frecuentes
    #print("Sacando jefes y productos menos frecuentes")
    productos_ordenados = matriz_relaciones.diagonal()

    mas_frecuentes = argsort(productos_ordenados)
    mas_frecuentes = list(i for i in mas_frecuentes)
    menos_frecuentes = mas_frecuentes[:750]
    mas_frecuentes.reverse()
    productos_por_agregar = mas_frecuentes[30:len(mas_frecuentes) - 750]
    mas_frecuentes = mas_frecuentes[:30]

    productos_sobrantes = []

    familias = []
    for i in mas_frecuentes:
        familias.append([int(i)])

    t = time() - t
    #print('Formando familias, tiempo:', t)
    # Formar familias
    # Calcular frecuencias de las familias

    frecuencia_familias = {k: 0 for k in range(30)}

    for i in range(30):
        frecuencia_familias[i] += matriz_relaciones[familias[i][0], familias[i][0]]

    for sku in productos_por_agregar:
        # Calcular correlacion producto con familia
        correlaciones_familias = []
        for i in range(len(familias)):
            corr = 0
            if len(familias[i]) < 400 and frecuencia_familias[i] < max(frecuencia_familias):
                for producto in familias[i]:
                    corr += matriz_probabilidad[producto, sku]
                promedio_correlacion_familia = corr/(len(familias[i]))
                correlaciones_familias.append(promedio_correlacion_familia)
            else:
                correlaciones_familias.append(0)

        # Agregar producto
        corr_max = correlaciones_familias.index(max(correlaciones_familias))
        if len(familias[corr_max]) < 400:
            familias[corr_max].append(int(sku))
            frecuencia_familias[corr_max] += matriz_relaciones[corr_max, corr_max]
        else:
            productos_sobrantes.append(int(sku))



    # Agregar productos sobrantes
    #print("Los poroductos asignados al azar son:")
    #print(len(productos_sobrantes))

    t = time() - t
    #print('Agregar sobrantes a familias, tiempo:', t)
    familias.reverse()

    # agregar productos sin correlacion
    for familia in familias:
        if len(familia) < 400:
            pops = []
            for i in range(len(productos_sobrantes)):
                familia.append(int(productos_sobrantes[i]))
                pops.append(i)
                if len(familia) == 400:
                    break
            pops.reverse()
            for i in pops:
                productos_sobrantes.pop(i)


    # Revisar frecuencias de las familias al final
    frecuencia_familias = []
    for familia in familias:
        frecuencia = 0
        for producto in familia:
            frecuencia += matriz_relaciones[producto, producto]
        frecuencia_familias.append(frecuencia)

    #print(frecuencia_familias)

    #print('diferencia maxima:', max(frecuencia_familias) - min(frecuencia_familias))
    #print('frecuancia minima:', min(frecuencia_familias))

    # Productos sobrantes sin familias
    for i in range(len(menos_frecuentes)):
        menos_frecuentes[i] = int(menos_frecuentes[i])

    skus_sobrantes = []
    for i in range(15):
        skus_sobrantes.append(menos_frecuentes[50*i: 50*(i+1)])

    '''
    # Crear suubfamilias dentro de cada familia
    lista_subfamilias = []
    for familia in familias:
        mas_frecuentes = sorted(familia, reverse=True)
        productos_por_agregar = mas_frecuentes[16:]
        mas_frecuentes = mas_frecuentes[:16]

        subfamilias = []
        for i in mas_frecuentes:
            subfamilias.append([int(i)])

        frecuencia_subfamilias = {k: 0 for k in range(16)}

        for i in range(16):
            frecuencia_subfamilias[i] += matriz_relaciones[subfamilias[i][0], subfamilias[i][0]]

        for sku in productos_por_agregar:
            # Calcular correlacion producto con familia
            correlaciones_subfamilias = []
            productos_sobrantes = []
            for i in range(len(subfamilias)):
                corr = 0
                if len(subfamilias[i]) < 25:
                    for producto in subfamilias[i]:
                        corr += matriz_probabilidad[producto, sku]
                    promedio_correlacion_subfamilia = corr/(len(subfamilias[i]))
                    correlaciones_subfamilias.append(promedio_correlacion_subfamilia)
                else:
                    correlaciones_subfamilias.append(0)

            # Agregar producto
            corr_max = correlaciones_subfamilias.index(max(correlaciones_subfamilias))
            if len(subfamilias[corr_max]) < 25:
                subfamilias[corr_max].append(int(sku))
                frecuencia_subfamilias[corr_max] += matriz_relaciones[corr_max, corr_max]
            else:
                productos_sobrantes.append(int(sku))

            # productos no agregados
            for subfamilia in subfamilias:
                if len(subfamilia) < 25:
                    for prod in productos_sobrantes:
                        subfamilia.append(int(prod))
                        productos_sobrantes.remove(prod)
                        if len(subfamilia) == 25:
                            break

        lista_subfamilias.append(subfamilias)
    '''

    # a = set()
    # for i in familias:
    #     for j in i:
    #         a.add(j)
    # for i in productos_sobrantes:
    #     a.add(i)
    # for i in skus_sobrantes:
    #     for j in i:
    #         a.add(j)
    # print(len(a))
    # exit()

    # print(type(familias))
    # print(familias[0])
    # print(type(familias[0][0]))
    # print(familias[1])
    # print(familias[2])
    # print(len(familias[0]))

    with open('Datos/familiasP{}.json'.format(periodo), 'w') as file:
        json.dump(familias, file)

    # for i in range(len(lista_subfamilias)):
    #     with open('Datos/subfamilias{}P{}.json'.format(i, periodo), 'w') as file:
    #         json.dump(lista_subfamilias[i], file)

    with open('Datos/skus_sobrantesP{}.json'.format(periodo), 'w') as file:
        json.dump(skus_sobrantes, file)

