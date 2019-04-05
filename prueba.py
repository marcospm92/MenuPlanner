# estructura diccionarios comidas y cenas {"plato":{"ingrediente":{cantidad,"ud medida"}}}

import csv
import time
import os


dict_comidas = {}

# Función para mostrar cualquiera de los diccionarios de comidas o cenas
def show_recipes(tipo):
    for plato, ingredientes in tipo.items():
        print("\n*",plato)
        for ingrediente, medidas in ingredientes.items():
            if (medidas[0] == 0 or medidas[0] == ""):
                print("\t-", ingrediente + ": Al gusto")
            else:
                print("\t-", ingrediente + ":", " ".join(map(str, medidas)))

def load_data():
    cantidad = []
    ind = 0
    with open("bbdd.txt") as f:
        lists = [line.strip().split(';') for line in f.readlines()]
    for line in lists:
        if(len(line) == 1):
            if(line[0] == "Comidas"):
                com_cen="com"
                continue
            if(line[0] == "Cenas"):
                com_cen="cen"
                continue
        else:
            dict_comidas[line[0]] = {}
            ingrs = line[1].strip().split(':')
            for i in range(len(ingrs)):
                if(i%3 == 0 or i%3==3):
                    ingrediente = ingrs[i]
                if(i%3 == 1):
                    cantidad.append(ingrs[i])
                if(i%3 == 2):
                    cantidad.append(ingrs[i])
                    dict_comidas[line[0]].update({ingrediente:cantidad})
                    cantidad = []

# Función para añadir recetas a mano
def add_recipes(tipo):
    cantidad = []
    plato = input("Introduce nombre para comida y pulsa Enter: ")
    tipo[plato] = {}
    with open("bbdd.txt", "a") as f:
        f.write(plato+";")
    while 1:
        ingrediente = input("Introduce ingrediente y pulsa Enter (Si has terminado, pulsa Enter sin escribir nada): ")
        if ingrediente == "":
            break
        print("Introduce cantidad de %s sin unidad y pulsa Enter (Puede dejarse vacío)" % ingrediente.upper(), end="")
        cantidad.append(input(": "))
        cantidad.append(input("Introduce unidad de medida para la cantidad previa (g, ml, kg, ...)(Puede dejarse vacío): "))

        tipo[plato].update({ingrediente:cantidad})
        with open("bbdd.txt", "a") as f:
            f.write(ingrediente+":"+cantidad[0]+":"+cantidad[1]+":")
        cantidad = []
    with open("bbdd.txt", 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    with open("bbdd.txt", "a") as f:
        f.write("\n")

###################################
###################################
print("Cargando datos...")
load_data()
time.sleep(0.5)
print("Datos cargados")
time.sleep(1)

print("*MENU*")
print("\t1. Mostrar comidas")
print("\t2. Mostrar cenas")
print("\t3. Añadir comidas o cenas")
print("\t4. Generar lista")

menu_ppal = int(input("Selecciona la opción: "))

if menu_ppal == 1:
    print("COMIDAS")
    show_recipes(dict_comidas)
elif menu_ppal == 2:
    print("CENAS")
    show_recipes(dict_cenas)
elif menu_ppal == 3:
    print("Añadir recetas")
    print("\t1. Añadir comida")
    print("\t2. Añadir cena")
    menu_add = int(input("Selecciona la opción: "))
    if menu_add == 1:
        print("AÑADIR COMIDAS")
        add_recipes(dict_comidas)
    elif menu_add == 2:
        print("AÑADIR CENAS")
        add_recipes(dict_cenas)
    else:
        print("Error")
elif menu_ppal == 4:
    print("Error")

else:
    print("Error")
