#aqui se abre el archivo que se quiere leer que contiene los 12750 sku que van
import json
def armar_familias(productos_del_periodo,datos):
    with open(productos_del_periodo, 'r') as file:
        periodo1 = json.load(file)
    familias=[]
    file=open(datos)
    matrix=[]
    matriz_final=[]
    mas_frecuentes=[]
    menos_frecuentes=[]
    lista_jefes=[]
    productos_sobrantes=[]
    ##indicador
    productos_sin_familia_inicialmente=0
    print("sacando matriz de correlaciones")
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
    print("sacando jefes y productos menos frecuentes")
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
            productos_sobrantes.append(i)
    print("armando familias")
    ###armar familias

    familias_llenas=[]
    for sku in periodo1:
        lista_auxiliar=[]
        for familia in familias:
            suma=0
            if len(familia)<400:
                for producto in familia:
                    suma=suma+matriz_final[producto][sku]
                promedio_correlacion_familia=suma/(len(familia))
                lista_auxiliar.append(promedio_correlacion_familia)
            else:
                lista_auxiliar.append(0)
        indicador=lista_auxiliar.index(max(lista_auxiliar))
        if len(familias[indicador])<400:
            familias[indicador].append(sku)      
        else:
            productos_sobrantes.insert(0,sku)
    productos_sin_familia_inicialmente=len(productos_sobrantes)
    for familia in familias:
        if len(familia)<400:
            for i in productos_sobrantes:
                familia.append(i)
                productos_sobrantes.remove(i)
                if len(familia)==400:
                    break
    lista_sku_s=[productos_sobrantes[:25],productos_sobrantes[25:50],productos_sobrantes[50:75],productos_sobrantes[75:100],productos_sobrantes[100:125],productos_sobrantes[125:150],productos_sobrantes[150:175],productos_sobrantes[175:200],productos_sobrantes[200:225],productos_sobrantes[225:250],productos_sobrantes[250:275],productos_sobrantes[275:300],productos_sobrantes[300:325],productos_sobrantes[325:350],productos_sobrantes[350:375],productos_sobrantes[375:400],productos_sobrantes[400:425],productos_sobrantes[425:450],productos_sobrantes[450:475],productos_sobrantes[475:500],productos_sobrantes[500:525],productos_sobrantes[525:550],productos_sobrantes[550:575],productos_sobrantes[575:600],productos_sobrantes[600:625],productos_sobrantes[625:650],productos_sobrantes[650:675],productos_sobrantes[675:700],productos_sobrantes[700:725],productos_sobrantes[725:750]]       
    imprimir=[]
    imprimir.append(familias)
    imprimir.append(lista_sku_s)
    file=open("familias y productos sobrantes.json","w")
    json.dump(imprimir, file)
    file.close()
                
            
        
        

        
        
        
        


        





    

    

    




    

