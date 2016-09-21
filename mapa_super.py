import json

class Mapa:

    def __init__(self, X, Y, familias):

        self.shape = (X, Y)
        self.nodos = {}
        self.coordenadas = {}
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
                for x_i in range(1, 5):
                    for y_i in range(5): # dim 6x5
                        c = ((x-1)*6+x_i+1, (y-1)*5+y_i+1)  #posicion: (X-1)*n°elementos en c/X + pos x_i + 1
                        coord = Coordenada(c, nodo)
                        self.coordenadas.update(coord)
                    if x == 1 or x == 11:   # caso borde,
                        for y_ii in range(5):
                            c = ((x-1)*6+1, (y-1)*5+y_ii+1)
                            coord = Coordenada(c, nodo)
                            self.coordenadas.update(coord)
                            c = ((x-1)*6+5+1, (y-1)*5+y_ii+1)
                            coord = Coordenada(c, nodo)
                            self.coordenadas.update(coord)

        # ubicar productos en su posicion
        for x in [2, 11]:
            for y in range(1, Y+1):
                for lado in [-1, 1]:
                    posicion = (x,y)
                    g = Gondola(posicion, lado, next(familias))
                    self.gondolas.update({posicion: g})
                    self.productos.update(g.productos)

    def dijkstra_nodos(self, actual, final):
        nodo_actual = actual
        nodo_final = final

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
                n = arco.nodo_llegada()
                adyacentes.append(n)

            if not adyacentes:
                pass

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
        return ruta


class Nodo:

    def __init__(self, x, y):
        self.coord = (x, y)
        self.arcos = []
        self.mapita = Mapita()


class Coordenada:

    def __init__(self, coord, nodo):
        self.coord = coord


class Arco:

    def __init__(self, dir, nodo):
        self.dir = dir
        self.nodo = nodo


class Producto:

    def __init__(self, id, nodo, coordenada):
        self.id = id
        self.nodo = nodo
        self.coord = coordenada


class Gondola:

    def __init__(self, posicion, lado, productos_gondola):  # productos_gondola es un generador con todos los prod ordenados
        self.posicion = posicion  # coordenada mas cercana al origen del mapa de coordenadas: (x, 2) o (x,11) para 1 <= x <= 15
        self.lado = 0  # lado es izquierda sis lado = -1, es derecha si lado = 1
        self.productos = {}
        if lado < 0:
            if self.posicion[1] == 2:
                for y in range(1, 9*5 + 1):
                    for z in range(1, 6):
                        nodo = (1+6*(posicion[0]-1), round((1*5+y)/5))
                        coord = (1+6*(posicion[0]-1), 1*5+y)
                        prod = Producto(int(next(productos_gondola)), nodo, coord)
                        self.productos.update({prod.id, prod})
            else:
                for y in range(1, 8*5 + 1):
                    for z in range(1, 6):
                        nodo = (1+6*(posicion[0]-1), round((11*5+y)/5))
                        coord = (1+6*(posicion[0]-1), 11*5+y)
                        prod = Producto(int(next(productos_gondola)), nodo, coord)
                        self.productos.update({prod.id, prod})
        else:
            if self.posicion[1] == 2:
                for y in range(1, 9*5 + 1):
                    for z in range(1, 6):
                        nodo = (6*posicion[0], round((1*5+y)/5))
                        coord = (6*(posicion[0]), 1*5+y)
                        prod = Producto(int(next(productos_gondola)), nodo, coord)
                        self.productos.update({prod.id, prod})
            else:
                for y in range(1, 8*5 + 1):
                    for z in range(1, 6):
                        nodo = (6*posicion[0], round((11*5+y)/5))
                        coord = (6*(posicion[0]), 11*5+y)
                        prod = Producto(int(next(productos_gondola)), nodo, coord)
                        self.productos.update({prod.id, prod})
        try:
            next(productos_gondola)
        except StopIteration:
            pass
        else:
            print('error de numero de productos en una gondola {}'.format(self.posicion))
            exit()


with open('families.json') as file:
    families = json.load(file)


mapa = Mapa(15, 19, (f for f in families))