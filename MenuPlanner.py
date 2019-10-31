# !/usr/bin/python
# -*- coding: utf-8 -*-

# estructura diccionarios comidas y cenas
# {"plato":{"ingrediente":{cantidad,"ud medida"}}}


__author__ = 'Marcos Pérez Martín'
__title__ = 'MenuPlanner'
__date__ = '31/10/2019'
__version__ = '2.0.2'

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
import json
import logging.config
import shutil
import glob
from datetime import datetime

from MenuPlanner_ui import QtWidgets, Ui_MainWindow
from SearchDialog_ui import Ui_Dialog as Ui_Dialog_Search
from AddRecipeDialog_ui import Ui_Dialog as Ui_Dialog_AddRecipe
from AddIngredientDialog_ui import Ui_Dialog as Ui_Dialog_AddIngredient
from ConfirmRecipeDialog_ui import Ui_Dialog as Ui_Dialog_ConfirmRecipe
from SettingsDialog_ui import Ui_Dialog as Ui_Dialog_Settings
from ShowRecipesDialog_ui import Ui_Dialog as Ui_Dialog_ShowRecipes
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Ver si alguna de estas no hace falta para el funcionamiento
# Quizás más limpio pasarlas al main
dict_comidas = {}
dict_cenas = {}
comidas = []
cenas = []
menu_com = []
menu_cen = []
lista_cant = []
lista_ingredientes = []
receta = ""
logger = logging.getLogger(__name__)
show = ""

