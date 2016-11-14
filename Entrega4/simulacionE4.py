import simpy
import random
import constructorDeMapasE4
from scipy.sparse import coo_matrix
from numpy import mean, var, sqrt
from scipy.stats import norm
import pickle
import json
import time
import os


# CONFIGURACION_DE_FAMILIAS = 'Familias/familias'
INDICES_BOLETAS = (0, 36081)
TAMANO_DE_LA_MUESTRA = 2000
VELOCIDAD_DE_MOVIMIENTO_DE_CLIENTES = .8*60  # metros/minutos = 2.5 km/hora
TIME_OUT_CLIENTES = .00001
TIEMPO_PARA_RECOGER_UN_PRODUCTO = (.4, .6)  # uniforme(a, b)


class Supermercado:

    def __init__(self, env, tamano_muestra, indices_boletas, mapa, mapa_tiempo, mapa_flujo, velocidad_movimiento,
                 time_out_clientes, t_recoger, tiempo, debug=0, mt=1, mf=1, periodo=0):
        # simpy
        self.env = env
        self.tnow = tiempo

        # mapa del super
        self.mapa = mapa

        # canastas
        muestra = []
        with open('retail.dat', 'r') as file:
            boletas = file.readlines()[indices_boletas[0]: indices_boletas[1] + 1]
            for i in range(tamano_muestra):
                k = random.choice(boletas)
                boleta = boletas.index(k)
                muestra.append([int(j) for j in boletas[boleta].split()])
                boletas.pop(boleta)
        self.boletas = muestra
        with open('Datos/matrizProbabilidadesP{}'.format(periodo), 'rb') as file:
            self.recomendaciones = pickle.load(file)

        with open('Datos/valoresProductosP{}'.format(periodo), 'rb') as file:
            self.valores = pickle.load(file)

        with open('Datos/calvesProductosP{}'.format(periodo), 'rb') as file:
            self.claves = pickle.load(file)

        # debuguear
        self.debug = debug
        self.mt = mt
        self.mf = mf

        # parametros (crear mapa tiempo, mapa flujo)
        self.velocidad_cliente = velocidad_movimiento
        self.time_out_clientes = time_out_clientes
        self.t_recoger = t_recoger

        # elementos del supermercado
        self.clientes = []

        # empezar simulacion
        self.tnow = time.time() - self.tnow
        print('Tiempo de inicio:', self.tnow)
        self.action = self.env.process(self.run())

        # estadisticas
        self.tiempo_total_en_supermercado = []
        self.metros_totales_caminados = []
        self.total_prod_vendidos = []
        self.indice_de_tentacion = []

        # graficos y mapas
        self.mapa_calor_flujo = mapa_flujo
        self.mapa_calor_tiempo = mapa_tiempo
        self.histograma_canasta_tiempo = []
        self.histograma_canasta_caminata = []
        self.histograma_canasta_tentacion = []


    def run(self):

        # TODO HACER MAPA DE TIEMPO CON CADA CLIENTE POR SEPARADO, Y NO CON LOS QUE ESTAN DENTRO DEL SUPER

        # llegada de clientes
        for b in range(len(self.boletas)):
            yield self.env.timeout(self.time_out_clientes)
            self.env.process(self.llegada_de_cliente())

    def llegada_de_cliente(self):

        canasta = self.boletas[0]
        self.boletas.pop(0)

        # estadisticas
        self.total_prod_vendidos.append(len(canasta))

        cliente = Cliente(self.env, self, canasta)
        self.clientes.append(cliente)

        yield self.env.process(cliente.comprar())
        self.clientes.pop(self.clientes.index(cliente))

    def culcular_estadisticas(self, alpha):

        mu = mean(self.indice_de_tentacion)
        S = var(self.indice_de_tentacion, ddof=1)
        ci = norm.interval(alpha, mu, sqrt(S))
        self.indice_de_tentacion = [mu, S, ci]

        mu = mean(self.metros_totales_caminados)
        S = var(self.metros_totales_caminados, ddof=1)
        ci = norm.interval(alpha, mu, sqrt(S))
        self.metros_caminados = [mu, S, ci]

        mu = mean(self.tiempo_total_en_supermercado)
        S = var(self.tiempo_total_en_supermercado, ddof=1)
        ci = norm.interval(alpha, mu, sqrt(S))
        self.tiempo_total_en_supermercado = [mu, S, ci]

        mu = mean(self.total_prod_vendidos)
        S = var(self.total_prod_vendidos, ddof=1)
        ci = norm.interval(alpha, mu, sqrt(S))
        self.total_prod_vendidos = [mu, S, ci]


