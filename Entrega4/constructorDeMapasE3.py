import json
import random


# TODO ASOCIAR PRODUCTOS A CADA NODO PARA LA TENTACION DE UN CLIENTE CUANDO PASE POR AHI
# TODO TESTEAR QUE EL MAPA CON LOS PRODUCTOS SOBRANTES ESTE BIEN HECHO


class Mapa:

    def __init__(self, X, Y, familias, sobrantes):

        self.shape = (X, Y)
        self.nodos = {}
        self.coordenadas = {}
        self.productos = {}
        self.gondolas = {}
        self.productos_extra = list(sobrantes)

        # crear mapa de nodos
        for x in range(1, X+1):
            for y in range(1, Y+1):
                # crear nodos
                nodo = Nodo(x, y)
                self.nodos.update({(x, y): nodo})
                # unir nodos mediante arcos
                if y != Y:
                    self.nodos[(x, y)].arcos.append(Arco((0, 1), nodo))
                if y != 1:
                    self.nodos[(x, y)].arcos.append(Arco((0, -1), nodo))
                if (y == 1 or y == 11) and x != X:
                    self.nodos[(x, y)].arcos.append(Arco((1, 0), nodo))
                if (y == 1 or y == 11) and x != 1:
                    self.nodos[(x, y)].arcos.append(Arco((-1, 0), nodo))

                # crear mapa de coordenadas dentro de un nodo
                for x_i in range(1, 7):
                    for y_i in range(1, 6): # dim 6x5
                        c = ((x-1)*6+x_i, (y-1)*5+y_i)  #posicion: (X-1)*(n°elementos en cada X) + pos x_i + 1
                        coord = Coordenada(c, nodo)
                        self.coordenadas.update({c: coord})

        # ubicar productos en su posicion
        sobrantes = (i for i in self.productos_extra)
        for y in [2, 11]:
            for x in range(1, X + 1):
                posicion = (x,y)
                fam = next(familias)
                if y == 2:
                    # posicion: nodo de mas abajo
                    sob = next(sobrantes)
                    g = Gondola(self, posicion, (i for i in fam), (j for j in sob))
                else:
                    g = Gondola(self, posicion, (i for i in fam))
                self.gondolas.update({posicion: g})

    def dijkstra_nodos(self, actual, final):  # recibe nodos (x,y) del mapa
        nodo_actual = actual
        nodo_final = final

        if actual == final:
            return [actual]

        def grafo():
            graf = {}
            for nodo in self.nodos:
                graf.update({nodo: 9999})
            return graf

        def padre():
            p = {}
            for nodo in self.nodos:
                p.update({nodo: 0})
            return p

        def visto():
            v = {}
            for nodo in self.nodos:
                v.update({nodo: False})
            return v

        costo = grafo()  # costo de cada nodo
        costo[nodo_actual] = 0
        padre = padre()  # nodo predecesor
        marcado = visto()
        marcado[nodo_actual] = True  #marcar el primer nodo

        while True:
            # siempre existe camino, por lo tanto no hay condicion de salida
            adyacentes = []
            for arco in self.nodos[nodo_actual].arcos:
                n = arco.nodo_de_llegada
                adyacentes.append(n)

            #  actualizacion de costos y padres. todos los arcos tienen costo 1.
            for nodo in adyacentes:
                if costo[nodo] > costo[nodo_actual] + 1:
                    costo[nodo] = costo[nodo_actual] + 1
                    padre[nodo] = nodo_actual

            #  marcar y acutalizar nodos
            costos_no_marcados = costo
            costo_min = min(costos_no_marcados, key=lambda x: costo[x] if not marcado[x] else 9999)
            marcado[costo_min] = True

            if marcado[nodo_final]:
                break
            else:
                nodo_actual = costo_min

        # calculo ruta final
        ruta = []
        nodo_actual = nodo_final
        while True:
            ruta.append(padre[nodo_actual])
            nodo_actual = padre[nodo_actual]
            if nodo_actual == actual:
                break
        ruta.reverse()
        ruta.append(nodo_final)
        return ruta  # lista de nodos (x,y)

    def generar_camino_de_coordenadas(self, coord_actual, coord_final, camino_nodos):

        ruta = list()  # coordenadas (x,y)
        ruta.append(coord_actual)

        # avanzar derecho hasta siguiente siguiente curva
        # determinar largo lista (final del camino de nodos)
        fin = len(camino_nodos) - 1

        i = 0
        while True:
            coord_actual = ruta[-1]

            # termino algoritmo 1 (estamos en el mismo nodo donde se encuentra el producto)
            if camino_nodos[i] == camino_nodos[fin]:
                break
            nodo_actual = self.coordenadas[coord_actual].nodo

            #buscar direccion de movimiento del cliente (buscar direccion del siguiente nodo del camino)
            for arco in nodo_actual.arcos:
                if arco.nodo_de_llegada == camino_nodos[i+1]:
                    dir = arco.dir
                    break

            # chequear dir y ubicacion del cliente para poder avanzar
            if dir[0]:
                posicion_actual_y_pasillo = (coord_actual[1]+1) % 6 - 1
                if posicion_actual_y_pasillo in [2, 3, 4]:
                    # cliente centrado -> avanzar hasta siguiente nodo
                    c = coord_actual[0]
                    while True:
                        c += dir[0]
                        if self.coordenadas[(c, coord_actual[1])].nodo.coord != nodo_actual.coord:
                            siguiente_posicion = (c, coord_actual[1])
                            ruta.append(siguiente_posicion)
                            break
                    i += 1
                else:
                    # centrar cliente
                    nueva_pos_y_en_pasillo = (nodo_actual.coord[1]-1)*5 + random.randint(2, 4)
                    siguiente_posicion = (coord_actual[0], nueva_pos_y_en_pasillo)
                    ruta.append(siguiente_posicion)
            else:
                posicion_actual_x_pasillo = (coord_actual[0]+1) % 6 - 1
                if posicion_actual_x_pasillo in [3, 4]:
                    # cliente centrado -> avanzar hasta siguiente nodo
                    c = coord_actual[1]
                    while True:
                        c += dir[1]
                        if self.coordenadas[(coord_actual[0], c)].nodo.coord != nodo_actual.coord:
                            siguiente_posicion = (coord_actual[0], c)
                            ruta.append(siguiente_posicion)
                            break
                    i += 1

                else:
                    # centrar cliente
                    nueva_pos_x_en_pasillo = (nodo_actual.coord[0]-1)*6 + random.randint(3, 4)
                    siguiente_posicion = (nueva_pos_x_en_pasillo, coord_actual[1])
                    ruta.append(siguiente_posicion)

        # cliente esta en el nodo donde esta el producto -> caminar hasta producto:
        # camina hasta la altura del producto
        if ruta[-1] != (coord_actual[0], coord_final[1]):
            ruta.append((coord_actual[0], coord_final[1]))
        # camina hasta el producto
        ruta.append(coord_final)

        return ruta  # ruta: desde posicion cliente hasta posicion al frente de la ubicacion del producto