OK = 0
ERROR = -1
CANCEL = -2


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
        self.pushButton.clicked.connect(generar_menu)
        self.pushButton_2.clicked.connect(generar_lista)
        self.pushButton_3.clicked.connect(buscar_recetas)
        self.pushButton_4.clicked.connect(anadir_recetas)
        self.pushButton_5.clicked.connect(mostrar_ajustes)
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
        logger.debug("Radiobutton Sin Filtro seleccionado")
        self.label_2.setEnabled(False)
        self.comboBox_2.setEnabled(False)

    def filter(self):
        logger.debug("Radiobutton Con Filtro seleccionado")
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

        logger.info("Click en ACEPTAR")
        if len(self.lineEdit.text()) <= 3:
            logger.error("Error en la longitud del nombre, %d " +
                         "caracteres introducidos", len(self.lineEdit.text()))
            self.label.setStyleSheet("color: red;")
            self.lineEdit.setStyleSheet("border: 1.5px solid red;")
            alert = QMessageBox()
            alert.setWindowTitle("Añadir Receta")
            alert.setIcon(QMessageBox.Critical)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.setText("El nombre es demasiado corto")
            alert.exec_()
        else:
            logger.debug("Se va a añadir '%s' a '%s'",
                         self.lineEdit.text(), self.comboBox.currentText())
            receta = self.comboBox.currentText()[0:-1] + ";"
            receta = receta + self.lineEdit.text() + ";"
            logger.debug(receta)
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
                logger.info("Salgo de la función")
                self.done(OK)
            else:
                logger.error("Error al añadir ingredientes")
                logger.info("Salgo de la función")

    def reject(self):
        global receta

        logger.info("Click en CANCELAR")
        receta = ""
        logger.info("Salgo de la función")
        self.done(ERROR)


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

        logger.info("Click en ACEPTAR")
        if self.comboBox.currentIndex() == len(self.comboBox) - 1:
            if self.lineEdit.text() != "":
                text_ingr = self.lineEdit.text()
            else:
                logger.error("Error en ingrediente escrito (vacío)")
        else:
            text_ingr = self.comboBox.currentText()

        if self.comboBox_2.currentIndex() == len(self.comboBox_2) - 1:
            if self.lineEdit_2.text() != "":
                text_cant = self.lineEdit_2.text()
            else:
                logger.error("Error en cantidad escrita (vacía)")
        else:
            text_cant = self.comboBox_2.currentText()

        if self.comboBox_3.currentIndex() == len(self.comboBox_3) - 1:
            if self.lineEdit_3.text() != "":
                text_uds = self.lineEdit_3.text()
            else:
                logger.error("Error en unidades escritas (vacías)")
        else:
            text_uds = self.comboBox_3.currentText()

        logger.debug("Ingrediente: '%s'", text_ingr)
        logger.debug("Cantidad: '%s'", text_cant)
        logger.debug("Unidades de medida: '%s'", text_uds)

        receta = receta + text_ingr + ":" + text_cant + ":" + text_uds

        alert = QMessageBox()
        alert.setWindowTitle("Ingrediente añadido")
        alert.setIcon(QMessageBox.Information)
        alert.setStandardButtons(QMessageBox.Ok)
        alert.setText("Ingrediente añadido correctamente")
        alert.exec_()

        if self.checkBox.isChecked():
            logger.debug("CheckBox Último Ingrediente marcado")
            diag = ConfirmRecipeDialog()
            result = diag.exec_()
            if result == OK:
                logger.info("Salgo OK de la función")
                self.done(OK)
            else:
                logger.error("Error al confirmar receta")
                logger.info("Salgo de la función")
        else:
            receta = receta + ":"

    def reject(self):
        global receta

        logger.info("Click en CANCELAR")
        logger.debug("Limpio receta (actualmente: '%s')", receta)
        receta = ""
        logger.debug("Receta limpia: '%s'", receta)
        logger.info("Salgo de la función")
        self.done(ERROR)


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
        logger.info("Click en ACEPTAR")
        logger.debug(receta)
        logger.info("Salgo OK de la función")
        self.done(OK)

    def reject(self):
        global receta
        global receta_orig

        logger.info("Click en CANCELAR")
        receta = receta_orig
        logger.info("Salgo de la función")
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
        self.label_1_3.setText("Mostrar menú en consola")
        self.checkBox_1_3.setText("")
        self.checkBox_1_3.setChecked(menu_consola)
        self.label_1_4.setText("Mostrar lista de ingredientes en consola")
        self.checkBox_1_4.setText("")
        self.checkBox_1_4.setChecked(lista_consola)
        self.label_1_5.setText("Generar PDF de menú")
        self.checkBox_1_5.setText("")
        self.checkBox_1_5.setChecked(menu_pdf)
        self.label_1_6.setText("Generar PDF de lista de ingredientes")
        self.checkBox_1_6.setText("")
        self.checkBox_1_6.setChecked(lista_pdf)

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

    def accept(self):
        logger.debug("Click en GUARDAR")

        logger.debug("Ajustes que se guardan:")
        logger.debug("Semanas: %d", self.spinBox_1_1.value())
        logger.debug("Comensales: %d", self.spinBox_1_2.value())
        logger.debug("Menu_consola: %d", self.checkBox_1_3.isChecked())
        logger.debug("Lista_consola: %d", self.checkBox_1_4.isChecked())
        logger.debug("Menu_pdf: %d", self.checkBox_1_5.isChecked())
        logger.debug("Lista_pdf: %d", self.checkBox_1_6.isChecked())
        logger.debug("lista_medidas: %s", self.lineEdit_3_1.text())
        logger.debug("lista_cant: %s", self.lineEdit_3_2.text())
        logger.debug("lista_cant_tipicas: %s", self.lineEdit_3_3.text())
        logger.debug("Num_copias: %d", self.spinBox_4_1.value())

        with open("settings") as fich:
            lists = [line.strip().split('#') for line in fich.readlines()]
        fich_new = open("new_settings", "w")
        for line in lists:
            indice = lists.index(line)
            if indice == 0:  # Semanas
                fich_new.write(str(self.spinBox_1_1.value()))
            elif indice == 1:  # Comensales
                fich_new.write(str(self.spinBox_1_2.value()))
            elif indice == 2:  # Lista medidas
                fich_new.write(self.lineEdit_3_1.text())
            elif indice == 3:  # Lista Cantidades
                fich_new.write(self.lineEdit_3_2.text())
            elif indice == 4:  # Lista Cantidades Típicas
                fich_new.write(self.lineEdit_3_3.text())
            elif indice == 5:  # Numero de copias
                fich_new.write(str(self.spinBox_4_1.value()))
            elif indice == 6:  # Menú Consola
                fich_new.write(str(int(self.checkBox_1_3.isChecked())))
            elif indice == 7:  # Lista Consola
                fich_new.write(str(int(self.checkBox_1_4.isChecked())))
            elif indice == 8:  # Menú PDF
                fich_new.write(str(int(self.checkBox_1_5.isChecked())))
            elif indice == 9:  # Lista PDF
                fich_new.write(str(int(self.checkBox_1_6.isChecked())))

            fich_new.write("#" + line[1])
            if indice != lists.index(lists[-1]):  # Si no es última línea '\n'
                fich_new.write("\n")

        shutil.move("new_settings", "settings")
        logger.debug("Fichero renombrado de 'new_settings' a 'settings'")
        logger.debug("Ajustes guardados")

        self.done(OK)

    def reject(self):
        logger.debug("Click en CANCELAR")
        self.done(CANCEL)