class Cliente:
    id = 0

    def __init__(self, env, super, canasta):

        # elementos super
        self.super = super
        self.env = env
        self.id = Cliente.id

        # debug: observar lo que hace el cliente 0
        if self.super.debug == 1 and Cliente.id == 0:
            self.debug = 1
        else:
            self.debug = 0
        #print(Cliente.id)
        Cliente.id += 1

        # productos
        self.canasta_base = canasta
        self.canasta_inicial = list(i for i in canasta)
        self.len_canasta = len(self.canasta_base)
        self.productos_tentacion = set()
        self.productos_restantes = len(self.canasta_base)

        # estado posicion
        # entra en la posicion (x, 1), 1 <= x <= 6
        self.coord_actual = (random.randint(1, 6), 1)
        self.nodo_actual = (1, 1)

        # debug
        if self.debug == 1:
            print('coord incial de cliente', self.id, ': ', self.coord_actual)
            print('canasta inicial cliente', self.id, ': ', self.canasta_base)
            print('largo canasta inicial:', self.len_canasta)
            print('---------------------------------------------------------')

        # parametros cliente
        self.velocidad_cliente = self.super.velocidad_cliente  # metro/minutos = 2.5 km/hora

        # mapa calor - camino de cliente en el super
        self.ubicacion_cliente = []

        # estado del cliente
        self.siguiente_producto = -1
        self.siguiente_producto_id = -1
        self.camino_a_siguiente_producto = []
        self.det_siguiente_producto()  # determina camino y tiempo al sig producto

        # camino recorrido en todo el supermercado
        self.camino_en_supermercado = []

        # estadisticas
        self.metros_caminados = 0
        self.tiempo_en_el_super = 0

    def det_siguiente_producto(self):
        if self.productos_restantes:
            id = self.canasta_base[0]
            self.siguiente_producto_id = id
            coord_siguiente_producto = self.super.mapa.productos[self.super.valores[self.siguiente_producto_id]].coord_cliente
            distancia = abs(coord_siguiente_producto[0] - self.coord_actual[0]) + abs(coord_siguiente_producto[1] - self.coord_actual[1])

            if self.productos_restantes > 1:
                for i in range(1, len(self.canasta_base)):
                    id = self.canasta_base[i]
                    id = self.super.valores[id]
                    prod_i = self.super.mapa.productos[id].coord_cliente

                    distancia_i = abs(prod_i[0] - self.coord_actual[0]) + abs(prod_i[1] - self.coord_actual[1])
                    if distancia_i < distancia:
                        coord_siguiente_producto = prod_i
                        distancia = distancia_i
                        self.siguiente_producto_id = self.super.claves[id]

            self.productos_restantes -= 1

            self.canasta_base.pop(self.canasta_base.index(self.siguiente_producto_id))

            self.siguiente_producto = coord_siguiente_producto
            nodo_prod = self.super.mapa.coordenadas[coord_siguiente_producto].nodo

            # calcular camino de nodos
            camino_nodos = self.super.mapa.dijkstra_nodos(self.super.mapa.coordenadas[self.coord_actual].nodo.coord,
                                                          nodo_prod.coord)
            self.camino_nodos = camino_nodos

            # agregar productos tentados
            for n in self.camino_nodos:
                n1 = (n[0], n[1] + 1)
                n2 = n
                n3 = (n[0], n[1] - 1)
                nodos = [n1, n2, n3]
                for nod in nodos:
                    try:
                        self.productos_tentacion = self.productos_tentacion.union(self.super.mapa.nodos[nod].productos_tentacion)
                    except KeyError:
                        pass

            # camino desde posicion del cliente hasta coordenada del producto
            # GENERA UN CAMINO CON LOS VERTICES DONDE EL CLIENTE DOBLA
            self.camino_a_siguiente_producto = self.super.mapa.generar_camino_de_coordenadas(self.coord_actual,
                                                                                             coord_siguiente_producto,
                                                                                             camino_nodos)

            # actualizar mapa de calor-flujo de clientes en el supermercado
            if self.super.mf:
                for coord in self.camino_a_siguiente_producto[:-1]:
                    self.super.mapa_calor_flujo.coordenadas[coord].calor += 1

            # actualizar coordd cliente una vez que llegue al producto (coord en el fututro)
            self.coord_actual = self.camino_a_siguiente_producto[-1]
            self.tiempo_hasta_llegar_al_siguiente_producto = (len(self.camino_a_siguiente_producto) - 1)/self.velocidad_cliente
        else:
            self.siguiente_producto = False

    def comprar(self):

        # llegar y comprar
        i = 1
        while True:
            if self.siguiente_producto:
                if self.debug == 1:
                    print('iteracion: ', i)
                    print('id siguiente producto: ', self.siguiente_producto_id)
                    print('coord siguiente producto: ', self.siguiente_producto)
                    print('camino de nodos a siguiente producto: ', self.camino_nodos)
                    print('camino coords a siguiente producto cliente', self.id, ': ', self.camino_a_siguiente_producto)

                # CALCULO DEL CAMINO DE COORDENADAS HASTA EL SIGUIENTE PRODUCTO
                def determinar_largo_y_ubicacion():
                    # ubicacion_ciente contiene el camino de todos las coordenadas que pisa el cliente
                    self.ubicacion_cliente = []
                    for i in range(len(self.camino_a_siguiente_producto)-1):
                        c0 = self.camino_a_siguiente_producto[i]
                        c1 = self.camino_a_siguiente_producto[i+1]
                        # llego al producto
                        if c0 == c1:
                            continue
                        # avanza verticalmente
                        elif c0[0] == c1[0]:
                            metros = abs(c0[1] - c1[1])
                            for j in range(metros):
                                l = len(self.ubicacion_cliente)
                                if c0[1] > c1[1]:
                                    self.ubicacion_cliente.append((c0[0], c0[1] - j))
                                else:
                                    self.ubicacion_cliente.append((c0[0], c0[1] + j))
                        # avanza horizontalmente
                        elif c0[1] == c1[1]:
                            metros = abs(c0[0] - c1[0])
                            for j in range(metros):
                                l = len(self.ubicacion_cliente)
                                if c0[0] > c1[0]:
                                    self.ubicacion_cliente.append((c0[0] - j, c0[1]))
                                else:
                                    self.ubicacion_cliente.append((c0[0] + j, c0[1]))
                        else:
                            print('error de camino de cliente')
                            exit()

                    l = len(self.ubicacion_cliente)  # largo del camino hasta el siguiente producto
                    self.ubicacion_cliente.append(self.camino_a_siguiente_producto[-1])  # ultima posicion

                    if self.debug == 1:
                        print('camino cliente', self.ubicacion_cliente)

                determinar_largo_y_ubicacion()
                self.camino_en_supermercado.append(self.ubicacion_cliente)

                # determinar siguiente producto
                self.det_siguiente_producto()

                # TODO DETERMINAR TIEMPO TOTAL EN EL SUPERMERCADO -> TIEMPO QUE DURA LA CAMMINATA +
                # TIEMPO QUE DEMORA EN RECOGER LOS PRODUCTOS

                if self.debug == 1:
                    print('---------------------------------------------------------')
            else:
                break
            i += 1
        # salir - caminar a caja
        # actualizar camino
        self.ubicacion_cliente = []
        c0 = self.coord_actual
        c1 = (self.coord_actual[0], 1)
        metros = abs(c0[1] - c1[1])
        for j in range(metros):
            l = len(self.ubicacion_cliente)
            self.ubicacion_cliente.append((c0[0], c0[1] - j))
        self.ubicacion_cliente.append(c1)
        if self.debug == 1:
            print('camino a la salida:', self.ubicacion_cliente)
            print('---------------------------------------------------------')
        self.camino_en_supermercado.append(self.ubicacion_cliente)

        # CALCULO DE MAPA DE FLUJO Y DE TIEMPO
        # mapa de flujo
        if self.super.mf:
            for camino in self.camino_en_supermercado:
                if self.camino_en_supermercado.index(camino) == 0:
                    self.super.mapa_calor_flujo.coordenadas[camino[0]].calor += 1
                    self.metros_caminados += 1
                for i in range(1, len(camino)):
                    self.super.mapa_calor_flujo.coordenadas[camino[i]].calor += 1
                    self.metros_caminados += 1

        #mapa de tiempo
        if self.super.mt:
            for camino in self.camino_en_supermercado:
                if self.camino_en_supermercado.index(camino) == 0:
                    self.super.mapa_calor_tiempo.coordenadas[camino[0]].calor += 1/self.velocidad_cliente
                    self.tiempo_en_el_super += 1/self.velocidad_cliente
                for i in range(1, len(camino)-1):
                    self.super.mapa_calor_tiempo.coordenadas[camino[i]].calor += 1/self.velocidad_cliente
                    self.tiempo_en_el_super += 1/self.velocidad_cliente
                if self.camino_en_supermercado.index(camino) != len(self.camino_en_supermercado) - 1:
                    tiempo_para_recoger = random.uniform(self.super.t_recoger[0], self.super.t_recoger[1])
                    self.super.mapa_calor_tiempo.coordenadas[camino[-1]].calor += tiempo_para_recoger
                    self.tiempo_en_el_super += tiempo_para_recoger
                else:
                    self.super.mapa_calor_tiempo.coordenadas[camino[-1]].calor += 1 / self.velocidad_cliente
                    self.tiempo_en_el_super += 1 / self.velocidad_cliente

        # ESTADISTICAS
        if self.debug == 1:
            print('tiempo en el super:', self.tiempo_en_el_super)
            print('metros caminados:', self.metros_caminados)
            t_recogiendo = (self.super.t_recoger[0]+self.super.t_recoger[1])/2
            print('esperanza tiempo recogiendo + tiempo caminando:',
                  self.len_canasta*t_recogiendo + self.metros_caminados/self.velocidad_cliente )
            print('---------------------------------------------------------')

        self.super.tiempo_total_en_supermercado.append(self.tiempo_en_el_super)
        self.super.metros_totales_caminados.append(self.metros_caminados)
        self.super.histograma_canasta_tiempo.append((self.len_canasta, self.tiempo_en_el_super))
        self.super.histograma_canasta_caminata.append((self.len_canasta, self.metros_caminados))
        # calcular indice de tentacion

        def generar_vector_boleta(boleta):
            data = []
            row = []
            col = []
            for p in boleta:
                data.append(1)
                row.append(p)
                col.append(0)
            boleta = coo_matrix((data, (row, col)), shape=(12750, 1), dtype='f')
            return boleta

        for i in range(len(self.canasta_inicial)):
            self.canasta_inicial[i] = self.super.valores[self.canasta_inicial[i]]

        boleta = generar_vector_boleta(self.canasta_inicial)
        vector_recomendaciones = self.super.recomendaciones.dot(boleta)
        vector_vistos = generar_vector_boleta(self.productos_tentacion)
        indice_tentacion = vector_recomendaciones.transpose().dot(vector_vistos)

        self.super.indice_de_tentacion.append(indice_tentacion[0,0])
        self.super.histograma_canasta_tentacion.append((self.len_canasta, indice_tentacion[0,0]))
        if self.debug == 1:
            print('Indice tentacion')
            print(indice_tentacion[0,0])
            print('---------------------------------------------------------')

        # EL CLIENTE SE ELIMINA UNA VEZ QUE SALE DEL SUPER EN EL MAIN THREAD
        yield self.env.timeout(self.super.time_out_clientes)



