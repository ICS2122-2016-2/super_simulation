#aqui se abre el archivo que se quiere leer que contiene los 12750 sku que van
import json
periodo1=[]
for i in range(12750):
    periodo1.append(i)
familias=[]
file=open("retail.dat")
matrix=[]
matriz_final=[]
mas_frecuentes=[]
menos_frecuentes=[]
lista_jefes=[]
lista_skufuera=[]
##indicador
productos_sin_familia_inicialmente=0
########leer archivo
for i in range(16470):
    matriz_final.append([0]*16470)
for line in file:
    boleta=line.split(" ")
    boleta=boleta[0:-1]
    boleta=list(map(int,boleta))
    matrix.append(boleta)
#######armar matriz correlaciones
for boleta in matrix:
    for i in range(0,(len(boleta))):
        for j in range(0,(len(boleta))):
            producto1=boleta[i]
            producto2=boleta[j]
            matriz_final[producto1][producto2]=matriz_final[producto1][producto2]+1
######sacar jefes
for j in periodo1:
    mas_frecuentes.append([matriz_final[j][j],j])
mas_frecuentes_ordenados=sorted(mas_frecuentes,reverse=True)
familias=mas_frecuentes_ordenados[:30]
for jefe in familias:
    jefe.pop(0)
    for i in jefe:
        periodo1.remove(i)
        lista_jefes.append(i)
###sacar productos menos frecuentes
for j in periodo1:
    menos_frecuentes.append([matriz_final[j][j],j])
menos_frecuentes_ordenados=sorted(menos_frecuentes)
fuera=menos_frecuentes_ordenados[:750]
for sku in fuera:
    sku.pop(0)
    for i in sku:
        periodo1.remove(i)
        lista_skufuera.append(i)
print("paso1 listo")
###armar familias
productos_sobrantes=[]
familias_llenas=[]
for sku in periodo1:
    lista_auxiliar=[]
    for familia in familias:
        lista_auxiliar2=[]
        if len(familia)<400:
            for producto in familia:
                lista_auxiliar2.append(str(matriz_final[producto][sku]))
            promedio_correlacion_familia=(eval('+'.join(lista_auxiliar2))/(len(familia)))
            lista_auxiliar.append(promedio_correlacion_familia)
        else:
            lista_auxiliar.append(0)
    indicador=lista_auxiliar.index(max(lista_auxiliar))
    if len(familias[indicador])<400:
        familias[indicador].append(sku)      
    else:
        productos_sobrantes.append(sku)
for sku in lista_skufuera:
    lista_auxiliar=[]
    for familia in familias:
        lista_auxiliar2=[]
        if len(familia)<400:
            for producto in familia:
                lista_auxiliar2.append(str(matriz_final[producto][sku]))
            promedio_correlacion_familia=(eval('+'.join(lista_auxiliar2))/(len(familia)))
            lista_auxiliar.append(promedio_correlacion_familia)
        else:
            lista_auxiliar.append(0)
    indicador=lista_auxiliar.index(max(lista_auxiliar))
    if len(familias[indicador])<400:
        familias[indicador].append(sku)      
    else:
        productos_sobrantes.append(sku)
productos_sin_familia_inicialmente=len(productos_sobrantes)
for familia in familias:
    if len(familia)<400:
        for i in productos_sobrantes:
            familia.append(i)
            productos_sobrantes.remove(i)
            if len(familia)==400:
                break

print('familias listas')
file=open("Familias/familias1.json","w")
json.dump(familias, file)
file.close()


file=open("Familias/productos_sobrantes.json","w")
json.dump(productos_sobrantes, file)
file.close()


    
    

    
    
    
    


    





    

    

    




    

