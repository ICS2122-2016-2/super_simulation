import pickle
from scipy import sre_parse

def armar_matriz(datos):


    file=open(datos)
    matrix=[]
    matriz_final=[]
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
    with open('matrizFinal','wb') as file:
        pickle.dump(matriz_final, file)
#armar_matriz("retail.dat")
    