def run_simulacion(escenario, debug=0,mt=1, mf=1, replicas=TAMANO_DE_LA_MUESTRA, tnow=time.time(), periodo=0, indices=(0,0),
                   velocidad=0):

    #  una replica - describe lo que hace el primer cliente
    if debug == 1:
        # abrir archivo de escenario
        mapa, mapa_de_tiempo, mapa_de_flujo = constructorDeMapasE3.construir_mapas(escenario)

        '''Simulacion'''
        env = simpy.Environment()
        super = Supermercado(env, TAMANO_DE_LA_MUESTRA, INDICES_BOLETAS, mapa, mapa_de_tiempo, mapa_de_flujo,
                             VELOCIDAD_DE_MOVIMIENTO_DE_CLIENTES, TIME_OUT_CLIENTES, TIEMPO_PARA_RECOGER_UN_PRODUCTO,
                             tnow, debug, mt, mf)
        env.run()

        print('tiempo simulacion: ', (time.time()- tnow)/60, 'min')

    if debug == 0:
        # abrir archivo de escenario
        mapa, mapa_de_tiempo, mapa_de_flujo = constructorDeMapasE3.construir_mapas(escenario)

        '''Simulacion'''
        env = simpy.Environment()
        super = Supermercado(env, TAMANO_DE_LA_MUESTRA, INDICES_BOLETAS, mapa, mapa_de_tiempo, mapa_de_flujo,
                             VELOCIDAD_DE_MOVIMIENTO_DE_CLIENTES, TIME_OUT_CLIENTES, TIEMPO_PARA_RECOGER_UN_PRODUCTO,
                             tnow, debug, mt, mf)
        env.run()
        super.culcular_estadisticas(.95)
        print('tiempo simulacion: ', (time.time() - tnow) / 60, 'min')

        if not os.path.exists('Output/{}'.format(escenario)):
            os.makedirs('Output/{}'.format(escenario))

        # ESTADISTICAS
        histograma_canasta_tiempo = super.histograma_canasta_tiempo
        histograma_canasta_caminata = super.histograma_canasta_caminata
        histograma_canasta_tentacion = super.histograma_canasta_tentacion
        if mt:
            mapa_calor_tiempo = super.mapa_calor_tiempo
        if mf:
            mapa_calor_flujo = super.mapa_calor_flujo


        # INDICE DE TENTACION
        mu = super.indice_de_tentacion[0]
        S = super.indice_de_tentacion[1]
        ci = super.indice_de_tentacion[2]
        print('INDICE DE TENTACION:')
        print('Promedio:', mu)
        print('Desviacion standar:', sqrt(S))
        print('Intervalo de confianza:', ci)
        print()
        print('---------------------------------------------------------')
        print()

        with open('Output/{}/estadisticos.txt'.format(escenario), 'w') as file:
            file.write('INDICE DE TENTACION:\n')
            file.write('Promedio: {}\n'.format(mu))
            file.write('Desviacion estandar: {}\n'.format(sqrt(S)))
            file.write('Intervalo de confianza: {}\n'.format(ci))
            file.write('\n')
            file.write('---------------------------------------------------------\n\n')

        # METROS CAMINADOS
        mu = super.metros_caminados[0]
        S = super.metros_caminados[1]
        ci = super.metros_caminados[2]
        print('METROS CAMINADOS:')
        print('Promedio:', mu)
        print('Desviacion standar:', sqrt(S))
        print('Intervalo de confianza:', ci)
        print()
        print('---------------------------------------------------------')
        print()

        with open('Output/{}/estadisticos.txt'.format(escenario), 'a') as file:
            file.write('METROS CAMINADOS:\n')
            file.write('Promedio: {} metros\n'.format(mu))
            file.write('Desviacion estandar: {} metros\n'.format(sqrt(S)))
            file.write('Intervalo de confianza: {} metros\n'.format(ci))
            file.write('\n')
            file.write('---------------------------------------------------------\n\n')

        # TIEMPO EN SUPERMERCADO
        mu = super.tiempo_total_en_supermercado[0]
        S = super.tiempo_total_en_supermercado[1]
        ci = super.tiempo_total_en_supermercado[2]
        print('TIEMPO EN SUPERMERCADO:')
        print('Promedio:', mu)
        print('Desviacion standar:', sqrt(S))
        print('Intervalo de confianza:', ci)
        print()
        print('---------------------------------------------------------')
        print()

        with open('Output/{}/estadisticos.txt'.format(escenario), 'a') as file:
            file.write('TIEMPO EN SUPERMERCADO:\n')
            file.write('Promedio: {} minutos\n'.format(mu))
            file.write('Desviacion estandar: {} minutos\n'.format(sqrt(S)))
            file.write('Intervalo de confianza: {} minutos\n'.format(ci))
            file.write('\n')
            file.write('---------------------------------------------------------\n\n')

        # PRODUCTOS VENDIDOS
        mu = super.total_prod_vendidos[0]
        S = super.total_prod_vendidos[1]
        ci = super.total_prod_vendidos[2]
        print('PRODUCTOS VENDIDOS:')
        print('Promedio:', mu)
        print('Desviacion standar:', sqrt(S))
        print('Intervalo de confianza:', ci)
        print()
        print('---------------------------------------------------------')
        print()

        with open('Output/{}/estadisticos.txt'.format(escenario), 'a') as file:
            file.write('PRODUCTOS VENDIDOS:\n')
            file.write('Promedio: {}\n'.format(mu))
            file.write('Desviacion estandar: {}\n'.format(sqrt(S)))
            file.write('Intervalo de confianza: {}\n'.format(ci))
            file.write('\n')
            file.write('---------------------------------------------------------\n\n')

        # ESCRIBIR HISTOGRAMAS Y MAPAS
        with open('Output/{}/histograma_canasta_tentacion'.format(escenario), 'wb') as file:
            pickle.dump(histograma_canasta_tentacion, file)
        with open('Output/{}/histograma_canasta_caminata'.format(escenario), 'wb') as file:
            pickle.dump(histograma_canasta_caminata, file)
        with open('Output/{}/histograma_canasta_tiempo'.format(escenario), 'wb') as file:
            pickle.dump(histograma_canasta_tiempo, file)

        if mt:
            with open('Output/{}/mapa_calor_tiempo.json'.format(escenario), 'w') as file:
                d = {}
                for i in mapa_calor_tiempo.coordenadas:
                    d.update({str(i): mapa_calor_tiempo.coordenadas[i].calor})
                json.dump(d, file)
        if mf:
            with open('Output/{}/mapa_calor_flujo.json'.format(escenario), 'w') as file:
                d = {}
                for i in mapa_calor_flujo.coordenadas:
                    d.update({str(i): mapa_calor_flujo.coordenadas[i].calor})
                json.dump(d, file)

    # opti
    if debug == 2:
        mapa = escenario[0]
        mapa_de_tiempo = escenario[1]
        mapa_de_flujo = escenario[2]
        '''Simulacion'''
        env = simpy.Environment()
        super = Supermercado(env, replicas, indices, mapa, mapa_de_tiempo, mapa_de_flujo,
                             velocidad, TIME_OUT_CLIENTES, TIEMPO_PARA_RECOGER_UN_PRODUCTO,
                             tnow, debug, mt, mf, periodo=periodo)
        env.run()
        super.culcular_estadisticas(.9)

        return super.indice_de_tentacion, super.tiempo_total_en_supermercado, super.metros_caminados,\
               super.total_prod_vendidos,  super.histograma_canasta_tentacion, super.histograma_canasta_caminata, \
               super.histograma_canasta_tiempo

    # benchmark
    if debug == 3:
        mapa, mapa_de_tiempo, mapa_de_flujo = constructorDeMapasE4.construir_mapas(escenario, periodo=periodo)

        '''Simulacion'''
        env = simpy.Environment()
        super = Supermercado(env, replicas, INDICES_BOLETAS, mapa, mapa_de_tiempo, mapa_de_flujo,
                             VELOCIDAD_DE_MOVIMIENTO_DE_CLIENTES, TIME_OUT_CLIENTES, TIEMPO_PARA_RECOGER_UN_PRODUCTO,
                             tnow, debug, mt, mf)
        env.run()
        super.culcular_estadisticas(.9)

        return super.indice_de_tentacion, super.tiempo_total_en_supermercado, super.metros_caminados, \
               super.total_prod_vendidos, super.histograma_canasta_tentacion, super.histograma_canasta_caminata, \
               super.histograma_canasta_tiempo

