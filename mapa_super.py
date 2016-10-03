import json
import random


class Mapa:

    def __init__(self, X, Y, familias):

        self.shape = (X, Y)
        self.nodos = {}
        self.coordenadas = {}
        self.coordenadas_mapa_calor_un_cliente = {}
        self.gondolas = {}
        self.productos = {}
        # crear mapa de nodos
        for x in range(1, X+1):
            for y in range(1, Y+1):
                nodo = Nodo(x, y)
                self.nodos.update({(x, y): nodo})
                if y != Y:
                    self.nodos[(x, y)].arcos.append(Arco((0, 1), nodo))
                if y != 1:
                    self.nodos[(x, y)].arcos.append(Arco((0, -1), nodo))
                if (y == 1 or y == 11) and x != X:
                    self.nodos[(x, y)].arcos.append(Arco((1, 0), nodo))
                if (y == 1 or y == 11) and x != 1:
                    self.nodos[(x, y)].arcos.append(Arco((-1, 0), nodo))

                # crear mapa de coordenadas
                for x_i in range(1, 7):
                    for y_i in range(1, 6): # dim 6x5
                        c = ((x-1)*6+x_i, (y-1)*5+y_i)  #posicion: (X-1)*(n°elementos en cada X) + pos x_i + 1
                        coord = Coordenada(c, nodo)
                        self.coordenadas.update({c: coord})

        # ubicar productos en su posicion
        for y in [2, 11]:
            for x in range(1, X + 1):
                for lado in [-1, 1]:
                    posicion = (x,y)
                    fam = next(familias)
                    # print('len familia {}: '.format((x,y)), len(fam))
                    g = Gondola(posicion, lado, (i for i in fam), len(fam))
                    self.gondolas.update({posicion: g})
                    self.productos.update(g.productos)

    def dijkstra_nodos(self, actual, final):  # recibe coordenadas (x,y) de los nodos
        nodo_actual = actual
        nodo_final = final

        if actual == final:
            return [actual]

        def grafo():
            graf = {}
            for nodo in self.nodos:
                graf.update({nodo: 9999999})
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

        costo = grafo()  # costo
        costo[nodo_actual] = 0
        padre = padre()  # nodo predecesor
        marcado = visto()
        marcado[nodo_actual] = True

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
        return ruta  # lista de coordenadas (x,y)

    def generar_camino_de_coordenadas(self, coord_actual, coord_final, camino_nodos):

        ruta = list()  # coordenadas (x,y)
        ruta.append(coord_actual)

        # avanzar derecho hasta siguiente siguiente curva
        fin = len(camino_nodos) - 1
        i = 0
        while True:
            coord_actual = ruta[-1]

            # termino algoritmo 1 (estamos en el mismo nodo donde se encuentra el producto)
            if camino_nodos[i] == camino_nodos[fin]:
                break
            nodo_actual = self.coordenadas[coord_actual].nodo
            #print(i, coord_actual, coord_final, nodo_actual.coord, [i for i in camino_nodos])

            #buscar el siguiente nodo del camino
            for arco in nodo_actual.arcos:
                if arco.nodo_de_llegada == camino_nodos[i+1]:
                    dir = arco.dir
                    break

            # chequear dir y ubicacion del cliente para poder avanzar
            if dir[0]:
                posicion_actual_y_pasillo = (coord_actual[1]+1) % 6 - 1
                #print(posicion_actual_y_pasillo, 'pos y actual')
                if posicion_actual_y_pasillo in [2, 3, 4]:
                    #print('hola1')
                    # cliente centrado -> avanzar hasta siguiente nodo
                    c = coord_actual[0]
                    while True:
                        c += dir[0]
                        #print('c actual', (c, coord_actual[1]), 'nodo actual', self.coordenadas[(c, coord_actual[1])].nodo.coord)
                        if self.coordenadas[(c, coord_actual[1])].nodo.coord != nodo_actual.coord:
                            siguiente_posicion = (c, coord_actual[1])
                            ruta.append(siguiente_posicion)
                            break
                    #print('ruta', ruta)
                    i += 1
                else:
                    # centrar cliente
                    #print('hola2')

                    nueva_pos_y_en_pasillo = (nodo_actual.coord[1]-1)*5 + random.randint(2, 4)
                    #print(nueva_pos_y_en_pasillo, 'nueva pos y')
                    siguiente_posicion = (coord_actual[0], nueva_pos_y_en_pasillo)
                    ruta.append(siguiente_posicion)
                    #print('ruta', ruta)
            else:
                posicion_actual_x_pasillo = (coord_actual[0]+1) % 6 - 1
                #print(posicion_actual_x_pasillo, 'pos x actual')
                if posicion_actual_x_pasillo in [3, 4]:
                    #print('hola3')
                    # cliente centrado -> avanzar hasta siguiente nodo
                    c = coord_actual[1]
                    while True:
                        c += dir[1]
                        if self.coordenadas[(coord_actual[0], c)].nodo.coord != nodo_actual.coord:
                            siguiente_posicion = (coord_actual[0], c)
                            ruta.append(siguiente_posicion)
                            break
                    #print('ruta', ruta)
                    i += 1

                else:
                    # centrar cliente
                    #print('hola4')
                    nueva_pos_x_en_pasillo = (nodo_actual.coord[0]-1)*6 + random.randint(3, 4)
                    #print(nueva_pos_x_en_pasillo, 'nueva pos x')
                    siguiente_posicion = (nueva_pos_x_en_pasillo, coord_actual[1])
                    ruta.append(siguiente_posicion)
                    #print('ruta', ruta)

        # caminar hasta producto:
        if ruta[-1] != (coord_actual[0], coord_final[1]):
            ruta.append((coord_actual[0], coord_final[1]))
        ruta.append(coord_final)
        #print(ruta)

        return ruta  # ruta: desde posicion cliente hasta posicion al frente de la ubicacion del producto


