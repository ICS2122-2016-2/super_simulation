__author__ = 'Andres Anrique'
from gurobipy import *
import json
#####Recibe las correlaciones entre familias como un archivo diccionatrio con strings
def optimizacion_correlaciones(correlaciones):
    with open(correlaciones, 'r') as file:
        correlacion = json.load(file)
    file.close()
    familias = ['0','1', '2', '3','4','5','6','7','8','9','10','11','12','13','14','15']
    posiciones = ['0','1', '2', '3','4','5','6','7','8','9','10','11','12','13','14','15']
    '''
    cuadrante1=['0','1', '2', '3','4','5','6','7','8','9'] # el que quedará con mayor frecuencia
    cuadrante2=['10','11','12','13','14','15','16','17','18','19']# el segudo con mayor fecuencia de venta
    cuadrante3=['20','21','22','23','24','25','26','27','28','29'] # el tercero con mayor frecuencia
    '''
    distancias=[[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]]

    m = Model("assignment")
    x = {}
    n = 0
    #CREACION DE VARIABBLES
    for familia1 in familias:
        for familia2 in familias:
            for posicion1 in posiciones:
                for posicion2 in posiciones:
                    if posicion1!=posicion2 and familia1!=familia2:
                        x[familia1,familia2,posicion1,posicion2] = m.addVar(lb=0, ub=1, obj=float(correlacion["("+familia1+", "+familia2+")"])*distancias[int(posicion1)][int(posicion2)], vtype=GRB.BINARY, name=str(n))
                        n += 1
                    if familia1==familia2 and posicion1!=posicion2:
                        x[familia1,familia2,posicion1,posicion2] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=str(n))
                        n += 1
                    if posicion1==posicion2 and familia1!=familia2:
                        x[familia1,familia2,posicion1,posicion2] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=str(n))
                        n += 1
                    if posicion1==posicion2 and familia1==familia2:
                        x[familia1,familia2,posicion1,posicion2] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=str(n))
                        n += 1


    m.modelSense = GRB.MAXIMIZE                        
    m.update()
    #RESTRICCIONES DE ELIMINACION DE VARIABLES INEXISTENTES.
    
    for familia1 in familias:
        for familia2 in familias:
            for posicion1 in posiciones:
                for posicion2 in posiciones:
                    if familia1==familia2 and posicion1!=posicion2:
                         m.addConstr(x[familia1,familia2,posicion1,posicion2]==0)
                    if familia1!=familia2 and posicion1==posicion2:
                         m.addConstr(x[familia1,familia2,posicion1,posicion2]==0)
                    if familia1==familia2 and posicion1==posicion2:
                         m.addConstr(x[familia1,familia2,posicion1,posicion2]==0)
    #Restricciones del modelo principal 
    for var in familias:
        m.addConstr(quicksum(quicksum(quicksum(x[var,f2,p1,p2]for f2 in familias)for p1 in posiciones)for p2 in posiciones)<=1)
        m.addConstr(quicksum(quicksum(quicksum(x[f2,var,p1,p2]for f2 in familias)for p1 in posiciones)for p2 in posiciones)<=1)
        m.addConstr(quicksum(quicksum(quicksum(x[f2,p1,var,p2]for f2 in familias)for p1 in posiciones)for p2 in posiciones)<=1)
        m.addConstr(quicksum(quicksum(quicksum(x[f2,p2,p1,var]for f2 in familias)for p1 in posiciones)for p2 in posiciones)<=1)
        m.addConstr(quicksum(quicksum(quicksum(x[var,f2,p1,p2]for f2 in familias)+quicksum(x[f2,var,p1,p2]for f2 in familias)for p1 in posiciones)for p2 in posiciones)<=1)
        m.addConstr(quicksum(quicksum(quicksum(x[f2,p1,var,p2]for p2 in posiciones)+quicksum(x[f2,p1,p2,var]for p2 in posiciones)for p1 in posiciones)for f2 in familias)<=1)
    '''
    #RESTRICCION FREQ
    m.addConstr(quicksum(quicksum(quicksum(quicksum(x[f1,f2,p1,p2]*frqfam[int(f1)] for p1 in cuadrante1) for p2 in posiciones)+quicksum(quicksum(x[f1,f2,pp1,pp2]*frqfam[int(f2)] for pp1 in posiciones) for pp2 in cuadrante1)-quicksum(quicksum(x[f1,f2,p1,p2]*frqfam[int(f1)] for p1 in cuadrante2) for p2 in posiciones)-quicksum(quicksum(x[f1,f2,pp1,pp2]*frqfam[int(f2)] for pp1 in posiciones) for pp2 in cuadrante2)for f1 in familias) for f2 in familias)>=0)
    m.addConstr(quicksum(quicksum(quicksum(quicksum(x[f1,f2,p1,p2]*frqfam[int(f1)] for p1 in cuadrante2) for p2 in posiciones)+quicksum(quicksum(x[f1,f2,pp1,pp2]*frqfam[int(f2)] for pp1 in posiciones) for pp2 in cuadrante2)-quicksum(quicksum(x[f1,f2,p1,p2]*frqfam[int(f1)] for p1 in cuadrante3) for p2 in posiciones)-quicksum(quicksum(x[f1,f2,pp1,pp2]*frqfam[int(f2)] for pp1 in posiciones) for pp2 in cuadrante3)for f1 in familias) for f2 in familias)>=0)    
    '''
    m.optimize()
    status = m.status
    if status == GRB.Status.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
        
    if status == GRB.Status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        lista_final=[]
        for familia1 in familias:
            for familia2 in familias:
                for posicion1 in posiciones:
                    for posicion2 in posiciones:
                        if familia1!=familia2 and posicion1!=posicion2:
                            if x[familia1,familia2,posicion1,posicion2].X!=0:
                                lista_final.append([familia1,posicion1])
                                lista_final.append([familia2,posicion2])

    if status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % status)
                
    # do IIS
    if status == GRB.Status.INFEASIBLE:
        print('The model is infeasible; computing IIS')
        m.computeIIS()
        print('\nThe following constraint(s) cannot be satisfied:')
        for c in m.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)
    return lista_final

