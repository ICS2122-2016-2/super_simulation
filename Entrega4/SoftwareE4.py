import generarEstaciones
import generadorDeMatrizDeRecomendacionEficienteE4
import armarFamilias
from time import time
import optimizacion_corr_familiasE4
import optimizacion_simulacionE4
import analisisBenchmark
import json
import pickle


tnow = time()


def calcular_datos_periodos():
    periodos = generarEstaciones.periodos('retail.dat')

    with open('Datos/periodos', 'wb') as file:
        pickle.dump(periodos, file)

    # generar matrices
    for periodo in periodos:
        generadorDeMatrizDeRecomendacionEficienteE4.generar_matrices(periodo[0], periodo[1], periodos.index(periodo)+1)

    # armar familias
    for periodo in periodos:
        armarFamilias.armar_familias(periodos.index(periodo)+1)

    # reordenar familias
    for j in range(1, 4):
        orden = optimizacion_corr_familiasE4.optimizacion_correlaciones(j)
        familias_finales = list(range(30))
        with open('Datos/familiasP{}.json'.format(j), 'r') as file:
            familias_anteriores = json.load(file)
        for i in range(30):
            familias_finales[int(orden[i][1])] = familias_anteriores[int(orden[i][0])]
        with open('Datos/familiasP{}.json'.format(j), 'w') as file:
            json.dump(familias_finales, file)


def generar_benchmark():
    analisisBenchmark.benchmarck()


def optimizar_con_simulacion(periodo, velocidad, step1, step2, step3=0):
    # optimizar con simulacion
    with open('Datos/periodos', 'rb') as file:
        periodos = pickle.load(file)
    escenario = ['Datos/familiasP{}.json'.format(periodo), 'Datos/skus_sobrantesP{}.json'.format(periodo)]
    optimizacion_simulacionE4.optimizar(escenario, 999, 999, 999, 999, step1, step2, step3, periodo=periodo, indices=periodos[periodo-1],
                                    velocidad=velocidad)


calcular_datos_periodos()
#generar_benchmark()
#optimizar_con_simulacion(1, .8*60, 100, 10000, 15000)



