# MenuPlanner

Ver 1.0.0 - XX/01/19
- Funcionamiento básico en modo consola.

Ver 1.5.0 - XX/03/19
- Funcionamiento básico en modo gráfico con tkinter.
- Generación de menú y lista de ingredientes en PDF.

Ver 2.0.0 - XX/10/19
- Funcionamiento básico en modo gráfico con pyqt5.

Ver 2.0.1 - 21/10/19
- Añadido mensaje de confirmación al añadir ingrediente.
- Añadido mensaje de confirmación al añadir receta.
- Al añadir una comida nueva recargo la base de datos para que aparezca.
- Añadido chequeo a la base de datos para comprobar que tenga tantos caracteres
    ':' como debe.
- Eliminado 'MenuPlanner' de los títulos de las ventanas.

Ver 2.0.2 - 31/10/19
- Implementado LOG en lugar de prints, utilizando el módulo logging con
    rotación diaria.
- Añadida comprobación de que exista menú a la hora de generar listado de
    ingredientes, avisando al usuario si no es así.
- Añadida ventana de ajustes. Se pueden ver y modificar los ajustes, aunque
    por ahora no las restricciones de menú.
- Añadidos links a los ficheros PDF desde los mensajes de menú y lista de
    ingredientes generados correctamente.
- Se ha añadido un parámetro en la carga de datos para evitar que se cargue
    siempre todo. Ahora se puede cargar BBDD, Ajustes o Todo. Esto mejorará
    tiempos de ejecución y optimizará el programa y el Log.
- Añadido a ajustes la posibilidad de elegir si se quieren generar PDF, así
    como si se quiere imprimir por consola. Ambas opciones están disponibles
    para Menú y Lista de Ingredientes. Añadidas también las listas de
    cantidades y unidades de medida para mejorar la gestión.
- Ahora se muestran las recetas buscadas en el programa, antes sólo se podían
    ver en consola.
- Añadida gestión de copias de seguridad de base de datos y ajustes.
- Corregido un bug a la hora de añadir recetas. Al pulsar CANCEL se añadían
    igualmente.

Ver 2.0.3 - 18/11/19
- A la hora de generar menú en Windows aparecían caracteres extraños. Esto es
    por el encoding de los ficheros, que es distinto en Linux (donde se han
    creado) que en Windows. Ahora al abrir un fichero se fuerza el encoding a
    "utf-8", con lo que el problema debería quedar resuelto.
- Añadida comprobación al crear recetas de si el ingrediente, cantidad o unidad
    de medida que se ha escrito a mano ya existía previamente en la lista.
- Añadida barra superior de menú con la opción 'Acerca de', la cual abre una
    ventana nueva con los datos de la aplicación.
- Pequeña modificación para gestionar mejor los ingredientes con cantidades
    parciales, como los aguacates y su 0'5.