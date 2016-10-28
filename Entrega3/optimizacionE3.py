import constructorDeMapasE3
from itertools import permutations
from math import ceil
from time import time
from numpy import sqrt
import simulacionE3
import histogramasAExcel
import threading


## 1) GENERAR ESCENARIOS ADYACENTES Y UNIRLOS A TRAVES DE UN GRAFO
## 2) DEFINIR COMO SE COMPORTARA LA SIMULACION -> replicas, donde itera, como se alcena los resultados, si se repetira alguna boleta



CRITERIO_DE_TERMINO1 = 0
CRITERIO_DE_TERMINO2 = 0


# LA GRILLA CORRESPONDE A LAS COORDENADAS (X,Y), X IN {1,2,3}, Y IN {1,2} para
class Particion:

    def __init__(self, familias, coordenada):
        self.grupo = familias
        self.orden = {i: j for i, j in enumerate(familias)}
        self.coord = coordenada


class Generador_escenarios:

    def __init__(self, mapa, n_partiones):
        self.escenario_inicial = mapa
        # numero particiones =  2 o 4 o 6
        self.n_particiones = n_partiones
        self.particiones = {}
        self.particionar()

        self.escenarios_posibles = []
        self.generar_escenarios()

    def generar_escenarios(self):
        permutaciones = permutations(self.particiones)
        for i in range(self.factorial(self.n_particiones)):
            lista_familias = []
            productos_sobrantes = self.escenario_inicial.productos_extra
            permutacion = next(permutaciones)
            for i in permutacion:
                for j in range(len(self.particiones[i].orden)):
                    familia = self.particiones[i].orden[j].familia
                    lista_familias.append(familia)
            escenario = [lista_familias, productos_sobrantes]
            mapa = constructorDeMapasE3.construir_mapas(escenario, 1)[0]
            self.escenarios_posibles.append(mapa)

    def particionar(self):
        y = []
        for i in range(15):
            y.append(2)
        for i in range(15):
            y.append(11)
        x = [i for i in range(1, self.escenario_inicial.shape[0] + 1)]
        x += x
        map_coords = zip(x, y)
        resto = 0
        for i in range(self.n_particiones):
            fams = []
            coords = []
            coord_particion = 0
            resto += (30/self.n_particiones - 30//self.n_particiones)
            if 30 % self.n_particiones != 0 and resto > 0.98:
                if resto <= 1:
                    resto = 0
                else:
                    resto = resto % 1
                rango = ceil(30/self.n_particiones)

            else:
                rango = int(30 / self.n_particiones)
            for j in range(rango):
                coord = next(map_coords)
                if j == 0:
                    coord_particion = coord
                fams.append(self.escenario_inicial.gondolas[coord])
                coords.append(coord)
            p = Particion(fams, coord_particion)
            self.particiones.update({i: p})

    def factorial(self, n):
        if n == 0:
            return 1

        return self.factorial(n-1)*n


class Optimizacion:

    def __init__(self, escenarios, t_por_p, t_max, m_por_p, m_max, n_first_step, n_second_step, n_third_step=0):
        self.escenarios = [[i, j, 0] for i, j in enumerate(escenarios)]
        self.iteracion = 0

        # criterios de eliminacion
        self.tiempo_por_producto = t_por_p
        self.tiempo_maximo = t_max
        self.metros_por_producto = m_por_p
        self.metros_maximos = m_max

        self.repeticiones = [n_first_step, n_second_step, n_third_step]

    def opt_step(self, repeticiones, step):
        pop_indexs = []
        for escenario in self.escenarios:
            print('simulando escenario', self.escenarios.index(escenario))
            tentacion, tiempo, metros, productos, hte, hm, hti = simulacionE3.run_simulacion('escenario1', debug=2, mt=1,
                                                                               mf=1, replicas=repeticiones)
            if tiempo[0]/productos[0] < self.tiempo_por_producto:

                if metros[0] < self.metros_por_producto:
                    if (step == 2 and not self.repeticiones[2]) or step == 3:
                        escenario[2] = [tentacion, tiempo, metros, productos, hte, hm, hti]
                    else:
                        escenario[2] = [tentacion]

                else:
                    print('eliminado por restriccion de metros')
                    pop_indexs.insert(0, self.escenarios.index(escenario))
            else:
                print('eliminado por restriccion de tiempo')
                pop_indexs.insert(0, self.escenarios.index(escenario))

        print('Escenarios eliminados:', pop_indexs)
        for i in pop_indexs:
            self.escenarios.pop(i)

        self.escenarios.sort(key=lambda x: x[2][0][0])
        self.escenarios.reverse()

        if step == 1:
            if len(self.escenarios) >= 10:
                self.escenarios = self.escenarios[:10]
        elif step == 2:
            if len(self.escenarios) >= 3:
                self.escenarios = self.escenarios[:3]

    def optimizar(self):

        print('\nSimulando el primer step')
        self.opt_step(self.repeticiones[0], 1)
        print('\nSimulando el segundo step')
        self.opt_step(self.repeticiones[1], 2)
        if self.repeticiones[2]:
            print('\nSimulando el tercer step')
            self.opt_step(self.repeticiones[2], 3)

    def imprimir_output(self):

        for escenario in range(len(self.escenarios)):
            tentacion, tiempo, metros, productos, hte, hm, hti = self.escenarios[escenario][2]

            mu = tentacion[0]
            S = tentacion[1]
            ci = tentacion[2]
            print('INDICE DE TENTACION - ESCENARIO {}:'.format(str(escenario)))
            print('Promedio:', mu)
            print('Desviacion standar:', sqrt(S))
            print('Intervalo de confianza:', ci)
            print()
            print('---------------------------------------------------------')
            print()
            with open('Optimizacion/estadisticos_escenario{}.txt'.format(str(escenario)), 'w') as file:
                file.write('INDICE DE TENTACION - ESCENARIO {}:\n'.format(str(escenario)))
                file.write('Promedio: {}\n'.format(mu))
                file.write('Desviacion estandar: {}\n'.format(sqrt(S)))
                file.write('Intervalo de confianza: {}\n'.format(ci))
                file.write('\n')
                file.write('---------------------------------------------------------\n\n')

            mu = tiempo[0]
            S = tiempo[1]
            ci = tiempo[2]
            print('INDICE DE TIEMPO - ESCENARIO {}:'.format(str(escenario)))
            print('Promedio:', mu)
            print('Desviacion standar:', sqrt(S))
            print('Intervalo de confianza:', ci)
            print()
            print('---------------------------------------------------------')
            print()
            with open('Optimizacion/estadisticos_escenario{}.txt'.format(str(escenario)), 'a') as file:
                file.write('INDICE DE TIEMPO - ESCENARIO {}:\n'.format(str(escenario)))
                file.write('Promedio: {}\n'.format(mu))
                file.write('Desviacion estandar: {}\n'.format(sqrt(S)))
                file.write('Intervalo de confianza: {}\n'.format(ci))
                file.write('\n')
                file.write('---------------------------------------------------------\n\n')

            mu = metros[0]
            S = metros[1]
            ci = metros[2]
            print('INDICE DE METROS - ESCENARIO {}:'.format(str(escenario)))
            print('Promedio:', mu)
            print('Desviacion standar:', sqrt(S))
            print('Intervalo de confianza:', ci)
            print()
            print('---------------------------------------------------------')
            print()
            with open('Optimizacion/estadisticos_escenario{}.txt'.format(str(escenario)), 'a') as file:
                file.write('INDICE DE METROS - ESCENARIO {}:\n'.format(str(escenario)))
                file.write('Promedio: {}\n'.format(mu))
                file.write('Desviacion estandar: {}\n'.format(sqrt(S)))
                file.write('Intervalo de confianza: {}\n'.format(ci))
                file.write('\n')
                file.write('---------------------------------------------------------\n\n')

            mu = productos[0]
            S = productos[1]
            ci = productos[2]
            print('INDICE DE TENTACION - PRODUCTOS {}:'.format(str(escenario)))
            print('Promedio:', mu)
            print('Desviacion standar:', sqrt(S))
            print('Intervalo de confianza:', ci)
            print()
            print('---------------------------------------------------------')
            print()
            with open('Optimizacion/estadisticos_escenario{}.txt'.format(str(escenario)), 'a') as file:
                file.write('INDICE DE TENTACION - PRODUCTOS {}:\n'.format(str(escenario)))
                file.write('Promedio: {}\n'.format(mu))
                file.write('Desviacion estandar: {}\n'.format(sqrt(S)))
                file.write('Intervalo de confianza: {}\n'.format(ci))
                file.write('\n')
                file.write('---------------------------------------------------------\n\n')


            histogramasAExcel.generar_histograma('', 'Optimizacion/excel_histogramas_escenario{}.xlsx'.format(str(escenario)),
                                                 optimizacion=1, te=hte, ti=hti, m=hm)


def optimizar(escenario, restriccion_tiempo_por_prodcuto, restriccion_tiempo_maximo, restriccion_metros_por_prodcuto,
              restriccion_metros_maximos, step1, step2, step3=0):
    escenario_inicial = constructorDeMapasE3.construir_mapas(escenario)[0]
    generador = Generador_escenarios(escenario_inicial, 4)
    escenarios = generador.escenarios_posibles

    opt = Optimizacion(escenarios, restriccion_tiempo_por_prodcuto, restriccion_tiempo_maximo,
                       restriccion_metros_por_prodcuto, restriccion_metros_maximos, step1, step2, step3)
    opt.optimizar()
    opt.imprimir_output()


tnow = time()
optimizar('escenario1', 999, 999, 999, 999, 30, 100)
tnow = time() - tnow
print('tiempo optimizacion:', tnow)





