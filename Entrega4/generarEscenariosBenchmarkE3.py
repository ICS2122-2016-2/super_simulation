import random
import json

def generar_benchmark():
    productos = list(range(12750))

    familias = []
    for i in range(30):
        familia = []
        for j in range(400):
            p = random.choice(productos)
            familia.append(p)
            productos.pop(productos.index(p))
        familias.append(familia)

    sobrantes = []
    for i in range(15):
        s = []
        for j in range(50):
            p = random.choice(productos)
            s.append(p)
            productos.pop(productos.index(p))
        sobrantes.append(s)

    fam = [familias, sobrantes]

    with open('Benchmark/benchmark.json', 'w') as file:
        json.dump(fam, file)

