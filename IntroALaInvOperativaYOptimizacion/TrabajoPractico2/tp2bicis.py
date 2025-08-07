import sys
import cplex

## Modelo para pie/bicis y camiones

TOLERANCE =10e-6 

class InstanciaRecorridoMixto:
    def __init__(self):
        self.cant_clientes = 0
        self.costo_repartidor = 0
        self.d_max = 0
        self.refrigerados = []
        self.exclusivos = []
        self.distancias = []        
        self.costos = []        

    def leer_datos(self,filename):
        # abrimos el archivo de datos
        f = open(filename)
        # leemos la cantidad de clientes
        self.cantidad_clientes = int(f.readline())
        # leemos el costo por pedido del repartidor
        self.costo_repartidor = int(f.readline())
        # leemos la distamcia maxima del repartidor
        self.d_max = int(f.readline())
        
        # inicializamos distancias y costos con un valor muy grande (por si falta algun par en los datos)
        self.distancias = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]
        self.costos = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]
        
        # leemos la cantidad de refrigerados
        cantidad_refrigerados = int(f.readline())
        # leemos los clientes refrigerados
        for i in range(cantidad_refrigerados):
            self.refrigerados.append(int(f.readline()))
        
        # leemos la cantidad de exclusivos
        cantidad_exclusivos = int(f.readline())
        # leemos los clientes exclusivos
        for i in range(cantidad_exclusivos):
            self.exclusivos.append(int(f.readline()))
        
        # leemos las distancias y costos entre clientes
        lineas = f.readlines()
        for linea in lineas:
            row = list(map(int,linea.split(' ')))
            self.distancias[row[0]-1][row[1]-1] = row[2]
            self.distancias[row[1]-1][row[0]-1] = row[2]
            self.costos[row[0]-1][row[1]-1] = row[3]
            self.costos[row[1]-1][row[0]-1] = row[3]
        # cerramos el archivo
        f.close()

def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaRecorridoMixto()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia


def agregar_variables(prob, instancia):
    nombres = []
    coef_obj = []
    tipos = []
    lb = []
    ub = []

    n = instancia.cantidad_clientes

    # Variables binarias x_ij (i ≠ j), valen 1 si el camion va de i a j
    for i in range(n):
        for j in range(n):
            if i != j:
                nombre = f"x_{i+1}_{j+1}"
                nombres.append(nombre)
                coef_obj.append(instancia.costos[i][j])
                tipos.append(prob.variables.type.binary)
                lb.append(0)
                ub.append(1)
                
    # Variables binarias y_ij, valen 1 si la bici va de i a j
    for i in range(n):
        for j in range(n):
            if i != j:
                nombre = f"y_{i+1}_{j+1}"
                nombres.append(nombre)
                coef_obj.append(instancia.costo_repartidor)
                tipos.append(prob.variables.type.binary)
                lb.append(0)
                ub.append(1)

    # Variables binarias p_i, valen 1 si el camion para en i
    for i in range(n):
        nombre = f"p_{i+1}"
        nombres.append(nombre)
        coef_obj.append(0.0)
        tipos.append(prob.variables.type.binary)
        lb.append(0)
        ub.append(1)
    

    # Variables enteras u_i, representan el orden en el recorrido del camión
    for i in range(n):
        nombre = f"u_{i+1}"
        nombres.append(nombre)
        if i == 0:
            coef_obj.append(0.0)
            tipos.append(prob.variables.type.integer)
            lb.append(0)
            ub.append(0)
        else:
            coef_obj.append(0.0)
            tipos.append(prob.variables.type.integer)
            lb.append(-1)
            ub.append(n - 1)

    prob.variables.add(obj=coef_obj, lb=lb, ub=ub, types=tipos, names=nombres)

