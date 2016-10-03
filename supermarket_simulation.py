import simpy
import random
from mapa_super import MapaDeCalor, Mapa
import numpy as np
import scipy.stats as st
import json
import time


hora_de_inicio = 8  # horas
hora_de_termino = 20  # horas
tasa_de_llegada = [50, 100, 100, 100, 80, 80, 50, 50, 80, 100, 100, 100]  # clientes/hora
numero_de_cajas_abiertas = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] # en c/hora
escenario = 'families'


NUMERO_DE_REPLICAS = 10


'''---------------------------------Super--------------------------------------------'''


class Supermercado:

    def __init__(self, env, mapa, tasa, canastas_basicas, mapa_calor, debug=-1):
        self.env = env

        self.mapa = mapa
        self.canastas = canastas_basicas
        self.mapa_calor = mapa_calor

        self.debug = debug

        self.tasa_de_llegada = tasa
        self.clientes = {}
        self.clientes_dentro_del_supermercado = []
        self.venta_productos = {}
        for i in range(16470):
            self.venta_productos.update({i: 0})

        # variables de estado
        self.clientes_en_el_super = 0

        # variables de output
        self.productos_vendidos = 0
        self.clientes_totales = 0

        # simulacion
        self.action = self.env.process(self.run())

        # estadisticas
        self.tiempo_total_en_supermercado = 0
        self.metros_totales_caminados = 0
        self.total_prod_vendidos = 0
        self.histograma_canasta_tiempo = []
        self.histograma_canasta_caminata = []
        self.ventas_por_sku = []

        #lista = []
        #for i in range(16470):
        #    try:
        #        self.mapa.productos[i]
        #        lista.append(i)
        #    except KeyError:
        #        pass
        #for i in lista:
        #    self.ventas_por_sku[i] = 0

    def run(self):
        self.env.process(self.actualizar_mapa_calor())
        while True:
            tiempo_entre_llegadas = random.expovariate(self.tasa_de_llegada[int(round(self.env.now//60 - 8))]/60)
            yield self.env.timeout(tiempo_entre_llegadas)
            self.env.process(self.llegada_de_cliente())
            self.clientes_en_el_super += 1
            self.clientes_totales += 1

    def actualizar_mapa_calor(self):
        if self.debug >= 0:
            self.calor_cliente_i = {}
        while True:
            yield self.env.timeout(.4)  # cada .4 segundos aactualiza mapa calor
            for cliente in self.clientes_dentro_del_supermercado:
                if not cliente.recogiendo:
                    calor = cliente.ubicacion_actual()
                    if self.debug >= 0 and cliente.id == self.debug:
                        self.mapa_calor.coordenadas_mapa_calor_un_cliente[calor].calor += 1
                else:
                    calor = cliente.coord_actual
                self.mapa_calor.coordenadas[calor].calor += 1
                if self.debug >= 0 and cliente.id == self.debug:
                    self.mapa_calor.coordenadas_mapa_calor_un_cliente[calor].calor += 1

    def llegada_de_cliente(self):
        # en los ultimos 15 minutos no puedde entrar nade que haga una compra mas grande que 10 min
        if hora_de_termino*60 - 30 > self.env.now:

            index_canasta = random.randint(0, len(self.canastas) - 1)
            canasta = self.canastas[index_canasta]
            # eliminar productos que no estan en el super
            i = 0
            lista_pop= []
            for prod in canasta:
                try:
                    self.mapa.productos[prod]
                except KeyError:
                    lista_pop.append(i)
                i += 1
            lista_pop.reverse()
            for j in lista_pop:
                canasta.pop(j)

            # estadisticas
            self.total_prod_vendidos += len(canasta)
            for p in canasta:
                self.ventas_por_sku.append((p, 1))

            cliente = Cliente(self.env, self, canasta, self.env.now, self.debug)
            self.canastas.pop(index_canasta)
            self.clientes[cliente.id] = cliente
            self.clientes_dentro_del_supermercado.append(cliente)

            yield self.env.process(cliente.comprar())

    def hora(self, now):
        return str(round(now//60)) + ':' + str(round(now%60)) if len(str(round(now%60))) == 2 \
            else str(round(now//60)) + ':0' + str(round(now%60))


class Cliente:
    id = 0

    def __init__(self, env, super, canasta, timenow, debug=0):
        self.super = super
        self.env = env
        self.id = Cliente.id
        self.debug = self.id == debug
        Cliente.id += 1

        # productos
        self.canasta_base = canasta
        self.len_canasta = len(canasta)

        # estado posicion
        self.coord_actual = (random.randint(1, 6), 1)
        if self.debug:
            print('coord incial de cliente', self.id, ': ', self.coord_actual)
            print('canasta inicial cliente', self.id, ': ', self.canasta_base)
        self.nodo_actual = (1, 1)
        #self.pasillo_actual = 0
        self.velocidad_cliente = .8*60  # metro/minutos = 2.5 km/hora
        self.tiempo_de_llegada = timenow  # en minutos
        self.tiempo_de_salida = -1

        # mapa calor
        self.ubicacion_cliente = {}
        self.tiempo_inicio_camino = timenow
        self.recogiendo = False

        # estado del cliente
        self.tiempo_ultima_actualizacion = -1
        self.siguiente_producto = -1
        self.siguiente_producto_id = -1
        self.tiempo_al_siguiente_producto = 0  # depende del largo del camino
        self.metros_hasta_el_siguiente_producto = 0
        self.camino_a_siguiente_producto = []
        self.tiempo_en_el_super = 0
        self.det_siguiente_producto()  # determina camino y tiempo al sig producto
        self.tiempo_ultima_actualizacion = self.env.now
        self.salio_del_super = False

        # estadisticas
        self.metros_caminados = 0
        self.tiempo_estadia_total = 0
        self.cantindad_productos_comprados = 0
        self.canasta_tentados = []

    def generar_canasta(self):  # canasta inicial (si la generamos aleatoriamente)
        pass

    def det_siguiente_producto(self):  # todo arreglar error de key de producto que no esta en ls 12750
        if self.canasta_base:
            id = self.canasta_base[0]
            self.siguiente_producto_id = id
            coord_siguiente_producto = self.super.mapa.productos[id].coord_cliente
            distancia = abs(coord_siguiente_producto[0] - self.coord_actual[0]) + abs(coord_siguiente_producto[1] - self.coord_actual[1])

            if len(self.canasta_base) > 1:
                for i in range(1, len(self.canasta_base)):
                    id = self.canasta_base[i]
                    prod_i = self.super.mapa.productos[id].coord_cliente
                    distancia_i = abs(prod_i[0] -self.coord_actual[0]) + abs(prod_i[1] -self.coord_actual[1])
                    if distancia_i < distancia:
                        coord_siguiente_producto = prod_i
                        distancia = distancia_i
                        self.siguiente_producto_id = id

            self.canasta_base.pop(self.canasta_base.index(self.siguiente_producto_id))

            self.siguiente_producto = coord_siguiente_producto
            nodo_prod = self.super.mapa.coordenadas[coord_siguiente_producto].nodo

            # calcular camino de nodos
            camino_nodos = self.super.mapa.dijkstra_nodos(self.super.mapa.coordenadas[self.coord_actual].nodo.coord,
                                                          nodo_prod.coord)
            self.camino_nodos = camino_nodos

            # camino desde posicion del cliente hasta coordenada del producto
            self.camino_a_siguiente_producto = self.super.mapa.generar_camino_de_coordenadas(self.coord_actual,
                                                                                             coord_siguiente_producto,
                                                                                             camino_nodos)
            # actualizar coordd cliente una vez que llegue al producto (coord en el fututro)
            self.coord_actual = self.camino_a_siguiente_producto[-1]
            self.tiempo_hasta_llegar_al_siguiente_producto = (len(self.camino_a_siguiente_producto) - 1)/self.velocidad_cliente
        else:
            self.siguiente_producto = False

    def ubicacion_actual(self):
        tiempo_transcurrido = self.env.now - self.tiempo_inicio_camino
        posicion_actual_cliente = self.ubicacion_cliente[round(tiempo_transcurrido)]
        return posicion_actual_cliente

    def comprar(self):

        # llegar y comprar
        i = 1
        while True:
            if self.siguiente_producto:
                if self.debug:
                    print('iteracion: ', i)
                    print('id siguiente producto: ', self.siguiente_producto_id)
                    print('canasta base cliente', self.id, ': ', self.canasta_base)
                    print('coord siguiente producto: ', self.siguiente_producto)
                    print('camino de nodos a siguiente producto: ', self.camino_nodos)
                    print('camino coords a siguiente prod cliente', self.id, ': ', self.camino_a_siguiente_producto)

                # calculo largo del camino y calculo del camino de calor
                def determinar_largo_y_ubicacion():
                    self.ubicacion_cliente = {}
                    self.metros_hasta_el_siguiente_producto = 0
                    for i in range(len(self.camino_a_siguiente_producto)-1):
                        c0 = self.camino_a_siguiente_producto[i]
                        c1 = self.camino_a_siguiente_producto[i+1]
                        if c0 == c1:
                            continue
                        elif c0[0] == c1[0]:
                            metros = abs(c0[1] - c1[1])
                            self.metros_hasta_el_siguiente_producto += metros
                            for j in range(metros):
                                l = len(self.ubicacion_cliente)
                                if c0[1] > c1[1]:
                                    self.ubicacion_cliente.update({l: (c0[0], c0[1] - j)})
                                else:
                                    self.ubicacion_cliente.update({l: (c0[0], c0[1] + j)})
                        elif c0[1] == c1[1]:
                            metros = abs(c0[0] - c1[0])
                            self.metros_hasta_el_siguiente_producto += metros
                            for j in range(metros):
                                l = len(self.ubicacion_cliente)
                                if c0[0] > c1[0]:
                                    self.ubicacion_cliente.update({l: (c0[0] - j, c0[1])})
                                else:
                                    self.ubicacion_cliente.update({l: (c0[0] + j, c0[1])})
                        else:
                            print('error de camino de cliente')
                            exit()

                    l = len(self.ubicacion_cliente)
                    self.ubicacion_cliente.update({l: self.camino_a_siguiente_producto[-1]})

                    if self.debug:
                        print('ubicacion cliente', self.ubicacion_cliente)

                    self.metros_caminados += self.metros_hasta_el_siguiente_producto
                    self.cantindad_productos_comprados += 1
                determinar_largo_y_ubicacion()

                # caminar a siguiente producto
                self.tiempo_hasta_llegar_al_siguiente_producto = self.metros_hasta_el_siguiente_producto/self.velocidad_cliente
                self.tiempo_en_el_super += self.tiempo_hasta_llegar_al_siguiente_producto
                self.tiempo_inicio_camino = self.env.now
                yield self.env.timeout(self.tiempo_hasta_llegar_al_siguiente_producto)

                # determinar siguiente producto
                self.det_siguiente_producto()

                # recoger_producto
                tiempo_recoger =random.uniform(.4, .6)
                self.tiempo_en_el_super += tiempo_recoger
                self.recogiendo = True
                yield self.env.timeout(tiempo_recoger)  # ~30 sen recoger el producto
                self.recogiendo = False
                try:
                    self.super.venta_productos[self.siguiente_producto] += 1
                except KeyError:
                    self.super.venta_productos[self.siguiente_producto] = 1
            else:
                break
            i += 1
        # salir - caminar a caja
        self.tiempo_en_el_super += abs(1 - self.coord_actual[1])/self.velocidad_cliente
        self.metros_caminados += abs(1 - self.coord_actual[1])
        # actualizar camino
        self.ubicacion_cliente = {}
        c0 = self.coord_actual
        c1 = (self.coord_actual[0], 1)
        metros = abs(c0[1] - c1[1])
        for j in range(metros):
            l = len(self.ubicacion_cliente)
            self.ubicacion_cliente.update({l: (c0[0], c0[1] - j)})
        self.ubicacion_cliente.update({len(self.ubicacion_cliente): c1})
        yield self.env.timeout(abs(1 - self.coord_actual[1])/self.velocidad_cliente)  #camina recto hacia abajo

        # sacar al cliente del super
        self.super.clientes_en_el_super -= 1
        self.super.clientes_dentro_del_supermercado.pop(self.super.clientes_dentro_del_supermercado.index(self))
        self.salio_del_super = True

        # estadisticas
        self.tiempo_de_salida = self.env.now
        if self.debug:
            print('tiempo en el super:', self.tiempo_en_el_super)

            print('metros caminados:', self.metros_caminados)

        self.super.tiempo_total_en_supermercado += self.tiempo_en_el_super
        self.super.metros_totales_caminados += self.metros_caminados
        self.super.histograma_canasta_tiempo.append((self.len_canasta, self.tiempo_en_el_super))
        self.super.histograma_canasta_caminata.append((self.len_canasta, self.metros_caminados))


'''generar canastas basicas a partir de boletas en bdd'''
canastas_basicas = []
with open('retail.dat', 'r') as file:
    lista = file.readlines()
    j=0
    for p in lista:
        j+=1
        productos = p.split()
        for i in range(len(productos)):
            productos[i] = int(productos[i])
        canastas_basicas.append(productos)

def run_simulacion(replicas, tasa_de_llegada, canastas_basicas, escenario, debug=-1):
    if debug > 0:

        tnow = time.time()

        with open('{}.json'.format(escenario)) as file:
            families = json.load(file)
        families.reverse()

        mapa = Mapa(15, 19, (f for f in families))
        mapa_de_calor = MapaDeCalor(mapa)

        '''Simulacion'''
        env = simpy.Environment(hora_de_inicio*60)
        super = Supermercado(env, mapa, tasa_de_llegada, canastas_basicas, mapa_de_calor, debug)
        env.run(until=hora_de_termino*60)

        '''mapa calor de un cliente'''
        #for c in super.mapa_calor.coordenadas_mapa_calor_un_cliente:
        #    if super.mapa_calor.coordenadas_mapa_calor_un_cliente[c].calor:
        #        print(c, ':', super.mapa_calor.coordenadas_mapa_calor_un_cliente[c].calor)

        '''Output'''
        print('metros caminados cliente: ', super.clientes[0].metros_caminados)
        print('tiempo en el super cliente: ', super.clientes[0].tiempo_estadia_total)
        print('super vacio al termino de simulacion:', super.clientes_en_el_super == 0)

        with open('mapa_de_calor.json', 'w') as file:
            d = {}
            for i in super.mapa_calor.coordenadas:
                d.update({str(i): super.mapa_calor.coordenadas[i].calor})
            json.dump(d, file)
        with open('mapa_de_calor_un_cliente.json', 'w') as file:
            d = {}
            for i in super.mapa_calor.coordenadas_mapa_calor_un_cliente:
                d.update({str(i): super.mapa_calor.coordenadas_mapa_calor_un_cliente[i].calor})
            json.dump(d, file)
        print('tiempo simulacion: ', (time.time()- tnow)/60, 'min')

    if debug < 0:

        #ventas_skus = {}
        #lista = []
        #for i in range(16470):
        #    try:
        #        mapa.productos[i]
        #        lista.append(i)
        #    except KeyError:
        #        pass
        #for i in lista:
        #   ventas_skus[i] = []

        with open('{}.json'.format(escenario)) as file:
            families = json.load(file)
        families.reverse()

        mapa = Mapa(15, 19, (f for f in families))
        mapa_de_calor = MapaDeCalor(mapa)

        unidades_vendidas = []
        distancia_recorrida = []
        tiempo_promedio = []
        clientes_promedio = []
        vendidos_por_clientes = []
        histograma_canasta_tiempo = {}
        histograma_canasta_metros = {}
        ventas_por_sku = {}
        mapaCalor = MapaDeCalor(mapa)

        for r in range(replicas):
            tnow = time.time()
            '''Simulacion'''
            env = simpy.Environment(hora_de_inicio*60)
            super = Supermercado(env, mapa, tasa_de_llegada, canastas_basicas, mapa_de_calor, debug)
            env.run(until=hora_de_termino*60)

            print('tiempo simulacion',r, ':', (time.time()- tnow)/60, 'min')

            for dato in super.histograma_canasta_caminata:
                try:
                    histograma_canasta_metros[dato[0]] += 1/NUMERO_DE_REPLICAS
                except KeyError:
                    histograma_canasta_metros[dato[0]] = 1/NUMERO_DE_REPLICAS

            for dato in super.histograma_canasta_tiempo:
                try:
                    histograma_canasta_tiempo[dato[0]] += 1/NUMERO_DE_REPLICAS
                except KeyError:
                    histograma_canasta_tiempo[dato[0]] = 1/NUMERO_DE_REPLICAS

            for dato in super.ventas_por_sku:
                try:
                    ventas_por_sku[dato] += 1/NUMERO_DE_REPLICAS
                except KeyError:
                    ventas_por_sku[dato] = 1/NUMERO_DE_REPLICAS

            for dato in super.mapa_calor.coordenadas:
                mapaCalor.coordenadas[dato].calor += super.mapa_calor.coordenadas[dato].calor/NUMERO_DE_REPLICAS

            unidades_vendidas.append(super.total_prod_vendidos)
            distancia_recorrida.append(super.metros_totales_caminados/super.clientes_totales)
            tiempo_promedio.append(super.tiempo_total_en_supermercado/super.clientes_totales)
            clientes_promedio.append(super.clientes_totales)
            vendidos_por_clientes.append(super.total_prod_vendidos/super.clientes_totales)

        # calcular intervalos de confianza
        # distancia_recorrida
        mu = np.mean(distancia_recorrida)
        S = np.var(distancia_recorrida, ddof=1)
        ci = st.t.interval(0.95, NUMERO_DE_REPLICAS - 1, mu, np.sqrt(S))
        print('Distancia recorrida:')
        print('Promedio:', mu)
        print('Desviacion standar:', np.sqrt(S))
        print('Intervalo de confianza:', ci)
        print()

        with open('KPIs {}.txt'.format(escenario), 'w') as file:
            file.write('Distancia recorrida:\n)')
            file.write('Promedio: {}\n'.format(mu))
            file.write('Desviacion standar: {}\n'.format(np.sqrt(S)))
            file.write('Intervalo de confianza: {}\n'.format(ci))

        # tiempo_promedio
        mu = np.mean(tiempo_promedio)
        S = np.var(tiempo_promedio, ddof=1)
        ci = st.t.interval(0.95, NUMERO_DE_REPLICAS - 1, mu, np.sqrt(S))
        print('Tiempo promedio dentro del supermercado:')
        print('Promedio:', mu)
        print('Desviacion standar: ', np.sqrt(S))
        print('Intervalo de confianza:', ci)
        print()

        with open('KPIs {}.txt'.format(escenario), 'a') as file:
            file.write('Tiempo promedio dentro del supermercado:\n)')
            file.write('Promedio: {}\n'.format(mu))
            file.write('Desviacion standar: {}\n'.format(np.sqrt(S)))
            file.write('Intervalo de confianza: {}\n'.format(ci))

        # promedio_clientes
        mu = np.mean(clientes_promedio)
        S = np.var(clientes_promedio, ddof=1)
        ci = st.t.interval(0.95, NUMERO_DE_REPLICAS - 1, mu, np.sqrt(S))
        print('Promedio clientes que entraron al supermercado:')
        print('Promedio: ', mu)
        print('Desviacion standar: ', np.sqrt(S))
        print('Intervalo de confianza: '.format(ci))
        print()

        with open('KPIs {}.txt'.format(escenario), 'a') as file:
            file.write('TPromedio clientes que entraron al supermercado:\n)')
            file.write('Promedio: {}\n'.format(mu))
            file.write('Desviacion standar: {}\n'.format(np.sqrt(S)))
            file.write('Intervalo de confianza: {}\n'.format(ci))

        # unidades_vendidas
        mu = np.mean(unidades_vendidas)
        S = np.var(unidades_vendidas, ddof=1)
        ci = st.t.interval(0.95, NUMERO_DE_REPLICAS - 1, mu, np.sqrt(S))
        print('Total unidades vendidas:')
        print('Promedio:', mu)
        print('Desviacion standar:', np.sqrt(S))
        print('Intervalo de confianza:', ci)
        print()

        with open('KPIs {}.txt'.format(escenario), 'a') as file:
            file.write('Total de unidades vendidas:\n)')
            file.write('Promedio: {}\n'.format(mu))
            file.write('Desviacion standar: {}\n'.format(np.sqrt(S)))
            file.write('Intervalo de confianza: {}\n'.format(ci))

        # unidades_vendidas_por_cliente
        mu = np.mean(vendidos_por_clientes)
        S = np.var(vendidos_por_clientes, ddof=1)
        ci = st.t.interval(0.95, NUMERO_DE_REPLICAS - 1, mu, np.sqrt(S))
        print('Total unidades vendidas:')
        print('Promedio:', mu)
        print('Desviacion standar:', np.sqrt(S))
        print('Intervalo de confianza:', ci)
        print()

        with open('KPIs {}.txt'.format(escenario), 'a') as file:
            file.write('Total unidades vendidas por cada cliente:\n)')
            file.write('Promedio: {}\n'.format(mu))
            file.write('Desviacion standar: {}\n'.format(np.sqrt(S)))
            file.write('Intervalo de confianza: {}\n'.format(ci))

        # mapa de calor
        with open('mapa_de_calor {}.json'.format(escenario), 'w') as file:
            d = {}
            for i in mapaCalor.coordenadas:
                d.update({str(i): mapaCalor.coordenadas[i].calor})
            json.dump(d, file)

        # histograma_canasta_metros
        with open('histogramas {}.json'.format(escenario), 'w') as file:
            json.dump(histograma_canasta_metros, file)

        # histograma_canasta_tiempo
        with open('histogramas {}.json'.format(escenario), 'a') as file:
            json.dump(histograma_canasta_tiempo, file)

        # histograma venta_sku
        with open('histogramas {}.json'.format(escenario), 'a') as file:
            json.dump(ventas_por_sku, file)


run_simulacion(NUMERO_DE_REPLICAS, tasa_de_llegada, canastas_basicas, escenario)
