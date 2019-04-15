# estructura diccionarios comidas y cenas {"plato":{"ingrediente":{cantidad,"ud medida"}}}


__author__ = 'Marcos Pérez Martín'
__title__= 'MenuPlanner'
__date__ = '2019'
__version__ = '1.0'

from tkinter import *
from tkinter import ttk
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
modo_grafico = True
comidas = []
cenas = []
menu_com = []
menu_cen = []
var = ""

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
    global var
    if tipo == "comida" or tipo == "cena":
        if tipo == "comida":
            tipo = dict_comidas
        elif tipo == "cena":
            tipo = dict_cenas
        for plato, ingredientes in tipo.items():
            print("\n*",plato)
            var = var + "\n\n* " + plato
            for ingrediente, medidas in ingredientes.items():
                if (medidas[0] == 0 or medidas[0] == ""):
                    print("\t-", ingrediente + ": Al gusto")
                    var = var + "\n- " + ingrediente + ": Al gusto"
                else:
                    print("\t-", ingrediente + ":", " ".join(map(str, medidas)))
                    var = var + "\n- " + ingrediente + ": " + " ".join(map(str, medidas))
        var = var + "\n\n"
    else:
        print("Error al mostrar recetas")

# Función para buscar en cualquiera de los diccionarios
def search_recipes(filtro, tipo = " "):
    global var
    if tipo == " ":
        search_recipes(filtro, dict_comidas)
        search_recipes(filtro, dict_cenas)
    else:
        if tipo == "comida":
            tipo = dict_comidas
        elif tipo == "cena":
            tipo = dict_cenas
        for plato, ingredientes in tipo.items():
            if plato.upper() == filtro.upper():
                print("-",plato)
                var = var + "\n\n*" + plato
            for ingrediente, medidas in ingredientes.items():
                if (ingrediente.upper() == filtro.upper()):
                    print("-", plato)
                    var = var + "\n\n*" + plato

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

def generate_menu(semanas):
    comid = []
    global comidas
    comidas = []
    comidas_wip = []
    ingr_com = []
    in_com = []
    i_com = []
    cen = []
    global cenas
    cenas = []
    ingr_cen = []
    in_cen = []
    i_cen = []
    i = 0
    intentos = 0
    global menu_com
    global menu_cen

    saltar = 0
    menu_ok = 0

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
                if comida1 == comida2 or cena1 == cena2:
                    saltar = 1
                if comida2 in comidas_wip or cena2 in cenas_wip:
                    saltar = 1
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
            if sum >= 16:
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
            if sum >= 16:
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
    menu_com = comidas
    menu_cen = cenas
    return comidas, cenas