class MapaDeCalor:

    def __init__(self, mapa):
        self.coordenadas = mapa.coordenadas


class Nodo:

    def __init__(self, x, y):
        self.coord = (x, y)
        self.arcos = []
        self.productos_tentacion = set()


class Coordenada:

    def __init__(self, coord, nodo):
        self.coord = coord
        self.nodo = nodo
        self.calor = 0


class Arco:

    def __init__(self, dir, nodo):
        self.dir = dir
        self.nodo = nodo
        x_i = self.nodo.coord[0]
        y_i = self.nodo.coord[1]
        self.nodo_de_llegada = (x_i + self.dir[0], y_i + self.dir[1])  # coord (x,y)


class Producto:

    def __init__(self, id, nodo, coordenada, c_cliente):
        self.id = id
        self.nodo = nodo
        self.coord = coordenada
        self.coord_cliente = c_cliente


class Gondola:
    id = 1

    def __init__(self, mapa, posicion, productos_gondola, productos_extra=(i for i in [])):
        self.mapa = mapa
        self.id = Gondola.id
        self.familia = list(productos_gondola)
        Gondola.id += 1
        # productos_gondola es un generador con todos los prod ordenados
        # posicion es el nodo de la gondola mas cercano al origen del mapa de coordenadas: (x, 2) o (x,11) para 1 <= x <= 15
        self.posicion = posicion
        # lado es izquierda sis lado = -1, es derecha si lado = 1
        self.lado = 0
        self.productos = {}

        productos_gondola = (i for i in self.familia)
        # si esta en las gondolas de abajo
        if self.posicion[1] == 2:
            for y in range(1, 9*5 + 1):
                for z in range(1, 6):
                    nodo = (posicion[0], posicion[1] + (y // 5))
                    coord = (1+6*(posicion[0]-1), 1*5+y)
                    c_cliente = (coord[0] + 1, coord[1])
                    try:
                        id = int(next(productos_gondola))
                        prod = Producto(id, nodo, coord, c_cliente)
                        self.mapa.nodos[nodo].productos_tentacion.add(id)
                        self.mapa.productos.update({prod.id: prod})
                    except StopIteration:
                        id = int(next(productos_extra))
                        prod = Producto(id, nodo, coord, c_cliente)
                        self.mapa.nodos[nodo].productos_tentacion.add(id)
                        self.mapa.productos.update({prod.id: prod})
            for y in range(1, 9 * 5 + 1):
                for z in range(1, 6):
                    nodo = (posicion[0], posicion[1] + (y // 5))
                    coord = (6 * (posicion[0]), 1 * 5 + y)
                    c_cliente = (coord[0] - 1, coord[1])
                    try:
                        id = int(next(productos_gondola))
                        prod = Producto(id, nodo, coord, c_cliente)
                        self.mapa.nodos[nodo].productos_tentacion.add(id)
                        self.mapa.productos.update({prod.id: prod})
                    except StopIteration:
                        id = int(next(productos_extra))
                        prod = Producto(id, nodo, coord, c_cliente)
                        self.mapa.nodos[nodo].productos_tentacion.add(id)
                        self.mapa.productos.update({prod.id: prod})
        elif self.posicion[1] == 11:
            for y in range(1, 8 * 5 + 1):
                for z in range(1, 6):
                    nodo = (posicion[0], posicion[1] + (y // 5))
                    coord = (1 + 6 * (posicion[0] - 1), 11 * 5 + y)
                    c_cliente = (coord[0] + 1, coord[1])
                    id = int(next(productos_gondola))
                    prod = Producto(id, nodo, coord, c_cliente)
                    self.mapa.nodos[nodo].productos_tentacion.add(id)
                    self.mapa.productos.update({prod.id: prod})
            for y in range(1, 8*5 + 1):
                for z in range(1, 6):
                    nodo = (posicion[0], posicion[1] + (y // 5))
                    coord = (6*(posicion[0]), 11*5+y)
                    c_cliente = (coord[0] - 1, coord[1])
                    id = int(next(productos_gondola))
                    prod = Producto(id, nodo, coord, c_cliente)
                    self.mapa.nodos[nodo].productos_tentacion.add(id)
                    self.mapa.productos.update({prod.id: prod})
        try:
            next(productos_gondola)
        except StopIteration:
            pass
        else:
            print('error de numero de productos en una gondola', self.posicion)
            print('len productos: ', len(self.productos))
            exit()


## 30 familias de 400 productos
## 15 grupos de 25 productos sin familias


def construir_mapas(archivo, optimizacion=0):
    if not optimizacion:
        with open('Benchmark/{}.json'.format(archivo), 'r') as file:
            escenario = json.load(file)
    else:
        escenario = archivo
    mapa = Mapa(15, 19, (f for f in escenario[0]), (s for s in escenario[1]))
    mapa_de_tiempo = MapaDeCalor(mapa)
    mapa_de_flujo = MapaDeCalor(mapa)

    return mapa, mapa_de_tiempo, mapa_de_flujo

# construir_mapas('escenario1')


