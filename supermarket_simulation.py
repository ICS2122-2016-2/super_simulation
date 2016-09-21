import simpy
import random
from mapa_super import mapa
import numpy
import scipy.stats as st
import threading
import time


hora_de_inicio = 8  # horas
hora_de_termino = 20  # horas
tasa_de_llegada = [50, 100, 100, 100, 80, 80, 80, 50, 50, 100, 100, 100]  # clientes/hora
numero_de_cajas_abiertas = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3] # en c/hora


seed = 458123
NUMERO_DE_REPLICAS = 30
benchmark = True
TNOW = time.time()


'''---------------------------------Super--------------------------------------------'''


class Supermercado:

    def __init__(self, env, mapa, tasa, canastas):
        self.env = env

        self.mapa = mapa
        self.canastas = canastas_basicas

        self.tasa_de_llegada = tasa
        self.clientes = {}
        self.venta_productos = {}
        for i in range(16470):
            self.venta_productos.update({i: 0})

        # variables de estado
        self.clientes_en_el_super = 0

        # variables de output
        self.productos_vendidos = 0

        # simulacion
        self.action = self.env.process(self.run())

    def run(self):
        while True:
            tiempo_entre_llegadas = random.expovariate(self.tasa_de_llegada[int(round(self.env.now//60 - 8))]/60)
            yield self.env.timeout(tiempo_entre_llegadas)
            self.env.process(self.llegada_de_cliente())
            #print(self.hora(self.env.now))

    def llegada_de_cliente(self):
        # en los ultimos 15 minutos no puedde entrar nade que haga una compra mas grande que 10 min
        if hora_de_termino*60 - 15 > self.env.now:

            index_canasta = random.randint(0, len(self.canastas) - 1)
            canasta = self.canastas[index_canasta]
            self.canastas.pop(index_canasta)

            cliente = Cliente(self.env, self, canasta)
            self.clientes[round(self.env.now//60 - 8)].append(cliente)

            yield self.env.process(cliente.comprar())

    def hora(self, now):
        return str(round(now//60)) + ':' + str(round(now%60)) if len(str(round(now%60))) == 2 \
            else str(round(now//60)) + ':0' + str(round(now%60))


class Cliente:
    id = 0

    def __init__(self, env, super, canasta):
        self.super = super
        self.env = env
        self.id = Cliente.id
        Cliente.id += 1

        # productos
        self.canasta_base = canasta

        # estado posicion
        self.coord_actual = -1
        self.nodo_actual = -1
        self.pasillo_actual = -1
        self.velocidad_cliente = -1
        self.tiempo_de_llegada_ = -1
        self.tiempo_de_salida = -1

        # estado del cliente
        self.tiempo_al_siguiente_producto = -1  # depende del largo del camino
        self.camino_a_siguiente_producto = -1
        self.tiempo_en_el_super = 0

        # estadisticas
        self.metros_caminados = 0
        self.tiempo_estadia_total = 0
        self.productos_comprados = []
        self.canasta_tentados = []

    def generar_canasta(self):  # canasta inicial (si la generamos aleatoriamente)
        pass

    def siguiente_producto(self):
        siguiente_producto = 0
        distancia = abs(self.canasta_base[0].x -self.posicion_actual[0]) + abs(self.canasta_base[0].y -self.posicion_actual[1])
        if len(self.canasta_base) > 0:
            for i in range(1, len(self.canasta_base)):
                distancia_i = abs(self.canasta_base[i].x -self.posicion_actual[0]) + abs(self.canasta_base[i].y -self.posicion_actual[1])
                if distancia_i < distancia:
                    siguiente_producto = i
                    distancia = distancia_i

        nodo_prod = self.super.mapa.productos[siguiente_producto].nodo
        self.actualizar_posicion_cliente()


        return siguiente_producto, distancia

    def caminar_a_siguiente_producto(self):
        if len(self.canasta_base) >= 0:
            siguiente_prod, distancia = self.siguiente_producto()
            tiempo_llegada = distancia/self.velocidad_cliente
            self.tiempo_hasta_llegar_al_siguiente_producto = tiempo_llegada

        else:
            self.caminar_a_la_caja()

    def recoger_producto(self):
        pass

    def actualizar_posicion_cliente(self):
        # actualizar coordenada calculando todo lo que ha avanzado el cliente desde la primera posicion
        self.nodo_actual = self.super.mapa.coordenadas[self.coord_actual].nodo

    def caminar_a_la_caja(self):
        pass

    def comprar(self):

        while len(self.canasta_base) > 0:
            #llegar y comprar
            self.caminar_a_siguiente_producto()
            # yield te tiempo  hasta que llega
            # eliminar prod de la canasta base
            self.recoger_producto()
            # yiel ...

        self.caminar_a_la_caja()
        #yield ...


class Boleta:
    id = 0

    def __init__(self, p):
        self.id = Boleta.id
        Boleta.id += 1


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


'''Simulacion'''
env = simpy.Environment(hora_de_inicio*60)
super = Supermercado(env, mapa, tasa_de_llegada, canastas_basicas)
env.run(until=hora_de_termino*60)