def generate_ingr_list(personas):
    lista_ingr = []
    lista_ingrCant = []
    lista_ingrUd = []
    lista_ingrN = []

    for item in menu_com:
        for key, value in dict_comidas.get(item).items():
            if key not in lista_ingr:
                lista_ingr.append(key)
                if value[0] != "":
                    if ((value[0] == "0.5") or (value[0] == "1.0")
                    or (value[0] == "1.5") or (value[0] == "2.0")): # Un poco chapuza, para los aguacates... Puede que haga falta ampliarlo o mejorarlo
                        lista_ingrCant.append(str(personas*float(value[0])))
                    else:
                        lista_ingrCant.append(str(personas*int(value[0])))
                else:
                    lista_ingrCant.append(value[0])
                lista_ingrUd.append(value[1])
                lista_ingrN.append(1)
            else:
                for i in lista_ingr:
                    if i == key:
                        if lista_ingrUd[lista_ingr.index(key)] == value[1]:
                            if lista_ingrCant[lista_ingr.index(key)] != "":
                                if ((lista_ingrCant[lista_ingr.index(key)] == "0.5") or (lista_ingrCant[lista_ingr.index(key)] == "1.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "1.5") or (lista_ingrCant[lista_ingr.index(key)] == "2.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "2.5") or (lista_ingrCant[lista_ingr.index(key)] == "3.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "3.5") or (lista_ingrCant[lista_ingr.index(key)] == "4.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "4.5") or (lista_ingrCant[lista_ingr.index(key)] == "5.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "5.5") or (lista_ingrCant[lista_ingr.index(key)] == "6.0")): # Un poco chapuza, para los aguacates... Puede que haga falta ampliarlo o mejorarlo
                                    print(lista_ingrCant[lista_ingr.index(key)], value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = float(lista_ingrCant[lista_ingr.index(key)]) + float(personas)*float(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                                else:

                                    lista_ingrCant[lista_ingr.index(key)] = int(lista_ingrCant[lista_ingr.index(key)]) + personas*int(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                            lista_ingrN[lista_ingr.index(key)] = lista_ingrN[lista_ingr.index(key)] + 1
                        else:
                            print("Error en las unidades de medida, revisar comidas de la bbdd (%s)" % i)
    for item in menu_cen:
        for key, value in dict_cenas.get(item).items():
            if key not in lista_ingr:
                lista_ingr.append(key)
                if value[0] != "":
                    if ((value[0] == "0.5") or (value[0] == "1.0")
                    or (value[0] == "1.5") or (value[0] == "2.0")): # Un poco chapuza, para los aguacates... Puede que haga falta ampliarlo o mejorarlo
                        lista_ingrCant.append(str(personas*float(value[0])))
                    else:
                        lista_ingrCant.append(str(personas*int(value[0])))
                else:
                    lista_ingrCant.append(value[0])
                lista_ingrUd.append(value[1])
                lista_ingrN.append(1)
            else:
                for i in lista_ingr:
                    if i == key:
                        if lista_ingrUd[lista_ingr.index(key)] == value[1]:
                            if lista_ingrCant[lista_ingr.index(key)] != "":
                                if ((lista_ingrCant[lista_ingr.index(key)] == "0.5") or (lista_ingrCant[lista_ingr.index(key)] == "1.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "1.5") or (lista_ingrCant[lista_ingr.index(key)] == "2.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "2.5") or (lista_ingrCant[lista_ingr.index(key)] == "3.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "3.5") or (lista_ingrCant[lista_ingr.index(key)] == "4.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "4.5") or (lista_ingrCant[lista_ingr.index(key)] == "5.0")
                                or (lista_ingrCant[lista_ingr.index(key)] == "5.5") or (lista_ingrCant[lista_ingr.index(key)] == "6.0")): # Un poco chapuza, para los aguacates... Puede que haga falta ampliarlo o mejorarlo
                                    lista_ingrCant[lista_ingr.index(key)] = float(lista_ingrCant[lista_ingr.index(key)]) + float(personas)*float(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                                else:
                                    lista_ingrCant[lista_ingr.index(key)] = int(lista_ingrCant[lista_ingr.index(key)]) + personas*int(value[0])
                                    lista_ingrCant[lista_ingr.index(key)] = str(lista_ingrCant[lista_ingr.index(key)])
                            lista_ingrN[lista_ingr.index(key)] = lista_ingrN[lista_ingr.index(key)] + 1
                        else:
                            print("Error en las unidades de medida, revisar cenas de la bbdd (%s)" % i)

    c = canvas.Canvas("lista_ingredientes.pdf")
    y = 0
    x = 100
    string = "LISTA DE INGREDIENTES PARA " + str(personas)
    c.drawString(200,790,string)
    for item in range(len(lista_ingr)):
        print(str(lista_ingrN[item])+ "x -  " + lista_ingr[item] + ": " + lista_ingrCant[item] + " " + lista_ingrUd[item])
        c.drawString(x,750-y,str(lista_ingrN[item])+ "x -  " + lista_ingr[item] + ": " + lista_ingrCant[item] + " " + lista_ingrUd[item])
        y = y + 15
        if (750 - y) <= 100:
            x = 350
            y = 0
    c.save()


##################################
# MENÚ PRINCIPAL EN MODO CONSOLA #
##################################

def modo_consola():

    print("Cargando datos...")
    load_data()
    time.sleep(0.5)
    print("Datos cargados")
    time.sleep(1)

    while(1):
        clear()
        print("*MENU*\n")
        print("\t1. Generar propuesta de menú")
        print("\t2. Generar lista de ingredientes")
        print("\t3. Mostrar recetas")
        print("\t4. Añadir recetas")
        print("\t5. Buscar")
        print("\t6. Salir")

        menu_ppal = int(input("\nSelecciona la opción: "))

        if menu_ppal == 1:

            print("Generar propuesta de menús")

            print("Selecciona para cuánto tiempo quieres generar menú")
            print("\t1. 1 semana")
            print("\t2. 2 semanas")
            semanas = int(input("\nSelecciona la opción: "))

            (menu_com, menu_cen) = generate_menu(semanas)
            input("Pulsa Enter para volver al menú principal")

        elif menu_ppal == 2:

            print("Generar lista de ingredientes")
            personas = int(input("Introduce número de personas para los cálculos: "))

            generate_ingr_list(personas)
            input("\nPulsa Enter para volver al menú principal")

        elif menu_ppal == 3:

            print("Mostrar recetas")
            print("\t1. Mostrar comidas")
            print("\t2. Mostrar cenas")
            menu_show = int(input("Selecciona la opción: "))
            if menu_show == 1:
                print("MOSTRAR COMIDAS")
                show_recipes("comida")
            elif menu_show == 2:
                print("MOSTRAR CENAS")
                show_recipes("cena")
            else:
                print("Error")
            input("Pulsa Enter para volver al menú principal")

        elif menu_ppal == 4:

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

        elif menu_ppal == 5:

            print("Buscar")
            filtro = input("Introduce el plato o ingrediente a buscar: ")
            print("\t1. Buscar en comidas")
            print("\t2. Buscar en cenas")
            print("\t3. Buscar en comidas y cenas")
            menu_search = int(input("Selecciona la opción: "))
            if menu_search == 1:
                print("BUSCAR EN COMIDAS")
                search_recipes(filtro, "comida")
            elif menu_search == 2:
                print("BUSCAR EN CENAS")
                search_recipes(filtro, "cena")
            elif menu_search == 3:
                print("BUSCAR EN COMIDAS Y CENAS")
                search_recipes(filtro)
            else:
                print("Error")
            input("Pulsa Enter para volver al menú principal")

        elif menu_ppal == 6:
            clear()
            break

        else:
            print("Error")
            input("Pulsa Enter para volver al menú principal")



##################################
# MENÚ PRINCIPAL EN MODO GRÁFICO #
##################################
class VerticalScrolledFrame:
    """
    A vertically scrolled Frame that can be treated like any other Frame
    ie it needs a master and layout and it can be a master.
    keyword arguments are passed to the underlying Frame
    except the keyword arguments 'width' and 'height', which
    are passed to the underlying Canvas
    note that a widget layed out in this frame will have Canvas as self.master,
    if you subclass this there is no built in way for the children to access it.
    You need to provide the controller separately.
    """
    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        self.outer = Frame(master, **kwargs)

        self.vsb = Scrollbar(self.outer, orient=VERTICAL)
        self.vsb.pack(fill=Y, side=RIGHT)
        self.canvas = Canvas(self.outer, highlightthickness=0, width=width, height=height)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
        # mouse scroll does not seem to work with just "bind"; You have
        # to use "bind_all". Therefore to use multiple windows you have
        # to bind_all in the current widget
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview

        self.inner = Frame(self.canvas)
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion = (0,0, x2, max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units" )
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units" )

class Aplicacion():

    def __init__(self):

        load_data()

        self.raiz = Tk()
        #self.raiz.geometry('600x400')
        self.raiz.resizable(width=False,height=False)
        self.raiz.title('MenuPlanner')

        # DEFINIR BARRA DE MENÚ DE LA APLICACION:
        barramenu = Menu(self.raiz)
        self.raiz['menu'] = barramenu

        # DEFINIR SUBMENÚS 'Opciones' y 'Ayuda':

        menuopciones = Menu(barramenu)
        menuayuda = Menu(barramenu)
        barramenu.add_cascade(menu=menuopciones, label='Opciones')
        barramenu.add_cascade(menu=menuayuda, label='Ayuda')

        menuopciones.add_command(label='Ver base de datos', command=self.raiz.destroy, compound=LEFT)
        menuopciones.add_separator()  # Agrega un separador
        menuopciones.add_command(label='Salir', command=self.raiz.destroy, compound=LEFT)

        menuayuda.add_command(label="Acerca de", command=self.f_acerca, compound=LEFT)

        self.bgenerarmenu = ttk.Button(self.raiz, text='Generar menú', command=self.generarmenu)
        self.bgenerarlista = ttk.Button(self.raiz, text='Generar lista de ingredientes', command=self.generarlista)
        self.bshow = ttk.Button(self.raiz, text='Mostrar recetas', command=self.show)
        self.badd = ttk.Button(self.raiz, text='Añadir recetas', command=self.add)
        self.bsearch = ttk.Button(self.raiz, text='Buscar', command=self.search)
        self.bsalir = ttk.Button(self.raiz, text='Salir', command=self.raiz.destroy)
        self.separador = ttk.Separator()

        self.bgenerarmenu.pack(side=TOP, fill=BOTH, expand=True, padx = 20, pady=20)
        self.bgenerarlista.pack(side=TOP, fill=BOTH, expand=True, padx = 20, pady=0)
        self.bshow.pack(side=TOP, fill=BOTH, expand=True, padx = 20, pady=20)
        self.badd.pack(side=TOP, fill=BOTH, expand=True, padx = 20, pady=0)
        self.bsearch.pack(side=TOP, fill=BOTH, expand=True, padx = 20, pady=20)
        self.separador.pack(side=TOP, fill=BOTH, expand=True, padx = 20, pady=0)
        self.bsalir.pack(side=TOP, fill=BOTH, expand=True, padx = 20, pady=20)


        self.bgenerarmenu.focus_set()
        self.raiz.mainloop()

    def generarmenu(self):

        # pequeña función para lanzar la función de generar menú y después una pantalla de OK
        def genmenu():
            generate_menu(self.semanas.get())
            ok = Toplevel()
            marco = ttk.Frame(ok, padding=(10, 10, 10, 10), relief=RAISED)
            marco.pack(side=TOP, fill=BOTH, expand=True)

            etiq = Label(marco, text="Operación completada")
            etiq.pack(side=TOP, padx=10, pady=10)
            boton = Button(marco, text="Salir", command=ok.destroy)
            boton.pack(side=TOP, padx=10, pady=10)
            boton.focus_set()

            ok.transient(master=self.dialogo)
            ok.grab_set()
            self.dialogo.wait_window(ok)

        # Muestra una nueva ventana que pide si quieres generar una o dos semanas
        self.dialogo = Toplevel()
        self.semanas = IntVar(value = 1)

        radiouna = ttk.Radiobutton(self.dialogo, text = 'Una semana', variable = self.semanas, value = 1)
        radiodos = ttk.Radiobutton(self.dialogo, text = 'Dos semanas', variable = self.semanas, value = 2)
        botongenerar = ttk.Button(self.dialogo, text='Generar', command = lambda: genmenu())
        botoncerrar = ttk.Button(self.dialogo, text='Cerrar', command=self.dialogo.destroy)

        radiouna.pack(side=TOP, padx=20, pady=20)
        radiodos.pack(side=TOP, padx=20, pady=0)
        botongenerar.pack(side=LEFT, padx=20, pady=20)
        botoncerrar.pack(side=RIGHT, padx=20, pady=20)

        botongenerar.wait_variable(self.semanas)

        self.dialogo.transient(master=self.raiz)
        self.dialogo.grab_set()
        self.raiz.wait_window(self.dialogo)



    def generarlista(self):

        # pequeña función para lanzar la función de generar lista de ingredientes y después una pantalla de OK
        def genlista():
            generate_ingr_list(self.personas.get())
            ok = Toplevel()
            marco = ttk.Frame(ok, padding=(10, 10, 10, 10), relief=RAISED)
            marco.pack(side=TOP, fill=BOTH, expand=True)

            etiq = Label(marco, text="Operación completada")
            etiq.pack(side=TOP, padx=10, pady=10)
            boton = Button(marco, text="Salir", command=ok.destroy)
            boton.pack(side=TOP, padx=10, pady=10)
            boton.focus_set()

            ok.transient(master=self.dialogo)
            ok.grab_set()
            self.dialogo.wait_window(ok)


        # Muestra una nueva ventana que pide si quieres generar lista para una o dos personas
        self.dialogo = Toplevel()
        self.personas = IntVar(value = 1)


        radiouna = ttk.Radiobutton(self.dialogo, text = 'Una persona', variable = self.personas, value = 1)
        radiodos = ttk.Radiobutton(self.dialogo, text = 'Dos personas', variable = self.personas, value = 2)
        botongenerar = ttk.Button(self.dialogo, text='Generar', command = lambda: genlista())
        botoncerrar = ttk.Button(self.dialogo, text='Cerrar', command=self.dialogo.destroy)

        radiouna.pack(side=TOP, padx=20, pady=20)
        radiodos.pack(side=TOP, padx=20, pady=0)
        botongenerar.pack(side=LEFT, padx=20, pady=20)
        botoncerrar.pack(side=RIGHT, padx=20, pady=20)

        self.dialogo.transient(master=self.raiz)
        self.dialogo.grab_set()
        self.raiz.wait_window(self.dialogo)

    def show(self):

        # pequeña función para lanzar la función de mostrar recetas en una nueva ventana con un scrollbar vertical
        def muestrarecetas():
            global var
            var = ""

            show_recipes(self.tipo.get())
            ok = Toplevel()

            frame = VerticalScrolledFrame(ok, width=470, relief=SUNKEN)
            frame.pack(fill=BOTH, expand=True) # fill window

            label = Label(frame, text = var)
            label.grid(column=1, row=1, sticky=W)

            ok.transient(master=self.dialogo)
            ok.grab_set()
            self.dialogo.wait_window(ok)

        # Muestra una nueva ventana que pide si quieres ver comidas o cenas
        self.dialogo = Toplevel()
        self.tipo = StringVar(value = "comida")
        self.txt = StringVar()


        radiocomidas = ttk.Radiobutton(self.dialogo, text = 'Comidas', variable = self.tipo, value = "comida")
        radiocenas = ttk.Radiobutton(self.dialogo, text = 'Cenas', variable = self.tipo, value = "cena")
        botonmostrar = ttk.Button(self.dialogo, text='Mostrar', command = lambda: muestrarecetas())
        botoncerrar = ttk.Button(self.dialogo, text='Cerrar', command=self.dialogo.destroy)

        radiocomidas.pack(side=TOP, padx=20, pady=20)
        radiocenas.pack(side=TOP, padx=20, pady=0)
        botonmostrar.pack(side=LEFT, padx=20, pady=20)
        botoncerrar.pack(side=RIGHT, padx=20, pady=20)

        self.dialogo.transient(master=self.raiz)
        self.dialogo.grab_set()
        self.raiz.wait_window(self.dialogo)

    def add(self):

        # Muestra una nueva ventana que pide si quieres añadir comidas o cenas
        self.dialogo = Toplevel()
        self.tipo = IntVar(value = 1)


        radiocomidas = ttk.Radiobutton(self.dialogo, text = 'Comidas', variable = self.tipo, value = 1)
        radiocenas = ttk.Radiobutton(self.dialogo, text = 'Cenas', variable = self.tipo, value = 2)
        botonanadir = ttk.Button(self.dialogo, text='Añadir', command=self.dialogo.destroy)
        botoncerrar = ttk.Button(self.dialogo, text='Cerrar', command=self.dialogo.destroy)

        radiocomidas.pack(side=TOP, padx=20, pady=20)
        radiocenas.pack(side=TOP, padx=20, pady=0)
        botonanadir.pack(side=LEFT, padx=20, pady=20)
        botoncerrar.pack(side=RIGHT, padx=20, pady=20)

        self.dialogo.transient(master=self.raiz)
        self.dialogo.grab_set()
        self.raiz.wait_window(self.dialogo)

    def search(self):

        # pequeña función para lanzar la función de buscar recetas en una nueva ventana con un scrollbar vertical
        def buscarecetas():
            global var
            var = ""

            search_recipes(self.busq.get(), self.tipo.get())
            ok = Toplevel()

            frame = VerticalScrolledFrame(ok, width=470, relief=SUNKEN)
            frame.pack(fill=BOTH, expand=True) # fill window

            label = Label(frame, text = var)
            label.grid(column=1, row=1, sticky=W)

            ok.transient(master=self.dialogo)
            ok.grab_set()
            self.dialogo.wait_window(ok)

        # Muestra una nueva ventana que pide si quieres buscar en comidas, cenas o ambas
        self.dialogo = Toplevel()
        self.tipo = StringVar(value = "comida")
        self.busq = StringVar()

        labelbusqueda = ttk.Label(self.dialogo, text="Comida o ingrediente:")
        entrybusqueda = ttk.Entry(self.dialogo, textvariable=self.busq, width=25)
        radiocomidas = ttk.Radiobutton(self.dialogo, text = 'Comidas', variable = self.tipo, value = "comida")
        radiocenas = ttk.Radiobutton(self.dialogo, text = 'Cenas', variable = self.tipo, value = "cena")
        radioambas = ttk.Radiobutton(self.dialogo, text = 'Ambas', variable = self.tipo, value = " ")
        botonbuscar = ttk.Button(self.dialogo, text='Buscar', command = lambda: buscarecetas())
        botoncerrar = ttk.Button(self.dialogo, text='Cerrar', command=self.dialogo.destroy)

        labelbusqueda.pack(side=TOP, padx=20, pady=20)
        entrybusqueda.pack(side=TOP, padx=20, pady=0)
        radiocomidas.pack(side=TOP, padx=20, pady=20)
        radiocenas.pack(side=TOP, padx=20, pady=0)
        radioambas.pack(side=TOP, padx=20, pady=20)
        botonbuscar.pack(side=LEFT, padx=20, pady=20)
        botoncerrar.pack(side=RIGHT, padx=20, pady=20)

        self.dialogo.transient(master=self.raiz)
        self.dialogo.grab_set()
        self.raiz.wait_window(self.dialogo)

    def f_acerca(self):

        acerca = Toplevel()
        #acerca.geometry("320x200")
        acerca.resizable(width=False, height=False)
        acerca.title("Acerca de")
        marco1 = ttk.Frame(acerca, padding=(10, 10, 10, 10),
                           relief=RAISED)
        marco1.pack(side=TOP, fill=BOTH, expand=True)

        etiq1 = Label(marco1, text=__title__+" v"+__version__)
        etiq1.pack(side=TOP, padx=10)
        etiq2 = Label(marco1, text=__author__)
        etiq2.pack(side=TOP, padx=10)
        etiq3 = Label(marco1, text=__date__)
        etiq3.pack(side=TOP, padx=10)
        boton1 = Button(marco1, text="Salir", command=acerca.destroy)
        boton1.pack(side=TOP, padx=10, pady=10)
        boton1.focus_set()
        acerca.transient(self.raiz)
        self.raiz.wait_window(acerca)



def main():

    if modo_grafico == True:
        mi_app = Aplicacion()
    else:
        modo_consola()
    return 0

if __name__ == '__main__':
    main()
