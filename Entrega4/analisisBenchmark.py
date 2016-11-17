import generarEscenariosBenchmarkE3
import simulacionE3
import constructorDeMapasE3
from numpy import mean
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from pickle import dump
import random


class OutputBenchmark:

    def __init__(self, n_escenarios, repeticiones, seed=0):
        self.escenarios = []
        self.repeticiones = repeticiones
        self.seed = seed

        for i in range(n_escenarios):
            fams = generarEscenariosBenchmarkE3.generar_benchmark()
            mapa = constructorDeMapasE3.construir_mapas('benchmark', 0)[0]
            self.escenarios.append(mapa)

    def generar_benchmark(self):
        tentacion_total = []
        tiempo_total = []
        metros_totales = []
        productos_totales = []
        hist_tiempo_total = []
        hist_tentacion_total = []
        hist_metros_total = []
        for escenario in self.escenarios:
            print('simulando escenario', self.escenarios.index(escenario))
            tentacion, tiempo, metros, productos, hte, hm, hti = simulacionE3.run_simulacion(escenario, debug=3, mt=1,
                                                                               mf=1, replicas=self.repeticiones)
            tentacion_total.append(tentacion[0])
            tiempo_total.append(tiempo[0])
            metros_totales.append(metros[0])
            productos_totales.append(productos[0])
            hist_tiempo_total += hti
            hist_tentacion_total += hte
            hist_metros_total += hm

        te = mean(tentacion_total)
        ti = mean(tiempo_total)
        m = mean(metros_totales)
        p = mean(productos_totales)

        with open('Benchmark/estadisticos.txt', 'w') as file:
            file.write('INDICE DE TENTACION:\n')
            file.write('Promedio: {}\n'.format(te))
            file.write('\n')
            file.write('---------------------------------------------------------\n\n')

        with open('Benchmark/estadisticos.txt', 'a') as file:
            file.write('METROS CAMINADOS:\n')
            file.write('Promedio: {} metros\n'.format(m))
            file.write('\n')
            file.write('---------------------------------------------------------\n\n')

        with open('Benchmark/estadisticos.txt', 'a') as file:
            file.write('TIEMPO EN SUPERMERCADO:\n')
            file.write('Promedio: {} minutos\n'.format(ti))
            file.write('\n')
            file.write('---------------------------------------------------------\n\n')

        with open('Benchmark/estadisticos.txt', 'a') as file:
            file.write('PRODUCTOS VENDIDOS:\n')
            file.write('Promedio: {}\n'.format(p))
            file.write('\n')
            file.write('----------------- ----------------------------------------\n\n')

        y = []
        for dato in hist_tentacion_total:
            y.append(int(dato[1]))

        blue_patch = mpatches.Patch(color='blue', label='Benchmark')
        plt.legend(handles=[blue_patch])

        plt.hist(y, bins=100, normed=True)
        plt.title("Histograma Frecuencia - Tentacion")
        plt.xlabel("Tentacion")
        plt.ylabel("Frecuencia")
        plt.savefig('Benchmark/grafico_tentacion_benchmark.png')
        with open('Benchmark/plot_bytes', 'wb') as file:
            dump(y, file)


def benchmarck(seed=0, replicas=0):
    if seed:
        random.seed(seed)
        b = OutputBenchmark(1, replicas, seed)
        b.generar_benchmark()
    else:
        b = OutputBenchmark(10, 2000)
        b.generar_benchmark()