class ShowRecipesDialog(QtWidgets.QDialog, Ui_Dialog_ShowRecipes):

    def __init__(self, *args, **kwargs):
        super(ShowRecipesDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Mostrar Recetas")

        self.label.setText(show)


def setup_logging(default_path='logging.json', default_level=logging.DEBUG,
                  env_key='LOG_CFG'):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as fich:
            config = json.load(fich)
        logging.config.dictConfig(config)
        logger.info("Configuración del Logger cargada desde fichero")
    else:
        logging.basicConfig(level=default_level)
        logger.info("Configuración del Logger básica, no hay fichero")


def generar_menu():
    """ Lanza la generación del menú y muestra un mensaje de confirmación
    """
    logger.info("Click en GENERAR MENÚ")
    alert = QMessageBox()
    alert.setWindowTitle("Generar Menú")
    if generate_menu(semanas)[2] == OK:  # Devuelvo comidas y cenas, por eso 2
        if menu_pdf:
            message = ("<a href=menu.pdf> <font color=black>Menú generado " +
                       "correctamente. Click para abrir</font></a>")
        else:
            message = "Menú Generado correctamente"
        logger.info(message)
        alert.setIcon(QMessageBox.Information)
    else:
        message = "Error al generar el menú"
        logger.error(message)
        alert.setIcon(QMessageBox.Critical)
    alert.setStandardButtons(QMessageBox.Ok)
    alert.setText(message)
    alert.exec_()
    logger.info("Salgo de la función")


def generar_lista():
    """ Lanza la generación de la lista de ingredientes y muestra
    un mensaje de confirmación
    """
    logger.info("Click en GENERAR LISTA DE INGREDIENTES")
    alert = QMessageBox()
    alert.setWindowTitle("Generar Lista de Ingredientes")
    if not menu_com or not menu_cen:  # Si no hay menú comidas o cenas
        logger.error("No hay menú generado")
        message = "Error al generar la lista de ingredientes\n"
        message = message + "No hay menú generado"
        alert.setIcon(QMessageBox.Critical)
    else:
        if generate_ingr_list(comensales) == OK:
            message = ("<a href=lista_ingredientes.pdf> <font color=black>" +
                       "Lista generada correctamente." +
                       "Click para abrir</font></a>")
            logger.info(message)
            alert.setIcon(QMessageBox.Information)
        else:
            message = "Error al generar la lista de ingredientes"
            logger.error(message)
            alert.setIcon(QMessageBox.Critical)
    alert.setStandardButtons(QMessageBox.Ok)
    alert.setText(message)
    alert.exec_()
    logger.info("Salgo de la función")


def buscar_recetas():
    """ Muestra las recetas del tipo elegido, permitiendo filtrar por
    ingredientes
    """
    global show
    logger.info("Click en BUSCAR RECETAS")
    dia = SearchDialog()
    result = dia.exec_()
    ret = OK

    if result == 1:
        logger.info("Click en OK")
        logger.debug("Buscando en %s", str(dia.comboBox.currentText()))
        if dia.radioButton.isChecked() is True:
            logger.debug("Sin filtros")
            fil = ""
        elif dia.radioButton_2.isChecked() is True:
            logger.debug("Filtro: %s", str(dia.comboBox_2.currentText()))
            fil = str(dia.comboBox_2.currentText())
        else:
            logger.error("Error en los RadioButton: Ninguno seleccionado")
            ret = ERROR
            return ret
        (st, show) = show_recipes(str(dia.comboBox.currentText()).lower(), fil)
        if st == OK:
            logger.info("Búsqueda finalizada correctamente")
            alert = ShowRecipesDialog()
            alert.exec_()

        else:
            logger.error("Error en la búsqueda")
            alert = ShowRecipesDialog()
            alert.exec_()

    elif result == 0:
        logger.info("Click en CANCEL")
    logger.info("Salgo de la función")
    return ret


def anadir_recetas():
    """ Permite añadir nuevas recetas directamente desde la aplicación
    """
    logger.info("Click en AÑADIR RECETAS")
    diag = AddRecipeDialog()
    result = diag.exec_()
    if result == OK:
        logger.info("Result: OK")
        logger.debug("Añado '%s'", receta)
        ret = add_recipes()
        if ret != OK:
            logger.error("Error al añadir receta")
        else:
            logger.info("Receta añadida correctamente")
    else:
        ret = ERROR
        logger.info("Click en CANCEL")
    logger.info("Salgo de la función")
    return ret


def mostrar_ajustes():
    """ Gestión de los ajustes
    """
    logger.info("Click en AJUSTES")
    diag = SettingsDialog()
    result = diag.exec_()
    logger.info("Salgo de la función")


def show_recipes(tipo, filtro):
    """ Muestra un listado de Comidas, Cenas o Ambos, con o sin filtro

    Arguments:
        tipo {str} -- puede venir "comidas", "cenas" o "ambos"
        filtro {str} -- puede venir un ingrediente o vacío si no hay filtro

    Returns:
        [int] -- OK (0): Si todo va bien
                 ERROR (-1): Si hay cualquier problema
    """

    ret = OK
    encontrado = 0
    resultado = ""

    logger.info("Entro con tipo = '%s', filtro = '%s'", tipo, filtro)
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
                    #print("\n*", plato)
                    resultado += "\n*" + plato
                    encontrado = 1
                for ingred, medidas in ingredientes.items():
                    if filtro == "" or filtro in ingredientes:
                        if (medidas[0] == 0 or medidas[0] == ""):
                            #print("\t-", ingred + ": Al gusto")
                            resultado += "\n\t-" + ingred + ": Al gusto"
                        else:
                            #print("\t-", ingred + ":",
                            #      " ".join(map(str, medidas)))
                            resultado += "\n\t-" + ingred + ":"
                            resultado += " ".join(map(str, medidas))
            if iteraciones == 2:  # Debo hacer una segunda iteración con cenas
                dicc = dict_cenas
                iteraciones -= 1
        if encontrado == 0:
            logger.debug("Ingrediente no encontrado")
            resultado = "Ingrediente no encontrado"
    else:
        logger.error("Error al mostrar recetas. 'tipo': '%s', filtro: '%s'",
                     tipo, filtro)
        ret = ERROR
    logger.info("Salgo de la función")
    return ret, resultado


def load_data(modo):
    """ Carga los datos de los diccionarios y los ajustes para utilizarlos
    en el programa.

    Modo:
        bbdd: Comidas
        settings: Ajustes
        todo: Comidas + Ajustes
    """

    logger.info("Entro a la función con 'modo' = '%s'", modo)
    ret = OK

    if modo == "bbdd" or modo == "todo":
        global lista_ingredientes
        cantidad = []
        num_dospuntos = 0

        with open("bbdd") as fich:
            lists = [line.strip().split(';') for line in fich.readlines()]
        for line in lists:
            # Compruebo que haya tres ':' por ingrediente más 2 por el último
            for item in line:
                for caract in item:
                    if caract == ":":
                        num_dospuntos += 1
            logger.debug("Línea %s", str(lists.index(line) + 1))
            logger.debug("Número de ':': %s", str(num_dospuntos))
            if (num_dospuntos - 2) % 3 == 0:
                logger.debug("Número de ingredientes: %s",
                             str(int((num_dospuntos - 2) / 3)))
                logger.debug("Número de ':' Correcto")
            else:
                logger.error("Número de ':' Incorrecto")
                return ERROR
            num_dospuntos = 0

            if line[0][0] == "#":  # Se ignora lo que venga en esa línea
                continue

            if line[0] == "Comida":
                com_cen = "com"
                dict_comidas[line[1]] = {}
            elif line[0] == "Cena":
                com_cen = "cen"
                dict_cenas[line[1]] = {}

            logger.debug("Procesando: %s", line)

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
        logger.info("Datos de recetas cargados")

    if modo == "settings" or modo == "todo":
        global semanas
        global comensales
        global lista_medidas
        global lista_cant
        global lista_cant_tipicas
        global num_copias
        global menu_consola
        global menu_pdf
        global lista_consola
        global lista_pdf

        with open("settings") as fich:
            lists = [line.strip().split('#') for line in fich.readlines()]
        for line in lists:
            indice = lists.index(line)
            if indice == 0:
                semanas = int(line[0])
                logger.debug("semanas: %s", semanas)
            elif indice == 1:
                comensales = int(line[0])
                logger.debug("comensales: %s", comensales)
            elif indice == 2:
                lista_medidas = line[0]
                logger.debug("lista_medidas: %s", lista_medidas)
            elif indice == 3:
                lista_cant = line[0]
                logger.debug("lista_cant: %s", lista_cant)
            elif indice == 4:
                lista_cant_tipicas = line[0]
                logger.debug("lista_cant_tipicas: %s", lista_cant_tipicas)
            elif indice == 5:
                num_copias = int(line[0])
                logger.debug("num_copias: %s", num_copias)
            elif indice == 6:
                menu_consola = int(line[0])
                logger.debug("menu_consola: %s", menu_consola)
            elif indice == 7:
                lista_consola = int(line[0])
                logger.debug("lista_consola: %s", lista_consola)
            elif indice == 8:
                menu_pdf = int(line[0])
                logger.debug("menu_pdf: %s", menu_pdf)
            elif indice == 9:
                lista_pdf = int(line[0])
                logger.debug("lista_pdf: %s", lista_pdf)
        logger.info("Ajustes cargados")

    if modo not in ("bbdd", "settings", "todo"):
        logger.error("Parámetro desconocido")
        ret = ERROR

    logger.debug("Salgo de la función")
    return ret


def add_recipes():
    """ Permite añadir recetas a los diccionarios
    """
    ret = OK

    logger.info("Entro a la función")
    with open("bbdd", "a") as fich:
        fich.write(receta + "\n")

    logger.debug("Plato añadido. Vuelvo a cargar datos")

    # Carga de datos de BBDD
    ret = load_data("bbdd")
    if ret != OK:
        logger.error("Error cargando datos")
        logger.info("Salgo de la función")
    else:
        logger.info("Todos los datos cargados")
        logger.info("Salgo de la función")
    return ret


def generate_menu(semanas):  # WIP. Returns, Revi general, mejorar filtros, etc
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

    logger.info("Entro con semanas = '%d'", semanas)
    # Genero menú solo con condiciones de no repetir, y despues compruebo
    # las restricciones. Si están OK pongo menu_ok a 1
    for semana in range(semanas):
        logger.debug("Planificando semana '%d' de '%d'", semana+1, semanas)
        while menu_ok == 0:
            comidas_wip = []
            cenas_wip = []
            intentos = intentos + 1
            primera_ok = 0

            while primera_ok == 0:
                logger.debug("Generando el día 0: Lunes")
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

            if primera_ok == 1:
                logger.debug("Día 0 (Lunes) generado")
                cenas_wip.append(cena1)
                comidas_wip.append(comida1)

            while j < 7:
                logger.debug("generate_menu(): Generando el día %d", j)
                comida2 = random.choice(list(dict_comidas.keys()))
                cena2 = random.choice(list(dict_cenas.keys()))
                if comida1 == comida2:
                    logger.debug("Comidas seguidas iguales")
                    saltar = 1
                elif cena1 == cena2:
                    logger.debug("Cenas seguidas iguales")
                    saltar = 1
                else:
                    # if comida2 in comidas_wip or cena2 in cenas_wip:
                    #    saltar = 1
                    if("Arroz" in dict_comidas[comida1].keys()
                       and "Arroz" in dict_comidas[comida2].keys()):
                        logger.debug("Arroz dos comidas consecutivas")
                        logger.debug("'%s' y '%s'", comida1, comida2)
                        saltar = 1
                    if("Boniato" in dict_comidas[comida1].keys()
                       and "Boniato" in dict_comidas[comida2].keys()):
                        logger.debug("Boniato dos comidas consecutivas")
                        logger.debug("'%s' y '%s'", comida1, comida2)
                        saltar = 1
                    if("Pescado" in dict_comidas[comida1].keys()
                       and "Pescado" in dict_comidas[comida2].keys()):
                        logger.debug("Pescado dos comidas consecutivas")
                        logger.debug("'%s' y '%s'", comida1, comida2)
                        saltar = 1
                    if("Pescado" in dict_cenas[cena1].keys()
                       and "Pescado" in dict_cenas[cena2].keys()):
                        logger.debug("Pescado dos cenas consecutivas")
                        logger.debug("'%s' y '%s'", cena1, cena2)
                        saltar = 1
                    if("Pescado" in dict_cenas[cena1].keys()
                       and "Pescado" in dict_comidas[comida2].keys()):
                        logger.debug("Pescado dos veces consecutivas")
                        logger.debug("'%s' y '%s'", cena1, comida2)
                        saltar = 1
                    if("Pescado" in dict_comidas[comida2].keys()
                       and "Pescado" in dict_cenas[cena2].keys()):
                        logger.debug("Pescado dos veces consecutivas")
                        logger.debug("'%s' y '%s'", comida2, cena2)
                        saltar = 1
                    if("Patata" in dict_comidas[comida1].keys()
                       and "Patata" in dict_comidas[comida2].keys()):
                        logger.debug("Patata dos comidas consecutivas")
                        logger.debug("'%s' y '%s'", comida1, comida2)
                        saltar = 1
                    if("Pasta" in dict_comidas[comida1].keys()
                       and "Pasta" in dict_comidas[comida2].keys()):
                        logger.debug("Pasta dos comidas consecutivas")
                        logger.debug("'%s' y '%s'", comida1, comida2)
                        saltar = 1
                    if("Pavo" in dict_comidas[comida1].keys()
                       and "Pavo" in dict_comidas[comida2].keys()):
                        logger.debug("Pavo dos comidas consecutivas")
                        logger.debug("'%s' y '%s'", comida1, comida2)
                        saltar = 1
                    if("Pollo" in dict_comidas[comida1].keys()
                       and "Pollo" in dict_comidas[comida2].keys()):
                        logger.debug("Pollo dos comidas consecutivas")
                        logger.debug("'%s' y '%s'", comida1, comida2)
                        saltar = 1
                    if comida2 == "Hamburguesa":
                        if (j != 4 and j != 5 and j != 6):
                            logger.debug("Hamburguesa y no es finde")
                            saltar = 1
                if saltar == 0:
                    logger.debug("Iteración OK. Día %s generado", str(j))
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
                else:
                    logger.debug("Iteración no válida. Vuelvo a probar")
                saltar = 0

            logger.debug("Semana generada. Compruebo condiciones")
            # Una vez generada una semana chequeo condiciones
            if (pescado_semana <= 2 and pescado_semana >= 1
               and boniato_semana <= 2 and legumbres_semana <= 2):  # Cuando meta aqui el dato desde settings acordarme de abajo cambiarlo que está a piñón
               # and hamburguesa_semana == 1):
                logger.info("Menu OK")
                logger.debug("Pescado: %d / %d", pescado_semana, 2)
                logger.debug("Boniato: %d / %d", boniato_semana, 2)
                logger.debug("Hamburguesa: %d", hamburguesa_semana)
                logger.debug("Legumbres: %d / %d", legumbres_semana, 2)
                logger.debug("Intentos totales: %d", intentos)
                pescado_semana = 0
                boniato_semana = 0
                hamburguesa_semana = 0
                legumbres_semana = 0
                menu_ok = 1
                intentos = 0
                comidas.extend(comidas_wip)
                cenas.extend(cenas_wip)
            else:
                logger.debug("El menú generado no cumple condiciones")
                logger.debug("Pescado: %d / %d", pescado_semana, 2)
                logger.debug("Boniato: %d / %d", boniato_semana, 2)
                logger.debug("Hamburguesa: %d", hamburguesa_semana)
                logger.debug("Legumbres: %d / %d", legumbres_semana, 2)
                logger.debug("Vuelvo a generarlo")
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

    if menu_consola:  # Si tengo activo en opciones mostrar el menú en consola
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
        print(tabulate(table, headers=["Lunes", "Martes", "Miércoles",
                                       "Jueves", "Viernes", "Sábado",
                                       "Domingo"],
                       tablefmt="fancy_grid"))
        logger.info("Menú escrito en consola")

    if menu_pdf:  # Si tengo activo en opciones crear el PDF con el menú
        doc = SimpleDocTemplate("menu.pdf", pagesize=landscape(A4))
        elements = []

        if semanas == 1:
            data = [separador2, comid, i_com, separador, cen, i_cen]
            t = Table(data, 7*[3.8*cm], [1*cm, 2.6*cm, 4*cm, 0.3*cm,
                                         2.6*cm, 4*cm])
            t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('INNERGRID', (0, 0), (-1, -1),
                                    0.25, colors.black),
                                   ('BOX', (0, 0), (-1, -1), 2,
                                    colors.black)]))
        elif semanas == 2:
            data = [separador2, comid[:7], i_com[:7], separador, cen[:7],
                    i_cen[:7], separador2, comid[7:], i_com[7:], separador,
                    cen[7:], i_cen[7:]]
            t = Table(data, 7*[3.8*cm], [1*cm, 2.6*cm, 4*cm, 0.3*cm, 2.6*cm,
                                         4*cm, 1*cm, 2.6*cm, 4*cm, 0.3*cm,
                                         2.6*cm, 4*cm])
            t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('INNERGRID', (0, 0), (-1, -1),
                                    0.25, colors.black),
                                   ('BOX', (0, 0), (6, 5), 2, colors.black),
                                   ('BOX', (0, 6), (-1, -1), 2,
                                    colors.black)]))

        elements.append(t)
        doc.build(elements)
        logger.info("'menu.pdf' guardado")


    menu_com = comidas
    menu_cen = cenas
    logger.info("Salgo de la función")
    return comidas, cenas, ret