def agregar_restricciones(prob, instancia):
    n = instancia.cantidad_clientes

    # Todo cliente es atendido una sola vez
    for j in range(n):
        vars_camion = [f"x_{i+1}_{j+1}" for i in range(n) if i != j]
        vars_repartidor = [f"y_{i+1}_{j+1}" for i in range(n) if i != j]
        
        todas_las_vars = vars_camion + vars_repartidor
        coeficientes = [1.0] * len(todas_las_vars)

        prob.linear_constraints.add(
            lin_expr=[[todas_las_vars, coeficientes]],
            senses=["E"],
            rhs=[1.0],
            names=[f"atendido_{j+1}"]
        )
    
    # Conservación de flujo del camión, lo que entra debe salir
    for j in range(n):
        vars_entrada = [f"x_{i+1}_{j+1}" for i in range(n) if i != j]
        vars_salida = [f"x_{j+1}_{i+1}" for i in range(n) if i != j]
        
        todas_las_vars = vars_entrada + vars_salida
        coeficientes = [1.0] * len(vars_entrada) + [-1.0] * len(vars_salida)

        prob.linear_constraints.add(
            lin_expr=[[todas_las_vars, coeficientes]],
            senses=["E"],
            rhs=[0.0],
            names=[f"flujo_camion_{j+1}"]
        )
    
    
    # No mas de un refrigerado por bici
    for j in range(n):
        ref = instancia.refrigerados
        vars_entrada = [f"y_{j+1}_{ref[i]}" for i in range(len(ref)) if j+1 != ref[i]]
        coeficientes = [1.0] * len(vars_entrada)

        prob.linear_constraints.add(
            lin_expr=[[vars_entrada, coeficientes]],
            senses=["L"],
            rhs=[1.0],
            names=[f"refri_{j+1}"]
        )
    
    # Definimos paradas (la ida)
    for i in range(n):
        vars_entrada = [f"y_{i+1}_{j+1}" for j in range(n) if i != j]
        paradas = f"p_{i+1}"
  
        todas_las_vars = vars_entrada + [paradas]
        coeficientes = [1.0] * len(vars_entrada) + [-n]

        prob.linear_constraints.add(
            lin_expr=[[todas_las_vars, coeficientes]],
            senses=["L"],
            rhs=[0.0],
            names=[f"paradas1_{i+1}"]
        )
        
    # Definimos paradas (la vuelta)
    for i in range(n):
        vars_salida_repartidor = [f"y_{i+1}_{j+1}" for j in range(n) if i != j]
        parada = f"p_{i+1}"

        todas_las_vars = vars_salida_repartidor + [parada]
        coeficientes = [1.0] * len(vars_salida_repartidor) + [-1.0]

        prob.linear_constraints.add(
            lin_expr=[[todas_las_vars, coeficientes]],
            senses=["G"],
            rhs=[0.0],
            names=[f"paradas_inversa_{i+1}"]
        )
        
    # Relacion paradas y camion
    for i in range(n):
        vars_entrada = [f"x_{j+1}_{i+1}" for j in range(n) if i != j]
        paradas = f"p_{i+1}"
  
        todas_las_vars = vars_entrada + [paradas]
        coeficientes = [1.0] * len(vars_entrada) + [-1.0]

        prob.linear_constraints.add(
            lin_expr=[[todas_las_vars, coeficientes]],
            senses=["G"],
            rhs=[0.0],
            names=[f"paradas2_{i+1}"]
        )
      
    # Distancias validas    
    for i in range(n):
        for j in range(n):
            if i != j :
                variable = [f"y_{i+1}_{j+1}"]
                coeficiente = [instancia.distancias[i][j]]
                prob.linear_constraints.add(
                    lin_expr=[[variable, coeficiente]],
                    senses=["L"],
                    rhs=[instancia.d_max],
                    names=[f"distancia_valida_{i+1}_{j+1}"]
                )
        

    # Restricciones de subtour para el camión
    agregar_subtours(prob, instancia)


def agregar_subtours(prob, instancia):
    n = instancia.cantidad_clientes
    
    for i in range(n):  
        for j in range(1, n):
            if i != j:
                nombre_u_i = f"u_{i+1}"
                nombre_u_j = f"u_{j+1}"
                nombre_x_ij = f"x_{i+1}_{j+1}"

                prob.linear_constraints.add(
                    lin_expr=[[[nombre_u_i, nombre_u_j, nombre_x_ij],
                               [1.0, -1.0, n+1]]],
                    senses=["L"],
                    rhs=[n],
                    names=[f"mtz_{i+1}_{j+1}"]
                )
        
def armar_lp(prob, instancia):
    # Agregar las variables
    agregar_variables(prob, instancia)
    
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.minimize)

    # Escribir el lp a archivo
    prob.write('recorridoMixto.lp')
    
def resolver_lp(prob):

    prob.parameters.timelimit.set(500)
    prob.solve()
    
    prob.solution.write("solucion.sol")


def mostrar_solucion(prob, instancia):
    status = prob.solution.get_status_string(status_code=prob.solution.get_status())    
    valor_obj = prob.solution.get_objective_value()
    print('Funcion objetivo: ', valor_obj, '(' + str(status) + ')')

    x = prob.solution.get_values()
    nombres = prob.variables.get_names()

    print("\nRecorridos del camión (x_ij):")
    for nombre, val in zip(nombres, x):
        if val > TOLERANCE and nombre.startswith("x_"):
            print(f"{nombre} = {val}")

    print("\nEntregas hechas por repartidor a pie/bici (y_ij):")
    for nombre, val in zip(nombres, x):
        if val > TOLERANCE and nombre.startswith("y_"):
            print(f"{nombre} = {val}")
            
    print("\nParadas del camión (p_i):")
    for nombre, val in zip(nombres, x):
        if val > TOLERANCE and nombre.startswith("p_"):
            print(f"{nombre} = {val}")
            

def main():
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()

    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp(prob, instancia)
    

    #prob.parameters.preprocessing.aggregator.set(0)
    #prob.parameters.preprocessing.linear.set(0)
    #prob.parameters.preprocessing.aggregator.set(1)
    #prob.parameters.preprocessing.linear.set(1)
  
    #prob.parameters.mip.strategy.nodeselect.set(0) # por profundidad
    #prob.parameters.mip.strategy.nodeselect.set(1) # por mejor cota
    
    # Resolucion del modelo
    resolver_lp(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob, instancia)

if __name__ == '__main__':
    main()