# !/usr/bin/python
# -*- coding: utf-8 -*-

# estructura diccionarios comidas y cenas
# {"plato":{"ingrediente":{cantidad,"ud medida"}}}


__author__ = 'Marcos Pérez Martín'
__title__ = 'MenuPlanner'
__date__ = '21/10/2019'
__version__ = '2.0.1'

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

from MenuPlanner_ui import QtWidgets, Ui_MainWindow
from SearchDialog_ui import Ui_Dialog as Ui_Dialog_Search
from AddRecipeDialog_ui import Ui_Dialog as Ui_Dialog_AddRecipe
from AddIngredientDialog_ui import Ui_Dialog as Ui_Dialog_AddIngredient
from ConfirmRecipeDialog_ui import Ui_Dialog as Ui_Dialog_ConfirmRecipe
from SettingsDialog_ui import Ui_Dialog as Ui_Dialog_Settings
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Ver si alguna de estas no hace falta para el funcionamiento
dict_comidas = {}
dict_cenas = {}
comidas = []
cenas = []
menu_com = []
menu_cen = []
lista_cant = []
lista_ingredientes = []
receta = ""

OK = 0
ERROR = -1


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """ Clase que controla la ventana principal de la aplicación y sus
    funciones.

    Arguments:
        QtWidgets.QMainWindow {} -- Objeto de tipo QMainWindow de QT
        Ui_MainWindow {} -- Interfaz de la ventana principal
    """
    def __init__(self, *args, **kwargs):
        """ Inicializa todo lo necesario para la interfaz gráfica.
        """
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("MenuPlanner")
        self.label.setText("MenuPlanner")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font: 30pt Comic Sans MS")

        self.pushButton.setText("Generar Menú")
        self.pushButton_2.setText("Generar Lista de Ingredientes")
        self.pushButton_3.setText("Buscar Recetas")
        self.pushButton_4.setText("Añadir Recetas")
        self.pushButton_5.setText("Ajustes")
        self.pushButton_6.setText("Salir")

        # Conectamos eventos con acciones
        self.pushButton.clicked.connect(generarmenu)
        self.pushButton_2.clicked.connect(generarlista)
        self.pushButton_3.clicked.connect(buscarrecetas)
        self.pushButton_4.clicked.connect(anadirrecetas)
        self.pushButton_5.clicked.connect(ajustes)
        self.pushButton_6.clicked.connect(exit)


class SearchDialog(QtWidgets.QDialog, Ui_Dialog_Search):

    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.setWindowTitle("Mostrar Recetas")

        self.label.setText("Mostrar:")
        self.comboBox.addItem("Comidas")
        self.comboBox.addItem("Cenas")
        self.comboBox.addItem("Ambos")

        self.radioButton.setText("Mostrar todas")
        self.radioButton_2.setText("Filtrar")
        self.radioButton.setChecked(True)

        self.label_2.setText("Ingrediente:")
        self.label_2.setEnabled(False)
        for item in sorted(set(lista_ingredientes)):
            self.comboBox_2.addItem(item)
        self.comboBox_2.setEnabled(False)

        self.radioButton.toggled.connect(self.no_filter)
        self.radioButton_2.toggled.connect(self.filter)

    def no_filter(self):
        self.label_2.setEnabled(False)
        self.comboBox_2.setEnabled(False)

    def filter(self):
        self.label_2.setEnabled(True)
        self.comboBox_2.setEnabled(True)