def generate_ingr_list(personas):
    """ Genera la lista de ingredientes del menú generado previamente, para
    el número de personas indicado

    Arguments:
        personas {int} -- Número de personas para calcular las cantidades
    """
    l_ing = []
    l_ing_cant = []
    l_ing_ud = []
    l_ing_num = []
    ret = OK
    menu = menu_com
    diccionario = dict_comidas
    comida = "comidas"

    logger.info("Entro con comensales = '%d'", personas)
    for _ in range(2):
        logger.debug("Procesando %s", comida)
        for item in menu:
            logger.debug("Procesando: %s", item)
            for key, value in diccionario.get(item).items():
                logger.debug("Procesando %s - %s", key, str(value))
                if key not in l_ing:
                    logger.debug("'%s' no está en 'l_ing'. Lo añado", key)
                    l_ing.append(key)
                    if value[0] != "":
                        logger.debug("'%s' no está vacío", value[0])
                        if value[0] in lista_cant:
                            logger.debug("'%s' está en la lista de " +
                                         "cantidades parciales. Añado '%f'",
                                         value[0], personas*float(value[0]))
                            l_ing_cant.append(str(personas*float(value[0])))
                        else:
                            l_ing_cant.append(str(personas*int(value[0])))
                            logger.debug("'%s' no está en la lista de " +
                                         "cantidades parciales. Añado '%d' " +
                                         "a 'l_ing_cant' (Por ser '%d' " +
                                         "personas y la cantidad '%s')",
                                         value[0], personas*int(value[0]),
                                         personas, value[0])
                    else:
                        logger.debug("Valor vacío (%s). Lo añado tal cual" +
                                     " a 'l_ing_cant", value[0])
                        l_ing_cant.append(value[0])
                    l_ing_ud.append(value[1])
                    l_ing_num.append(1)
                    logger.debug("Añado la unidad ('%s') al final de la " +
                                 "lista de unidades", value[1])
                    logger.debug("Añado 1 al final de la lista de " +
                                 "cantidad de apariciones")
                else:
                    logger.debug("'%s' está en 'l_ing'", key)
                    for i in l_ing:
                        if i == key:
                            logger.debug("Encontrado: %s", i)
                            if l_ing_ud[l_ing.index(key)] == value[1]:
                                logger.debug("Las unidades coinciden: '%s' " +
                                             "y '%s'",
                                             l_ing_ud[l_ing.index(key)],
                                             value[1])
                                if l_ing_cant[l_ing.index(key)] != "":
                                    logger.debug("La cantidad no está vacía:" +
                                                 " '%s'",
                                                 l_ing_cant[l_ing.index(key)])
                                    if l_ing_cant[l_ing.
                                                  index(key)] in lista_cant:
                                        logger.debug("Encuentro la cantidad " +
                                                     "en la lista de " +
                                                     "cantidades parciales")
                                        logger.debug("Añado a la cantidad que había en 'l_ing_cant' ('%s') el número de personas (%f) por la cantidad (%f) en float", l_ing_cant[l_ing.index(key)], float(personas), float(value[0]))
                                        l_ing_cant[l_ing.index(key)] = (
                                            float(l_ing_cant
                                                  [l_ing.index(key)]) +
                                            float(personas)*float(value[0]))
                                        l_ing_cant[l_ing.index(key)] = (
                                            str(l_ing_cant
                                                [l_ing.index(key)])
                                        )
                                    else:
                                        logger.debug("No encuentro la " +
                                                     "cantidad en la lista " +
                                                     "de cantidades parciales")
                                        logger.debug("Añado a la cantidad que había en 'l_ing_cant' ('%s') el número de personas (%d) por la cantidad (%d) en int", l_ing_cant[l_ing.index(key)], personas, int(value[0]))
                                        l_ing_cant[l_ing.index(key)] = (
                                            int(l_ing_cant
                                                [l_ing.index(key)]) +
                                            personas*int(value[0]))
                                        l_ing_cant[l_ing.index(key)] = (
                                            str(l_ing_cant
                                                [l_ing.index(key)]))
                                logger.debug("Sumo uno a 'l_ing_num' en la " +
                                             "posición %d", l_ing.index(key))
                                l_ing_num[l_ing.index(key)] += 1
                            else:
                                logger.error("Error en las unidades de medida")
                                logger.error("Revisar %s de la bbdd (%s)",
                                             comida, i)
                                ret = ERROR
                logger.debug("Estado de 'l_ing': %s", str(l_ing))
                logger.debug("Estado de 'l_ing_cant': %s", str(l_ing_cant))
                logger.debug("Estado de 'l_ing_ud': %s", str(l_ing_ud))
                logger.debug("Estado de 'l_ing_num': %s", str(l_ing_num))
        menu = menu_cen
        diccionario = dict_cenas
        comida = "cenas"

    if lista_pdf:  # Si tengo activo en opciones crear el PDF con la lista
        c = canvas.Canvas("lista_ingredientes.pdf")
        y = 0
        x = 100
        string = "LISTA DE INGREDIENTES PARA " + str(personas)
        c.drawString(200, 790, string)
        for item in range(len(l_ing)):
            logger.debug("Lista de ingredientes:")
            logger.debug(str(l_ing_num[item]) + "x -  " + l_ing[item] + ": " +
                         l_ing_cant[item] + " " + l_ing_ud[item])
            c.drawString(x, 750-y, str(l_ing_num[item]) + "x -  " +
                         l_ing[item] + ": " + l_ing_cant[item] + " "
                         + l_ing_ud[item])
            y = y + 15
            if (750 - y) <= 100:
                x = 350
                y = 0
        c.save()
        logger.info("'lista_ingredientes.pdf' guardado")

    if lista_consola:  # Si tengo activo en opciones crear el PDF con la lista
        print("LISTA DE INGREDIENTES PARA " + str(personas))
        for item in range(len(l_ing)):
            logger.debug("Lista de ingredientes:")
            logger.debug(str(l_ing_num[item]) + "x -  " + l_ing[item] + ": " +
                         l_ing_cant[item] + " " + l_ing_ud[item])
            print(str(l_ing_num[item]) + "x -  " + l_ing[item] + ": " +
                  l_ing_cant[item] + " " + l_ing_ud[item])
        logger.info("Lista escrita en consola")

    logger.info("Salgo de la función")
    return ret