class MapaDeCalor:

    def __init__(self, mapa):
        self.coordenadas = mapa.coordenadas


class Nodo:

    def __init__(self, x, y):
        self.coord = (x, y)
        self.arcos = []


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

    def __init__(self, posicion, lado, productos_gondola, len_familia):  # productos_gondola es un generador con todos los prod ordenados
        self.posicion = posicion  # coordenada mas cercana al origen del mapa de coordenadas: (x, 2) o (x,11) para 1 <= x <= 15
        self.lado = 0  # lado es izquierda sis lado = -1, es derecha si lado = 1
        self.productos = {}
        if lado < 0:
            if self.posicion[1] == 2:
                for y in range(1, 9*5 + 1):
                    for z in range(1, 6):
                        nodo = (posicion[0], posicion[1] + (y // 5))
                        coord = (1+6*(posicion[0]-1), 1*5+y)
                        c_cliente = (coord[0] + 1, coord[1])
                        prod = Producto(int(next(productos_gondola)), nodo, coord, c_cliente)
                        self.productos.update({prod.id: prod})
            else:
                for y in range(1, 8*5 + 1):
                    for z in range(1, 6):
                        nodo = (posicion[0], posicion[1] + (y // 5))
                        coord = (1+6*(posicion[0]-1), 11*5+y)
                        c_cliente = (coord[0] + 1, coord[1])
                        prod = Producto(int(next(productos_gondola)), nodo, coord, c_cliente)
                        self.productos.update({prod.id: prod})
        else:
            if self.posicion[1] == 2:
                for y in range(1, 9*5 + 1):
                    for z in range(1, 6):
                        nodo = (posicion[0], posicion[1] + (y // 5))
                        coord = (6*(posicion[0]), 1*5+y)
                        c_cliente = (coord[0] - 1, coord[1])
                        prod = Producto(int(next(productos_gondola)), nodo, coord, c_cliente)
                        self.productos.update({prod.id: prod})
            else:
                for y in range(1, 8*5 + 1):
                    for z in range(1, 6):
                        nodo = (posicion[0], posicion[1] + (y // 5))
                        coord = (6*(posicion[0]), 11*5+y)
                        c_cliente = (coord[0] - 1, coord[1])
                        prod = Producto(int(next(productos_gondola)), nodo, coord, c_cliente)
                        self.productos.update({prod.id: prod})
        try:
            next(productos_gondola)
        except StopIteration:
            pass
        else:
            print('error de numero de productos en una gondola', self.posicion)
            print('len productos: ', len(self.productos))
            print()
            exit()


with open('families.json') as file:
    families = json.load(file)
families.reverse()

mapa = Mapa(15, 19, (f for f in families))
mapa_de_calor = MapaDeCalor(mapa)