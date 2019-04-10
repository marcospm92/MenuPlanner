# estructura diccionarios comidas y cenas {"plato":{"ingrediente":{cantidad,"ud medida"}}}

import csv
import time
import os
import sys
from tabulate import tabulate
import random
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas

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
def add_recipes(tipo, diccionario):
    cantidad = []
    plato = input("Introduce nombre para comida y pulsa Enter: ")
    diccionario[plato] = {}
    with open("bbdd.txt", "a") as f:
        f.write(tipo+";"+plato+";")
    while 1:
        ingrediente = input("Introduce ingrediente y pulsa Enter (Si has terminado, pulsa Enter sin escribir nada): ")
        if ingrediente == "":
            break
        print("Introduce cantidad de %s sin unidad y pulsa Enter (Puede dejarse vacío)" % ingrediente.upper(), end="")
        cantidad.append(input(": "))
        cantidad.append(input("Introduce unidad de medida para la cantidad previa (g, ml, kg, ...)(Puede dejarse vacío): "))

        diccionario[plato].update({ingrediente:cantidad})
        with open("bbdd.txt", "a") as f:
            f.write(ingrediente+":"+cantidad[0]+":"+cantidad[1]+":")
        cantidad = []
    with open("bbdd.txt", 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    with open("bbdd.txt", "a") as f:
        f.write("\n")
    print("Plato añadido")

def generate_menu():
    comid = []
    comidas = []
    comidas_wip = []
    ingr_com = []
    in_com = []
    i_com = []
    cen = []
    cenas = []
    ingr_cen = []
    in_cen = []
    i_cen = []
    i = 0
    intentos = 0

    saltar = 0
    menu_ok = 0

    print("Selecciona para cuánto tiempo quieres generar menú")
    print("\t1. 1 semana")
    print("\t2. 2 semanas")
    semanas = int(input("\nSelecciona la opción: "))

### Genero menú solo con condiciones de no repetir, y despues compruebo las restricciones. Si están OK pongo menu_ok a 1
    for semana in range(semanas):
        print("Planificando semana",semana+1, "de", semanas)
        while menu_ok == 0:
            comidas_wip = []
            cenas_wip = []
            intentos = intentos + 1
            primera_ok = 0

            while primera_ok == 0:
                pescado_semana = 0
                boniato_semana = 0
                cena1 = random.choice(list(dict_cenas.keys()))
                comida1 = random.choice(list(dict_comidas.keys()))
                j = 1

                if "Pescado" in dict_comidas[comida1].keys():
                    pescado_semana = pescado_semana + 1
                if "Pescado" in dict_cenas[cena1].keys():
                    pescado_semana = pescado_semana + 1
                if "Boniato" in dict_comidas[comida1].keys():
                    boniato_semana = boniato_semana + 1
                if "Boniato" in dict_cenas[cena1].keys():
                    boniato_semana = boniato_semana + 1
                if pescado_semana < 2 and boniato_semana < 2:
                    primera_ok = 1

            cenas_wip.append(cena1)
            comidas_wip.append(comida1)

            while j < 7:
                comida2 = random.choice(list(dict_comidas.keys()))
                cena2 = random.choice(list(dict_cenas.keys()))
                if "Arroz" in dict_comidas[comida1].keys() and "Arroz" in dict_comidas[comida2].keys(): # No arroz dos comidas consecutivas
                   saltar = 1
                if "Boniato" in dict_comidas[comida1].keys() and "Boniato" in dict_comidas[comida2].keys(): # No boniato dos comidas consecutivas
                   saltar = 1
                if "Pescado" in dict_comidas[comida1].keys() and "Pescado" in dict_comidas[comida2].keys(): # No pescado dos comidas consecutivas
                   saltar = 1
                if "Pescado" in dict_cenas[cena1].keys() and "Pescado" in dict_cenas[cena2].keys(): # No pescado dos cenas consecutivas
                   saltar = 1
                if "Pescado" in dict_cenas[cena1].keys() and "Pescado" in dict_comidas[comida2].keys(): # No pescado dos veces consecutivas
                   saltar = 1
                if "Pescado" in dict_comidas[comida2].keys() and "Pescado" in dict_cenas[cena2].keys(): # No pescado dos veces consecutivas
                   saltar = 1
                if "Patata" in dict_comidas[comida1].keys() and "Patata" in dict_comidas[comida2].keys(): # No patata dos comidas consecutivas
                   saltar = 1
                if "Pasta colores" in dict_comidas[comida1].keys() or "Pasta espelta" in dict_comidas[comida1].keys() or "Pasta integral" in dict_comidas[comida1].keys():
                   if "Pasta colores" in dict_comidas[comida2].keys() or "Pasta espelta" in dict_comidas[comida2].keys() or "Pasta integral" in dict_comidas[comida2].keys(): # No pasta dos comidas consecutivas
                       saltar = 1
                if "Pavo" in dict_comidas[comida1].keys() and "Pavo" in dict_comidas[comida2].keys(): # No pavo dos comidas seguidas
                   saltar = 1
                if "Pollo" in dict_comidas[comida1].keys() and "Pavo" in dict_comidas[comida2].keys(): # No pollo dos comidas seguidas
                   saltar = 1
                if saltar == 0:
                   comidas_wip.append(comida2)
                   cenas_wip.append(cena2)
                   j = j+1
                   comida1 = comida2
                   cena1 = cena2
                   if "Pescado" in dict_comidas[comida2].keys():
                       pescado_semana = pescado_semana + 1
                   if "Pescado" in dict_cenas[cena2].keys():
                       pescado_semana = pescado_semana + 1
                   if "Boniato" in dict_comidas[comida2].keys():
                       boniato_semana = boniato_semana + 1
                saltar = 0

            # Una vez generada una semana chequeo condiciones
            if pescado_semana <= 2 and pescado_semana >=1 and boniato_semana <= 2:
                print("Menu OK")
                print("Pescado:", pescado_semana, "Boniato:", boniato_semana)
                print("Intentos:",intentos)
                pescado_semana = 0
                boniato_semana = 0
                menu_ok = 1
                intentos = 0
                comidas.extend(comidas_wip)
                cenas.extend(cenas_wip)
        menu_ok = 0

    # Esta parte prepara los datos que hay en comidas y cenas para meter saltos de linea y que se vean bien las tablas
    sum = 0
    for line in comidas:
        prueb = line.strip().split(' ')
        while i < len(prueb):
            sum = sum + int(len(prueb[i]))
            if sum >= 17:
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
            if sum >= 17:
                prueb.insert(i, "\n")
                sum = 0
            i = i + 1
        i = 0
        sum = 0
        prueb = " ".join(prueb)
        cen.append(prueb)

    # Esta parte añade los ingredientes para que aparezcan en el menú
    for line in comidas:
        for key, value in dict_comidas.get(line).items():
            ingr_com.append(key)
            for item in value:
                ingr_com.append(item)
            ingr_com.append("\n")
            ingr_com = " ".join(ingr_com)
            in_com.append(ingr_com)
            ingr_com = []
        in_com = " ".join(in_com)
        i_com.append(in_com)
        in_com = []

    for line in cenas:
        for key, value in dict_cenas.get(line).items():
            ingr_cen.append(key)
            for item in value:
                ingr_cen.append(item)
            ingr_cen.append("\n")
            ingr_cen = " ".join(ingr_cen)
            in_cen.append(ingr_cen)
            ingr_cen = []
        in_cen = " ".join(in_cen)
        i_cen.append(in_cen)
        in_cen = []

    separador = [" ", " ", " ", " ", " ", " ", " "]
    separador2 = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    if semanas == 1:
        lunes = [comid[0], i_com[0], separador[0], cen[0], i_cen[0]]
        martes = [comid[1], i_com[1], separador[1], cen[1], i_cen[1]]
        miercoles = [comid[2], i_com[2], separador[2], cen[2], i_cen[2]]
        jueves = [comid[3], i_com[3], separador[3], cen[3], i_cen[3]]
        viernes = [comid[4], i_com[4], separador[4], cen[4], i_cen[4]]
        sabado = [comid[5], i_com[5], separador[5], cen[5], i_cen[5]]
        domingo = [comid[6], i_com[6], separador[6], cen[6], i_cen[6]]
    elif semanas == 2:
        lunes = [comid[0], i_com[0], separador[0], cen[0], i_cen[0], separador[0], separador2[0], comid[7], i_com[7], separador[0], cen[7], i_cen[7]]
        martes = [comid[1], i_com[1], separador[1], cen[1], i_cen[1], separador[1], separador2[1], comid[8], i_com[8], separador[1], cen[8], i_cen[8]]
        miercoles = [comid[2], i_com[2], separador[2], cen[2], i_cen[2], separador[2], separador2[2], comid[9], i_com[9], separador[2], cen[9], i_cen[9]]
        jueves = [comid[3], i_com[3], separador[3], cen[3], i_cen[3], separador[3], separador2[3], comid[10], i_com[10], separador[3], cen[10], i_cen[10]]
        viernes = [comid[4], i_com[4], separador[4], cen[4], i_cen[4], separador[4], separador2[4], comid[11], i_com[11], separador[4], cen[11], i_cen[11]]
        sabado = [comid[5], i_com[5], separador[5], cen[5], i_cen[5], separador[5], separador2[5], comid[12], i_com[12], separador[5], cen[12], i_cen[12]]
        domingo = [comid[6], i_com[6], separador[6], cen[6], i_cen[6], separador[6], separador2[6], comid[13], i_com[13], separador[6], cen[13], i_cen[13]]

    table = zip(lunes, martes, miercoles, jueves, viernes, sabado, domingo)
    print(tabulate(table, headers=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], tablefmt="fancy_grid"))

    # Este módulo crea el PDF con el menú
    doc = SimpleDocTemplate("menu.pdf", pagesize=landscape(A4))
    elements = []

    if semanas == 1:
        data = [separador2, comid, i_com, separador, cen, i_cen]
        t=Table(data,7*[3.8*cm], [1*cm, 2.6*cm, 4*cm, 0.3*cm, 2.6*cm, 4*cm])
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 2, colors.black),
                            ]))
    elif semanas == 2:
        data = [separador2, comid[:7], i_com[:7], separador, cen[:7], i_cen[:7], separador2, comid[7:], i_com[7:], separador, cen[7:], i_cen[7:]]
        t=Table(data,7*[3.8*cm], [1*cm, 2.6*cm, 4*cm, 0.3*cm, 2.6*cm, 4*cm, 1*cm, 2.6*cm, 4*cm, 0.3*cm, 2.6*cm, 4*cm])
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (6,5), 2, colors.black),
                            ('BOX', (0,6), (-1,-1), 2, colors.black),
                            ]))

    elements.append(t)
    doc.build(elements)
    return comidas, cenas