class AddRecipeDialog(QtWidgets.QDialog, Ui_Dialog_AddRecipe):

    def __init__(self, *args, **kwargs):
        super(AddRecipeDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.setWindowTitle("Añadir Receta")

        self.label.setText("Nombre:")
        self.lineEdit.setFocus()
        self.label_2.setText("Añadir a:")
        self.comboBox.addItem("Comidas")
        self.comboBox.addItem("Cenas")

    def accept(self):
        global receta
        global receta_orig

        if len(self.lineEdit.text()) <= 3:
            print("Error en la longitud del nombre, " +
                  str(len(self.lineEdit.text())) + " caracteres introducidos")
            self.label.setStyleSheet("color: red;")
            self.lineEdit.setStyleSheet("border: 1.5px solid red;")
            alert = QMessageBox()
            alert.setWindowTitle("Añadir Receta")
            alert.setIcon(QMessageBox.Critical)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.setText("El nombre es demasiado corto")
            alert.exec_()
        else:
            print("Se va a añadir " + self.lineEdit.text() + " a " +
                  self.comboBox.currentText())
            receta = self.comboBox.currentText()[0:-1] + ";"
            receta = receta + self.lineEdit.text() + ";"
            print(receta)
            receta_orig = receta
            diag = AddIngredientDialog()
            result = diag.exec_()
            if result == OK:
                alert = QMessageBox()
                alert.setWindowTitle("Receta Añadida")
                alert.setIcon(QMessageBox.Information)
                alert.setStandardButtons(QMessageBox.Ok)
                alert.setText("Receta añadida correctamente")
                alert.exec_()
                print("Salgo OK de Añadir Receta")
                self.done(OK)
            else:
                print("Salgo KO de Añadir Receta")


class AddIngredientDialog(QtWidgets.QDialog, Ui_Dialog_AddIngredient):

    def __init__(self, *args, **kwargs):
        super(AddIngredientDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Añadir Ingrediente")

        self.label.setText("Nombre:")
        for item in sorted(set(lista_ingredientes)):
            self.comboBox.addItem(item)
        self.comboBox.addItem("Otro - Indicar abajo")
        self.lineEdit.setDisabled(True)

        self.label_2.setText("Cantidad:")
        for item in sorted(lista_cant_tipicas.strip('][ ').split(', ')):
            self.comboBox_2.addItem(item[1:-1])
        self.comboBox_2.addItem("Otro - Indicar abajo")
        self.lineEdit_2.setDisabled(True)

        self.label_3.setText("Unidad de medida:")
        for item in sorted(lista_medidas.strip('][ ').split(', ')):
            self.comboBox_3.addItem(item[1:-1])
        self.comboBox_3.addItem("Otro - Indicar abajo")
        self.lineEdit_3.setDisabled(True)

        self.checkBox.setText("Último ingrediente a añadir")

        self.comboBox.currentIndexChanged.connect(self.on_combobox_change)
        self.comboBox_2.currentIndexChanged.connect(self.on_combobox_2_change)
        self.comboBox_3.currentIndexChanged.connect(self.on_combobox_3_change)

    def on_combobox_change(self, new_index):
        if new_index == len(self.comboBox) - 1:  # "Otro" es la última opción
            self.lineEdit.setDisabled(False)
        else:
            self.lineEdit.setDisabled(True)

    def on_combobox_2_change(self, new_index):
        if new_index == len(self.comboBox_2) - 1:  # "Otro" es la última opción
            self.lineEdit_2.setDisabled(False)
        else:
            self.lineEdit_2.setDisabled(True)

    def on_combobox_3_change(self, new_index):
        if new_index == len(self.comboBox_3) - 1:  # "Otro" es la última opción
            self.lineEdit_3.setDisabled(False)
        else:
            self.lineEdit_3.setDisabled(True)

    def accept(self):  # Si pongo otro no me debe dejar ponerlo en blanco
        global receta
        global receta_orig
        if self.comboBox.currentIndex() == len(self.comboBox) - 1:
            if self.lineEdit.text() != "":
                text_ingr = self.lineEdit.text()
            else:
                print("Error en ingrediente escrito")
        else:
            text_ingr = self.comboBox.currentText()

        if self.comboBox_2.currentIndex() == len(self.comboBox_2) - 1:
            if self.lineEdit_2.text() != "":
                text_cant = self.lineEdit_2.text()
            else:
                print("Error en cantidad escrita")
        else:
            text_cant = self.comboBox_2.currentText()

        if self.comboBox_3.currentIndex() == len(self.comboBox_3) - 1:
            if self.lineEdit_3.text() != "":
                text_uds = self.lineEdit_3.text()
            else:
                print("Error en unidades escritas")
        else:
            text_uds = self.comboBox_3.currentText()

        print("Ingrediente: " + text_ingr + ". Cantidad: " +
              text_cant + ". Unidades de medida: " + text_uds + ".")

        receta = receta + text_ingr + ":" + text_cant + ":" + text_uds

        alert = QMessageBox()
        alert.setWindowTitle("Ingrediente añadido")
        alert.setIcon(QMessageBox.Information)
        alert.setStandardButtons(QMessageBox.Ok)
        alert.setText("Ingrediente añadido correctamente")
        alert.exec_()

        if self.checkBox.isChecked():
            print("CheckBox Último Ingrediente marcado")
            diag = ConfirmRecipeDialog()
            result = diag.exec_()
            if result == OK:
                print("Salgo OK")
                self.done(OK)
            else:
                print("Salgo KO")
            # Cierro y me voy al principal, ya he terminado
        else:
            receta = receta + ":"
        print(receta)


class ConfirmRecipeDialog(QtWidgets.QDialog, Ui_Dialog_ConfirmRecipe):

    def __init__(self, *args, **kwargs):
        global receta
        global receta_orig
        super(ConfirmRecipeDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.setWindowTitle("Confirmar Receta")

        texto = ""
        receta_list = receta.split(";")
        ingr_list = receta_list[2].split(":")
        for item in ingr_list:
            if ingr_list.index(item) % 3 == 0:
                texto = texto + "\n"
            texto = texto + item + " "
        texto = texto + "\n"
        self.label.setText("¿Es correcta la receta?\n\n" + receta_list[0] +
                           ": " + receta_list[1] + "\n" + texto)

    def accept(self):
        print("Hace click en Aceptar")
        print(receta)
        self.done(OK)

    def reject(self):
        global receta
        global receta_orig
        print("Hace click en Cancelar")
        receta = receta_orig
        self.done(ERROR)


class SettingsDialog(QtWidgets.QDialog, Ui_Dialog_Settings):

    def __init__(self, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Ajustes")
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Guardar")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Cancelar")
        self.tabWidget.setCurrentIndex(0)

        # Textos de cada pestaña
        self.tabWidget.setTabText(0, "&General")
        self.tabWidget.setTabText(1, "&Restricciones")
        self.tabWidget.setTabText(2, "&Cantidades")
        self.tabWidget.setTabText(3, "&Seguridad")

        # Interfaz de pestaña GENERAL
        self.label_1_1.setText("Semanas:")
        self.spinBox_1_1.setValue(semanas)
        self.label_1_2.setText("Comensales:")
        self.spinBox_1_2.setValue(comensales)

        # Interfaz de pestaña RESTRICCIONES
        self.label_2_1.setText("Próximamente")

        # Interfaz de pestaña CANTIDADES
        self.label_3_1.setText("Unidades de medida:")
        self.lineEdit_3_1.setText(lista_medidas)
        self.label_3_2.setText("Cantidades parciales:")
        self.lineEdit_3_2.setText(lista_cant)
        self.label_3_3.setText("Cantidades típicas:")
        self.lineEdit_3_3.setText(lista_cant_tipicas)

        # Interfaz de pestaña SEGURIDAD
        self.label_4_1.setText("Número de copias de seguridad simultáneas:")
        self.spinBox_4_1.setValue(num_copias)


def generarmenu():
    """ Lanza la generación del menú y muestra un mensaje de confirmación
    """
    alert = QMessageBox()
    alert.setWindowTitle("Generar Menú")
    if generate_menu(semanas)[2] == OK:  # Ahora devuelvo comidas y cenas antes
        message = "Menú generado correctamente"
        print(message)
        alert.setIcon(QMessageBox.Information)
    else:
        message = "Error al generar el menú"
        print(message)
        alert.setIcon(QMessageBox.Critical)
    alert.setStandardButtons(QMessageBox.Ok)
    alert.setText(message)
    alert.exec_()


def generarlista():
    """ Lanza la generación de la lista de ingredientes y muestra
    un mensaje de confirmación
    """
    alert = QMessageBox()
    alert.setWindowTitle("Generar Lista de Ingredientes")
    if generate_ingr_list(comensales) == OK:
        message = "Lista de ingredientes generada correctamente"
        alert.setIcon(QMessageBox.Information)
    else:
        message = "Error al generar la lista de ingredientes"
        print("Error al generar la lista de ingredientes")
        alert.setIcon(QMessageBox.Critical)
    alert.setStandardButtons(QMessageBox.Ok)
    alert.setText(message)
    alert.exec_()


def buscarrecetas():
    """ Muestra las recetas del tipo elegido, permitiendo filtrar por
    ingredientes
    """
    diag = SearchDialog()
    result = diag.exec_()
    if result == 1:
        print("El usuario ha hecho click en OK")
        print("Buscando en " + str(diag.comboBox.currentText()))
        if diag.radioButton.isChecked() is True:
            print("Sin filtros")
            fil = ""
        elif diag.radioButton_2.isChecked() is True:
            print("Filtro: " + str(diag.comboBox_2.currentText()))
            fil = str(diag.comboBox_2.currentText())
        else:
            print("Error en los RadioButton: Ninguno seleccionado")
        if show_recipes(str(diag.comboBox.currentText()).lower(), fil) == OK:
            print("Búsqueda finalizada correctamente")
        else:
            print("Error en la búsqueda")
    elif result == 0:
        print("El usuario ha hecho click en CANCEL")


def anadirrecetas():
    """ Permite añadir nuevas recetas directamente desde la aplicación
    """
    diag = AddRecipeDialog()
    result = diag.exec_()
    if result == OK:
        print("Añado " + receta)
        ret = add_recipes()
        if ret != OK:
            print("Error al añadir receta")
        else:
            print("Receta añadida correctamente")
    else:
        print("Cancelado por el usuario")
    return ret


def ajustes():  # WIP. Falta que se guarde al modificar. Por ahora puedo verlos
    """ Gestión de los ajustes
    """
    diag = SettingsDialog()
    result = diag.exec_()


def show_recipes(tipo, filtro):
    """ Muestra un listado con los diccionarios de Comidas, Cenas o Ambos

    Arguments:
        tipo {str} -- puede venir "comidas", "cenas" o "ambos"
        filtro {str} -- puede venir un ingrediente o vacío si no hay filtro

    Returns:
        [int] -- OK (0): Si todo va bien
                 ERROR (-1): Si hay cualquier problema
    """

    ret = OK
    encontrado = 0
    if tipo in ("comidas", "cenas", "ambos"):
        if tipo == "comidas":
            dicc = dict_comidas
            iteraciones = 1
        elif tipo == "cenas":
            dicc = dict_cenas
            iteraciones = 1
        elif tipo == "ambos":
            dicc = dict_comidas
            iteraciones = 2
        for _ in range(iteraciones):
            for plato, ingredientes in dicc.items():
                if filtro == "" or filtro in ingredientes:
                    print("\n*", plato)
                    encontrado = 1
                for ingred, medidas in ingredientes.items():
                    if filtro == "" or filtro in ingredientes:
                        if (medidas[0] == 0 or medidas[0] == ""):
                            print("\t-", ingred + ": Al gusto")
                        else:
                            print("\t-", ingred + ":",
                                  " ".join(map(str, medidas)))
            if iteraciones == 2:  # Debo hacer una segunda iteración con cenas
                dicc = dict_cenas
                iteraciones -= 1
        if encontrado == 0:
            print("Ingrediente no encontrado")
    else:
        print("Error al mostrar recetas. Parámetro 'tipo': '" + tipo + "'")
        ret = ERROR
    return ret


def load_data():
    """ Carga los datos de los diccionarios y los ajustes para utilizarlos
    en el programa.
    """

    print("Cargando datos...")
    global semanas
    global comensales
    global lista_ingredientes
    global lista_medidas
    global lista_cant
    global lista_cant_tipicas
    global num_copias
    cantidad = []
    num_dospuntos = 0
    ret = OK
    with open("bbdd.txt") as fich:
        lists = [line.strip().split(';') for line in fich.readlines()]
    for line in lists:
        if line[0][0] == "#":  # Se ignora lo que venga en esa línea
            continue

        # Compruebo que haya tres ':' por ingrediente más 2 por el último
        for item in line:
            for caract in item:
                if caract == ":":
                    num_dospuntos += 1
        print("Línea " + str(lists.index(line) + 1))
        print("Número de ':': " + str(num_dospuntos))
        if (num_dospuntos - 2) % 3 == 0:
            print("Número de ingredientes: " +
                  str(int((num_dospuntos - 2) / 3)))
            print("Número de ':' Correcto")
        else:
            print("Número de ':' Incorrecto")
            return ERROR
        num_dospuntos = 0

        if line[0] == "Comida":
            com_cen = "com"
            dict_comidas[line[1]] = {}
        elif line[0] == "Cena":
            com_cen = "cen"
            dict_cenas[line[1]] = {}
        ingrs = line[2].strip().split(':')
        for i in range(len(ingrs)):
            if i % 3 == 0 or i % 3 == 3:
                ingrediente = ingrs[i]
                lista_ingredientes.append(ingrediente)
            if i % 3 == 1:
                cantidad.append(ingrs[i])
            if i % 3 == 2:
                cantidad.append(ingrs[i])
                if com_cen == "com":
                    dict_comidas[line[1]].update({ingrediente: cantidad})
                elif com_cen == "cen":
                    dict_cenas[line[1]].update({ingrediente: cantidad})
                cantidad = []
    print("Datos de recetas cargados")

    with open("settings") as fich:
        lists = [line.strip().split('#') for line in fich.readlines()]
    for line in lists:
        indice = lists.index(line)
        if indice == 0:
            semanas = int(line[0])
        elif indice == 1:
            comensales = int(line[0])
        elif indice == 2:
            lista_medidas = line[0]
        elif indice == 3:
            lista_cant = line[0]
        elif indice == 4:
            lista_cant_tipicas = line[0]
        elif indice == 5:
            num_copias = int(line[0])
    print("Ajustes cargados")
    return ret


def add_recipes():
    """ Permite añadir recetas a los diccionarios
    """
    ret = OK

    with open("bbdd.txt", "a") as fich:
        fich.write(receta + "\n")

    print("Plato añadido. Vuelvo a cargar datos")

    # Carga de datos
    ret = load_data()
    if ret != OK:
        print("Error cargando datos")
    else:
        print("Todos los datos cargados")
    return ret


def generate_menu(semanas):  # WIP. Returns, Revisión general, mejorar filtros, etc
    """ Genera el menú para las semanas que queramos. Tiene algunas condiciones
    Para considerar el menú como válido. En algún momento habrá que sacarlas
    de aquí para que no estén a piñón en el código y vengan desde ajustes o
    algo similar

    Arguments:
        semanas {int} -- Cantidad de semanas para las que genero menú. Viene
                         de los ajustes
    """
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
    ret = OK

    # Genero menú solo con condiciones de no repetir, y despues compruebo
    # las restricciones. Si están OK pongo menu_ok a 1
    for semana in range(semanas):
        print("Planificando semana", semana+1, "de", semanas)
        while menu_ok == 0:
            comidas_wip = []
            cenas_wip = []
            intentos = intentos + 1
            primera_ok = 0

            while primera_ok == 0:
                pescado_semana = 0
                boniato_semana = 0
                hamburguesa_semana = 0
                legumbres_semana = 0
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
                if(pescado_semana < 2 and boniato_semana < 2 and
                   comida1 != "Hamburguesa"):
                    primera_ok = 1

            cenas_wip.append(cena1)
            comidas_wip.append(comida1)

            while j < 7:
                print("j = " + str(j))
                comida2 = random.choice(list(dict_comidas.keys()))
                cena2 = random.choice(list(dict_cenas.keys()))
                if comida1 == comida2 or cena1 == cena2:
                    saltar = 1
                # if comida2 in comidas_wip or cena2 in cenas_wip:
                #    saltar = 1
                if("Arroz" in dict_comidas[comida1].keys()
                   and "Arroz" in dict_comidas[comida2].keys()):
                    # No arroz dos comidas consecutivas
                    print("Arroz dos comidas consecutivas")
                    saltar = 1
                if("Boniato" in dict_comidas[comida1].keys()
                   and "Boniato" in dict_comidas[comida2].keys()):
                    # No boniato dos comidas consecutivas
                    print("Boniato dos comidas consecutivas")
                    saltar = 1
                if("Pescado" in dict_comidas[comida1].keys()
                   and "Pescado" in dict_comidas[comida2].keys()):
                    # No pescado dos comidas consecutivas
                    print("Pescado dos comidas consecutivas")
                    saltar = 1
                if("Pescado" in dict_cenas[cena1].keys()
                   and "Pescado" in dict_cenas[cena2].keys()):
                    # No pescado dos cenas consecutivas
                    saltar = 1
                if("Pescado" in dict_cenas[cena1].keys()
                   and "Pescado" in dict_comidas[comida2].keys()):
                    # No pescado dos veces consecutivas
                    print("Pescado dos veces consecutivas")
                    saltar = 1
                if("Pescado" in dict_comidas[comida2].keys()
                   and "Pescado" in dict_cenas[cena2].keys()):
                    # No pescado dos veces consecutivas
                    print("Pescado dos veces consecutivas")
                    saltar = 1
                if("Patata" in dict_comidas[comida1].keys()
                   and "Patata" in dict_comidas[comida2].keys()):
                    # No patata dos comidas consecutivas
                    print("Patata dos comidas consecutivas")
                    saltar = 1
                if("Pasta" in dict_comidas[comida1].keys()
                   and "Pasta" in dict_comidas[comida2].keys()):
                    # No pasta dos comidas consecutivas
                    print("Pasta dos comidas consecutivas")
                    saltar = 1
                if("Pavo" in dict_comidas[comida1].keys()
                   and "Pavo" in dict_comidas[comida2].keys()):
                    # No pavo dos comidas seguidas
                    print("Pavo dos comidas consecutivas")
                    saltar = 1
                if("Pollo" in dict_comidas[comida1].keys()
                   and "Pollo" in dict_comidas[comida2].keys()):
                    # No pollo dos comidas seguidas
                    print("Pollo dos comidas consecutivas")
                    saltar = 1
                if comida2 == "Hamburguesa":
                    # Si ha salido hamburguesa y no es finde no nos vale
                    if (j != 4 and j != 5 and j != 6):
                        print("Hamburguesa y no es finde")
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
                    if "Legumbres" in dict_comidas[comida2].keys():
                        legumbres_semana = legumbres_semana + 1
                    if comida2 == "Hamburguesa":
                        hamburguesa_semana = hamburguesa_semana + 1
                saltar = 0

            # Una vez generada una semana chequeo condiciones
            if (pescado_semana <= 2 and pescado_semana >= 1
               and boniato_semana <= 2 and legumbres_semana <= 2):
               # and hamburguesa_semana == 1):
                print("Menu OK")
                print("Pescado:", pescado_semana, "Boniato:", boniato_semana,
                        "Hamburguesa:", hamburguesa_semana, "Legumbres:",
                        legumbres_semana)
                print("Intentos:", intentos)
                pescado_semana = 0
                boniato_semana = 0
                hamburguesa_semana = 0
                legumbres_semana = 0
                menu_ok = 1
                intentos = 0
                comidas.extend(comidas_wip)
                cenas.extend(cenas_wip)
            else:
                print("No cumple condiciones")
        menu_ok = 0

    # Esta parte prepara los datos que hay en comidas y cenas
    # para meter saltos de linea y que se vean bien las tablas
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
    separador2 = ["Lunes", "Martes", "Miércoles", "Jueves",
                  "Viernes", "Sábado", "Domingo"]

    if semanas == 1:
        lunes = [comid[0], i_com[0], separador[0], cen[0], i_cen[0]]
        martes = [comid[1], i_com[1], separador[1], cen[1], i_cen[1]]
        miercoles = [comid[2], i_com[2], separador[2], cen[2], i_cen[2]]
        jueves = [comid[3], i_com[3], separador[3], cen[3], i_cen[3]]
        viernes = [comid[4], i_com[4], separador[4], cen[4], i_cen[4]]
        sabado = [comid[5], i_com[5], separador[5], cen[5], i_cen[5]]
        domingo = [comid[6], i_com[6], separador[6], cen[6], i_cen[6]]
    elif semanas == 2:
        lunes = [comid[0], i_com[0], separador[0], cen[0], i_cen[0],
                 separador[0], separador2[0], comid[7], i_com[7],
                 separador[0], cen[7], i_cen[7]]
        martes = [comid[1], i_com[1], separador[1], cen[1], i_cen[1],
                  separador[1], separador2[1], comid[8], i_com[8],
                  separador[1], cen[8], i_cen[8]]
        miercoles = [comid[2], i_com[2], separador[2], cen[2], i_cen[2],
                     separador[2], separador2[2], comid[9], i_com[9],
                     separador[2], cen[9], i_cen[9]]
        jueves = [comid[3], i_com[3], separador[3], cen[3], i_cen[3],
                  separador[3], separador2[3], comid[10], i_com[10],
                  separador[3], cen[10], i_cen[10]]
        viernes = [comid[4], i_com[4], separador[4], cen[4], i_cen[4],
                   separador[4], separador2[4], comid[11], i_com[11],
                   separador[4], cen[11], i_cen[11]]
        sabado = [comid[5], i_com[5], separador[5], cen[5], i_cen[5],
                  separador[5], separador2[5], comid[12], i_com[12],
                  separador[5], cen[12], i_cen[12]]
        domingo = [comid[6], i_com[6], separador[6], cen[6], i_cen[6],
                   separador[6], separador2[6], comid[13], i_com[13],
                   separador[6], cen[13], i_cen[13]]

    table = zip(lunes, martes, miercoles, jueves, viernes, sabado, domingo)
    print(tabulate(table, headers=["Lunes", "Martes", "Miércoles", "Jueves",
                                   "Viernes", "Sábado", "Domingo"],
                   tablefmt="fancy_grid"))

    # Este módulo crea el PDF con el menú
    doc = SimpleDocTemplate("menu.pdf", pagesize=landscape(A4))
    elements = []

    if semanas == 1:
        data = [separador2, comid, i_com, separador, cen, i_cen]
        t = Table(data, 7*[3.8*cm], [1*cm, 2.6*cm, 4*cm, 0.3*cm, 2.6*cm, 4*cm])
        t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('INNERGRID', (0, 0), (-1, -1),
                               0.25, colors.black),
                               ('BOX', (0, 0), (-1, -1), 2, colors.black)]))
    elif semanas == 2:
        data = [separador2, comid[:7], i_com[:7], separador, cen[:7],
                i_cen[:7], separador2, comid[7:], i_com[7:], separador,
                cen[7:], i_cen[7:]]
        t = Table(data, 7*[3.8*cm], [1*cm, 2.6*cm, 4*cm, 0.3*cm, 2.6*cm,
                  4*cm, 1*cm, 2.6*cm, 4*cm, 0.3*cm, 2.6*cm, 4*cm])
        t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('INNERGRID', (0, 0), (-1, -1),
                               0.25, colors.black),
                               ('BOX', (0, 0), (6, 5), 2, colors.black),
                               ('BOX', (0, 6), (-1, -1), 2, colors.black)]))

    elements.append(t)
    doc.build(elements)
    menu_com = comidas
    menu_cen = cenas
    return comidas, cenas, ret