def copia_seguridad(fich):
    """[summary]
    """
    logger.debug("Entro con fich = '%s'", fich)
    logger.debug("Procesando copia de seguridad de " + fich)
    logger.debug("Ficheros actuales: %d", len(glob.glob(fich + "*")))
    if len(glob.glob(fich + "*")) >= num_copias:
        # Buscar el más antiguo y eliminarlo
        logger.debug(sorted(glob.glob(fich + "*")))
        logger.debug("Fichero más antiguo: '%s'",
                     sorted(glob.glob(fich + "*"))[1])
        os.remove(sorted(glob.glob(fich + "*"))[1])
        logger.debug("Fichero eliminado")
        shutil.copy(fich, fich + datetime.now().strftime("%Y%m%d%H%M%S"))
        logger.debug("Fichero creado")
    else:
        logger.debug("No hay que eliminar ningún fichero")
        shutil.copy(fich, fich + datetime.now().strftime("%Y%m%d%H%M%S"))
        logger.debug("Fichero creado")
    logger.debug("Salgo de la función")

if __name__ == "__main__":
    num_copias = 0
    # Carga del fichero de configuración del LOG
    setup_logging()
    # Carga inicial de datos (BBDD + Settings)
    if load_data("todo") != OK:
        logger.error("Error cargando datos")
    else:
        logger.info("Todos los datos cargados")
    # Copia de seguridad inicial de Settings y BBDD
    copia_seguridad("settings")
    copia_seguridad("bbdd")

    APP = QtWidgets.QApplication([])
    WINDOW = MainWindow()
    WINDOW.show()
    APP.exec_()
