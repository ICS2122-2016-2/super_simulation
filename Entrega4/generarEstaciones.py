from scipy import sparse


#reicibe la lista de boletas y devuelve los 3 periodos

def periodos(datos):

    with open(datos, 'r') as file:
        lines = file.readlines()
        boletas = []
        for i in range(len(lines)):
            boleta = [int(j) for j in lines[i].split()]
            boletas.append(boleta)

    periodos_finales = []
    # Periodo 1
    productos1 = set()
    inicio = 0
    indice = 0
    while True:
        boleta = boletas[indice]
        for prod in boleta:
            productos1.add(prod)
        if len(productos1) > 12750:
            break
        else:
            indice += 1
    p1 = (inicio, indice - 1)
    periodos_finales.append(p1)

    # Segundo periodo
    productos2 = set()
    inicio = round(len(boletas)/2) - 6000
    bajo = inicio
    superior = inicio + 1
    while True:
        # bajo
        boleta = boletas[bajo]
        for prod in boleta:
            productos2.add(prod)
        if len(productos2) > 12750:
            break
        else:
            bajo -= 1
        # superior
        boleta = boletas[superior]
        for prod in boleta:
            productos2.add(prod)
        if len(productos2) > 12750:
            break
        else:
            superior += 1

    p2 = (bajo + 1, superior - 1)
    periodos_finales.append(p2)

    # Periodo 1
    productos3 = set()
    inicio = len(boletas) - 1
    indice = inicio
    while True:
        boleta = boletas[indice]
        for prod in boleta:
            productos3.add(prod)
        if len(productos3) > 12750:
            break
        else:
            indice -= 1
    p3 = (indice + 1, inicio)
    periodos_finales.append(p3)

    return periodos_finales


