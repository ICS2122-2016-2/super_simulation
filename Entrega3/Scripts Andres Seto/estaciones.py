file=open("retail.dat")
matrix=[]
matriz_final=[]


for line in file:
    boleta=line.split(" ")
    boleta=boleta[0:-1]
    boleta=list(map(int,boleta))
    matrix.append(boleta)
    
productos1 = set()
n_boleta = 0
estaciones = []
stop = 0

for boleta in matrix:
    if stop == 1:
        break
    for prod in boleta:
        productos1.add(prod)
        if len(productos1)==12750:
            stop = 1
            break
    n_boleta += 1

n_boleta -= 1
estaciones.append(n_boleta)
n_boleta += 1
stop = 0
productos2 = set()
prod_aux = set()
for boleta in matrix[n_boleta:]:
    if stop == 1:
        break
    for prod in boleta:
        if prod not in productos1:
            prod_aux.add(prod)
        productos2.add(prod)
        if len(prod_aux)==1860:
            stop = 1
            break
    n_boleta += 1


n_boleta -= 1
estaciones.append(n_boleta)
n_boleta += 1
#añadir productos faltantes en productos2 hasta llegar a 12750

for i in range(n_boleta,0,-1):
    boleta = matrix[i]
    if len(productos2)==12750:
        break
    for prod in boleta:
        productos2.add(prod)
        if len(productos2)==12750:
            break


stop = 0
productos3 = set()
prod_aux = set()
for boleta in matrix[n_boleta:]:
    if stop == 1:
        break
    for prod in boleta:
        productos3.add(prod)
        if len(productos3)==12750:
            stop = 1
            break
    n_boleta += 1

n_boleta -= 1
for i in range(n_boleta,0,-1):
    boleta = matrix[i]
    if len(productos3)==12750:
        break
    for prod in boleta:
        productos3.add(prod)
        if len(productos3)==12750:
            break

