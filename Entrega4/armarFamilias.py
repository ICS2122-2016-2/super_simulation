from pickle import load
from numpy import argsort
from scipy import sparse
from random import choice
from time import time
import json


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


def generar_J(familia):
    data = []
    row = []
    col = []
    for p in familia:
        data.append(1)
        row.append(0)
        col.append(p)
    boleta = sparse.coo_matrix((data, (row, col)), shape=(1, 12750), dtype='f')
    return boleta


def armar_familias(periodo):

    with open('Datos/matrizProbabilidadesP{}'.format(periodo), 'rb') as file:
        R = load(file)

    t = time()

    with open('Datos/matrizRelacionesP{}'.format(periodo), 'rb') as file:
        matriz_relaciones = load(file)

    # Obtener productos mas y menos frecuentes
    productos_ordenados = matriz_relaciones.diagonal()

    mas_frecuentes = argsort(productos_ordenados)
    mas_frecuentes = list(i for i in mas_frecuentes)
    menos_frecuentes = mas_frecuentes[:750]
    for i in range(len(menos_frecuentes)):
        menos_frecuentes[i] = int(menos_frecuentes[i])
    mas_frecuentes.reverse()
    productos_por_agregar = mas_frecuentes[30:len(mas_frecuentes) - 750]
    mas_frecuentes = mas_frecuentes[:30]

    productos_por_agregar.reverse()
    productos_sobrantes = []

    familias = []
    for i in mas_frecuentes:
        familias.append([int(i)])

    t = time() - t
    frecuencia_familias = {k: 0 for k in range(30)}

    for i in range(30):
        frecuencia_familias[i] += matriz_relaciones[familias[i][0], familias[i][0]]

    correlacionados = 0
    no_corr = 0

    # Productos sin familias
    skus_sobrantes = []
    for i in range(15):
        skus_sobrantes.append(menos_frecuentes[50 * i: 50 * (i + 1)])

    #agregar prods a familias
    for z in range(len(productos_por_agregar)):
        # todo: cambiar metedo de agregar familias
        # FORMA 1: que se armen eligiendo aleatoriamente  de los que no se han agregado aun
        sku = choice(productos_por_agregar)
        productos_por_agregar.remove(sku)

        # FORMA 2: elegir productos ordenados por orden de ventas decreciente
        # sku = productos_por_agregar[0]
        # productos_por_agregar.remove(sku)

        # FORMA 3: elegir productos ordenados por orden de ventas decreciente
        # sku = productos_por_agregar[-1]
        # productos_por_agregar.remove(sku)

        # FORMA 4: elegir productos ordenados por orden de ventas decreciente
        # sku = productos_por_agregar[-1]
        # productos_por_agregar.remove(sku)

        # Calcular correlacion producto con familia
        correlaciones_familias = []

        for i in range(len(familias)):
            if len(familias[i]) < 400:

                J = generar_J(familias[i])
                boleta_familia = generar_boleta_de_familias(familias[i])
                corr = R.dot(boleta_familia)
                corr = float(J.dot(corr)[0, 0])

                promedio_correlacion_familia = corr / (len(familias[i]))
                correlaciones_familias.append(promedio_correlacion_familia)
            else:
                correlaciones_familias.append(0)

        # Agregar producto
        corr_max = correlaciones_familias.index(max(correlaciones_familias))
        if len(familias[corr_max]) < 400:
            correlacionados += 1
            familias[corr_max].append(int(sku))
            frecuencia_familias[corr_max] += matriz_relaciones[corr_max, corr_max]
        else:
            no_corr += 1
            dict = {i: j for i, j in enumerate(frecuencia_familias.values())}
            while True:
                minimo = min(dict, key=lambda x: dict[x])
                if len(familias[minimo]) < 400:
                    familias[minimo].append(int(sku))
                    break
                else:
                    dict.pop(minimo)
                    if len(dict) == 0:
                        print('caca')
    familias.reverse()

    # a = set()
    # b = set()
    # for i in familias:
    #     for j in i:
    #         a.add(j)
    # for i in productos_sobrantes:
    #     b.add(i)
    #
    # print('productos en familias', len(a))
    # print('productos sobrantes', len(b))
    # print('---------------------------------------------------------------')
    # print('productos agregados por correlacion', correlacionados)
    # print('productos agregados por lista sobrantes', no_corr)

    # Revisar frecuencias de las familias al final

    # print(frecuencia_familias)
    print('diferencia maxima:', max(frecuencia_familias.values()) - min(frecuencia_familias.values()))
    print('frecuencia minima:', min(frecuencia_familias.values()))

    t = time() - t
    print('Tiempo:', t)

    # Crear suubfamilias dentro de cada familia
    print('creando subfamilias')

    lista_subfamilias = []
    lista_frecuencia_subfamilias ={}
    k=0
    for familia in familias:
        k += 1
        print(k)
        p_corr = 0
        p_no_corr = 0
        mas_frecuentes = sorted(familia, key=lambda x:matriz_relaciones[x, x], reverse=True)


        productos_por_agregar = mas_frecuentes[8:]
        mas_frecuentes = mas_frecuentes[:8]

        subfamilias = []
        for i in mas_frecuentes:
            subfamilias.append([int(i)])

        frecuencia_subfamilias = {k: 0 for k in range(8)}

        for i in range(8):
            frecuencia_subfamilias[i] += matriz_relaciones[subfamilias[i][0], subfamilias[i][0]]

        for z in range(len(productos_por_agregar)):

            sku = choice(productos_por_agregar)
            productos_por_agregar.remove(sku)
            # Calcular correlacion producto con familia
            correlaciones_subfamilias = []
            productos_sobrantes = []

            for i in range(len(subfamilias)):
                if len(subfamilias[i]) < 50:
                    J = generar_J(subfamilias[i])
                    boleta_familia = generar_boleta_de_familias(subfamilias[i])
                    corr = R.dot(boleta_familia)
                    corr = float(J.dot(corr)[0, 0])
                    promedio_correlacion_subfamilia = corr / (len(subfamilias[i]))
                    correlaciones_subfamilias.append(promedio_correlacion_subfamilia)
                else:
                    correlaciones_subfamilias.append(0)
            # Agregar productos
            corr_max = correlaciones_subfamilias.index(max(correlaciones_subfamilias))
            if len(subfamilias[corr_max]) < 50:
                p_corr += 1
                subfamilias[corr_max].append(int(sku))
                frecuencia_subfamilias[corr_max] += matriz_relaciones[corr_max, corr_max]

            else:
                p_no_corr += 1
                dict = {i: j for i, j in enumerate(frecuencia_subfamilias.values())}
                while True:
                    minimo = min(dict, key=lambda x: dict[x])
                    if len(subfamilias[minimo]) < 50:
                        subfamilias[minimo].append(int(sku))
                        break
                    else:
                        dict.pop(minimo)
                        if len(dict) == 0:
                            print('caca')

        lista_subfamilias.append(subfamilias)
        lista_frecuencia_subfamilias.update({familias.index(familia): frecuencia_subfamilias})

    print('reordenando familias')
    # ordenar subfamilias por cantidad de ventas
    for j in range(len(lista_subfamilias)):
        fam = lista_subfamilias[j]

        sub_fam_ordanada = sorted(fam, key=lambda x: lista_frecuencia_subfamilias[j][fam.index(x)], reverse=True)

        # poner mas vendidos en gondolas de abajo al medio, en gondolas de arribaa arriba
        if j in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            # sub_fam_final = []
            # for i in range(len(fam)):
            #     sub_fam_final.append(0)
            # for k in range(3):
            #     sub_fam_final[k+5] = sub_fam_ordanada[k]
            #
            # for k in range(3, 8):
            #     sub_fam_final[k-3] = sub_fam_ordanada[k]
            #
            # lista_subfamilias[j] = sub_fam_final
            sub_fam_ordanada.reverse()
            lista_subfamilias[j] = sub_fam_ordanada
        else:
            lista_subfamilias[j] = sub_fam_ordanada


    # ordenar subfamilias en familias
    # orden: 8 7 6 1 2 3 4 5 --->
    for j in range(len(lista_subfamilias)):
        fam = lista_subfamilias[j]
        familia_final = []
        for i in range(16):
            familia_final.append(0)
        for i in range(len(fam)):
            gondola1 = fam[i][:25]
            gondola2 = fam[i][25:]
            familia_final[i] = gondola1
            familia_final[i+8] = gondola2

        familias[j] = []

        for i in range(len(familia_final)):
            familias[j] += familia_final[i]

    with open('Datos/familiasP{}.json'.format(periodo), 'w') as file:
        json.dump(familias, file)

    with open('Datos/skus_sobrantesP{}.json'.format(periodo), 'w') as file:
        json.dump(skus_sobrantes, file)

#armar_familias(1)