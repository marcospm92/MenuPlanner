# estructura diccionarios comidas y cenas {"plato":{"ingrediente":{cantidad,"ud medida"}}}

import csv
import time
import os
import sys
from tabulate import tabulate
import random

dict_comidas = {}
dict_cenas = {}

def clear():
    SO = sys.platform
    if SO == "linux":
        os.system('clear')
    elif SO == "win64" or SO == "win32":
        os.system('cls')
    else:
        print("Error al limpiar la pantalla. Fallo al detectar SO")

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
        #if(len(line) == 1):
        if(line[0] == "Comida"):
            com_cen="com"
            dict_comidas[line[1]] = {}
        elif(line[0] == "Cena"):
            com_cen="cen"
            dict_cenas[line[1]] = {}
        ingrs = line[2].strip().split(':')
        for i in range(len(ingrs)):
            if(i%3 == 0 or i%3==3):
                ingrediente = ingrs[i]
            if(i%3 == 1):
                cantidad.append(ingrs[i])
            if(i%3 == 2):
                cantidad.append(ingrs[i])
                if(com_cen == "com"):
                    dict_comidas[line[1]].update({ingrediente:cantidad})
                elif(com_cen == "cen"):
                    dict_cenas[line[1]].update({ingrediente:cantidad})
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


def generate_menu():
    comid = []
    comidas = []
    cen = []
    cenas = []
    i = 0
    pescado_semana = 0

    # Primera prueba, platos random
    #comidas = random.choices(list(dict_comidas.keys()), k=7)
    cenas = random.choices(list(dict_cenas.keys()), k=7)

    comida1 = random.choice(list(dict_comidas.keys()))
    comidas.append(comida1)
    j = 1

    if "Pescado" in dict_comidas[comida1].keys():
        pescado_semana = pescado_semana + 1

    while j < 7:
        print(pescado_semana)
        comida2 = random.choice(list(dict_comidas.keys()))
        cena1 = random.choice(list(dict_cenas.keys()))
        if "Pescado" in dict_comidas[comida2].keys():
            if pescado_semana == 2:
                continue # Máximo 2 veces pescado a la semana
            else:
                pescado_semana = pescado_semana + 1
        else:
            if j == 3 and pescado_semana == 0:
                continue
        if "Arroz" in dict_comidas[comida1].keys() and "Arroz" in dict_comidas[comida2].keys(): # No arroz dos comidas consecutivas
            continue
        elif "Pescado" in dict_comidas[comida1].keys() and "Pescado" in dict_comidas[comida2].keys(): # No pescado dos comidas consecutivas
            continue
        elif "Pasta de colores" in dict_comidas[comida1].keys() or "Pasta de espelta" in dict_comidas[comida1].keys():
            if "Pasta de colores" in dict_comidas[comida2].keys() or "Pasta de espelta" in dict_comidas[comida2].keys(): # No pasta dos comidas consecutivas
                continue
            else:
                comidas.append(comida2)
                j = j+1
                comida1 = comida2
        else:
            comidas.append(comida2)
            j = j+1
            comida1 = comida2

    cena1 = random.choice(list(dict_cenas.keys()))
    cenas.append(cena1)
    j = 1

    sum = 0
    print("Pescado esta semana: ", pescado_semana)
    pescado_semana = 0

    # Esta parte prepara los datos que hay en comidas y cenas para meter saltos de linea y que se vean bien las tablas
    for line in comidas:
        prueb = line.strip().split(' ')
        while i < len(prueb):
            sum = sum + int(len(prueb[i]))
            if sum >= 18:
                prueb.insert(i, "\n")
                sum = 0
            i = i + 1
        i = 0
        sum = 0
        prueb = " ".join(prueb)
        comid.append(prueb)

    for line in cenas:
        prueb = line.strip().split(' ')
        while i < len(prueb):
            sum = sum + int(len(prueb[i]))
            if sum >= 18:
                prueb.insert(i, "\n")
                sum = 0
            i = i + 1
        i = 0
        sum = 0
        prueb = " ".join(prueb)
        cen.append(prueb)

    lunes = [comid[0], cen[0]]
    martes = [comid[1], cen[1]]
    miercoles = [comid[2], cen[2]]
    jueves = [comid[3], cen[3]]
    viernes = [comid[4], cen[4]]
    sabado = [comid[5], cen[5]]
    domingo = [comid[6], cen[6]]
    indice = range(1, len(comidas)+1)
    table = zip(lunes, martes, miercoles, jueves, viernes, sabado, domingo)
    print(tabulate(table, headers=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], tablefmt="fancy_grid"))




###################################
###################################



print("Cargando datos...")
load_data()
time.sleep(0.5)
print("Datos cargados")
time.sleep(1)

while(1):
    clear()
    print("*MENU*\n")
    print("\t1. Mostrar comidas")
    print("\t2. Mostrar cenas")
    print("\t3. Añadir comidas o cenas")
    print("\t4. Generar lista de ingredientes")
    print("\t5. Buscar")
    print("\t6. Generar propuesta de menú")
    print("\t7. Salir")

    menu_ppal = int(input("\nSelecciona la opción: "))

    if menu_ppal == 1:
        print("COMIDAS")
        show_recipes(dict_comidas)
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 2:
        print("CENAS")
        show_recipes(dict_cenas)
        input("Pulsa Enter para volver al menú principal")

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
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 4:
        print("Generar lista de ingredientes")
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 5:
        print("Error")
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 6:
        print("Generar propuesta de menús")
        generate_menu()
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 7:
        break

    else:
        print("Error")
        input("Pulsa Enter para volver al menú principal")
