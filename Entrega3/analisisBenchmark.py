import generarEscenariosBenchmarkE3
import simulacionE3
import constructorDeMapasE3
import histogramasAExcel
from numpy import mean


class OutputBenchmark:

    def __init__(self, n_escenarios, repeticiones):
        self.escenarios = []
        self.repeticiones = repeticiones

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
            tentacion, tiempo, metros, productos, hte, hm, hti = simulacionE3.run_simulacion('escenario1', debug=3, mt=1,
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
            file.write('---------------------------------------------------------\n\n')

            histogramasAExcel.generar_histograma('', 'Benchmark/excel_histogramas_benchmark.xlsx', 1,
                                                      hist_tentacion_total, hist_tiempo_total, hist_metros_total)


b = OutputBenchmark(10, 1000)
b.generar_benchmark()