def generate_ingr_list():
    lista_ingr = []
    lista_ingrCant = []
    lista_ingrUd = []
    lista_ingrN = []
    #try:
    for item in menu_com:
        for key, value in dict_comidas.get(item).items():
            if key not in lista_ingr:
                lista_ingr.append(key)
                lista_ingrCant.append(value[0])
                lista_ingrUd.append(value[1])
                lista_ingrN.append(1)
            else:
                for i in lista_ingr:
                    if i == key:
                        if lista_ingrUd[lista_ingr.index(key)] == value[1]:
                            if lista_ingrCant[lista_ingr.index(key)] != "":
                                if ((lista_ingrCant[lista_ingr.index(key)] == "0.5") or (lista_ingrCant[lista_ingr.index(key)] == "1.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "1.5") or (lista_ingrCant[lista_ingr.index(key)] == "2.0")): # Un poco chapuza, para los aguacates... Puede que haga falta ampliarlo o mejorarlo
                                    lista_ingrCant[lista_ingr.index(key)] = float(lista_ingrCant[lista_ingr.index(key)]) + float(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                                else:
                                    lista_ingrCant[lista_ingr.index(key)] = int(lista_ingrCant[lista_ingr.index(key)]) + int(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                            lista_ingrN[lista_ingr.index(key)] = lista_ingrN[lista_ingr.index(key)] + 1
                        else:
                            print("Error en las unidades de medida, revisar comidas de la bbdd (%s)" % i)
    for item in menu_cen:
        for key, value in dict_cenas.get(item).items():
            if key not in lista_ingr:
                lista_ingr.append(key)
                lista_ingrCant.append(value[0])
                lista_ingrUd.append(value[1])
                lista_ingrN.append(1)
            else:
                for i in lista_ingr:
                    if i == key:
                        if lista_ingrUd[lista_ingr.index(key)] == value[1]:
                            if lista_ingrCant[lista_ingr.index(key)] != "":
                                if ((lista_ingrCant[lista_ingr.index(key)] == "0.5") or (lista_ingrCant[lista_ingr.index(key)] == "1.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "1.5") or (lista_ingrCant[lista_ingr.index(key)] == "2.0")): # Un poco chapuza, para los aguacates... Puede que haga falta ampliarlo o mejorarlo
                                    lista_ingrCant[lista_ingr.index(key)] = float(lista_ingrCant[lista_ingr.index(key)]) + float(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                                else:
                                    lista_ingrCant[lista_ingr.index(key)] = int(lista_ingrCant[lista_ingr.index(key)]) + int(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                            lista_ingrN[lista_ingr.index(key)] = lista_ingrN[lista_ingr.index(key)] + 1
                        else:
                            print("Error en las unidades de medida, revisar cenas de la bbdd (%s)" % i)

    c = canvas.Canvas("lista_ingredientes.pdf")
    y = 0
    c.drawString(100,790,"LISTA DE INGREDIENTES")
    for item in range(len(lista_ingr)):
        print(str(lista_ingrN[item])+ "x -  " + lista_ingr[item] + ": " + lista_ingrCant[item] + " " + lista_ingrUd[item])
        c.drawString(100,750-y,str(lista_ingrN[item])+ "x -  " + lista_ingr[item] + ": " + lista_ingrCant[item] + " " + lista_ingrUd[item])
        y = y + 15
    c.save()

    #except:
        #print("\nError al encontrar el menú. Genera un menú nuevo\n")


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
    print("\t1. Mostrar comidas o cenas")
    print("\t2. Añadir comidas o cenas")
    print("\t3. Generar lista de ingredientes")
    print("\t4. Buscar")
    print("\t5. Generar propuesta de menú")
    print("\t6. Salir")

    menu_ppal = int(input("\nSelecciona la opción: "))

    if menu_ppal == 1:
        print("Mostrar recetas")
        print("\t1. Mostrar comidas")
        print("\t2. Mostrar cenas")
        menu_show = int(input("Selecciona la opción: "))
        if menu_show == 1:
            print("MOSTRAR COMIDAS")
            show_recipes(dict_comidas)
        elif menu_show == 2:
            print("MOSTRAR CENAS")
            show_recipes(dict_cenas)
        else:
            print("Error")
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 2:
        print("Añadir recetas")
        print("\t1. Añadir comida")
        print("\t2. Añadir cena")
        menu_add = int(input("Selecciona la opción: "))
        if menu_add == 1:
            print("AÑADIR COMIDAS")
            add_recipes("Comida", dict_comidas)
        elif menu_add == 2:
            print("AÑADIR CENAS")
            add_recipes("Cena", dict_cenas)
        else:
            print("Error")
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 3:
        print("Generar lista de ingredientes")
        generate_ingr_list()
        input("\nPulsa Enter para volver al menú principal")

    elif menu_ppal == 4:
        print("Error")
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 5:
        print("Generar propuesta de menús")
        (menu_com, menu_cen) = generate_menu()
        input("Pulsa Enter para volver al menú principal")

    elif menu_ppal == 6:
        clear()
        break

    else:
        print("Error")
        input("Pulsa Enter para volver al menú principal")