def generate_ingr_list(personas):
    """ Genera la lista de ingredientes del menú generado previamente, para
    el número de personas indicado

    Arguments:
        personas {int} -- Número de personas para calcular las cantidades
    """
    l_ingr = []
    l_ingr_cant = []
    l_ingr_ud = []
    l_ingr_num = []
    ret = OK

    for item in menu_com:
        for key, value in dict_comidas.get(item).items():
            if key not in l_ingr:
                l_ingr.append(key)
                if value[0] != "":
                    if value[0] in lista_cant:
                        l_ingr_cant.append(str(personas*float(value[0])))
                    else:
                        l_ingr_cant.append(str(personas*int(value[0])))
                else:
                    l_ingr_cant.append(value[0])
                l_ingr_ud.append(value[1])
                l_ingr_num.append(1)
            else:
                for i in l_ingr:
                    if i == key:
                        if l_ingr_ud[l_ingr.index(key)] == value[1]:
                            if l_ingr_cant[l_ingr.index(key)] != "":
                                if l_ingr_cant[l_ingr.
                                               index(key)] in lista_cant:
                                    print(l_ingr_cant
                                          [l_ingr.index(key)], value[0])
                                    l_ingr_cant[l_ingr.index(key)] = (
                                        float(l_ingr_cant
                                              [l_ingr.index(key)]) +
                                        float(personas)*float(value[0]))
                                    l_ingr_cant[l_ingr.index(key)] = (
                                        str(l_ingr_cant
                                            [l_ingr.index(key)])
                                    )
                                else:
                                    l_ingr_cant[l_ingr.index(key)] = (
                                        int(l_ingr_cant
                                            [l_ingr.index(key)]) +
                                        personas*int(value[0]))
                                    l_ingr_cant[l_ingr.index(key)] = (
                                        str(l_ingr_cant
                                            [l_ingr.index(key)]))
                            l_ingr_num[l_ingr.index(key)] += 1
                        else:
                            print("Error en las unidades de medida")
                            print("Revisar comidas de la bbdd (%s)" % i)
                            ret = ERROR
    for item in menu_cen:
        for key, value in dict_cenas.get(item).items():
            if key not in l_ingr:
                l_ingr.append(key)
                if value[0] != "":
                    if value[0] in lista_cant:
                        l_ingr_cant.append(str(personas*float(value[0])))
                    else:
                        l_ingr_cant.append(str(personas*int(value[0])))
                else:
                    l_ingr_cant.append(value[0])
                l_ingr_ud.append(value[1])
                l_ingr_num.append(1)
            else:
                for i in l_ingr:
                    print(i)
                    if i == key:
                        if l_ingr_ud[l_ingr.index(key)] == value[1]:
                            if l_ingr_cant[l_ingr.index(key)] != "":
                                if l_ingr_cant[l_ingr.
                                               index(key)] in lista_cant:
                                    a = float(l_ingr_cant[l_ingr.
                                                          index(key)])
                                    b = float(personas)*float(value[0])
                                    c = a + b
                                    l_ingr_cant[l_ingr.index(key)] = c
                                    d = str(l_ingr_cant
                                            [l_ingr.index(key)])
                                    l_ingr_cant[l_ingr.index(key)] = d
                                else:
                                    a = int(l_ingr_cant[l_ingr.index(key)])
                                    b = personas*int(value[0])
                                    c = a + b
                                    l_ingr_cant[l_ingr.index(key)] = c
                                    d = str(l_ingr_cant[l_ingr.index(key)])
                                    l_ingr_cant[l_ingr.index(key)] = d
                            l_ingr_num[l_ingr.index(key)] += 1
                        else:
                            print("Error en las unidades de medida")
                            print("Revisar cenas de la bbdd (%s)" % i)
                            ret = ERROR

    c = canvas.Canvas("lista_ingredientes.pdf")
    y = 0
    x = 100
    string = "LISTA DE INGREDIENTES PARA " + str(personas)
    c.drawString(200, 790, string)
    for item in range(len(l_ingr)):
        print(str(l_ingr_num[item]) + "x -  " + l_ingr[item] + ": " +
              l_ingr_cant[item] + " " + l_ingr_ud[item])
        c.drawString(x, 750-y, str(l_ingr_num[item]) + "x -  " +
                     l_ingr[item] + ": " + l_ingr_cant[item] + " "
                     + l_ingr_ud[item])
        y = y + 15
        if (750 - y) <= 100:
            x = 350
            y = 0
    c.save()
    return ret


if __name__ == "__main__":
    # Carga inicial de datos
    if load_data() != OK:
        print("Error cargando datos")
    else:
        print("Todos los datos cargados")
    APP = QtWidgets.QApplication([])
    WINDOW = MainWindow()
    WINDOW.show()
    APP.exec_()
