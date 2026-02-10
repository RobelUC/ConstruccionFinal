"""
Definición de modelos de datos para el sistema.
"""


class Task:
    """
    Representa una tarea individual. Se usa como contenedor para mover 
    información entre la base de datos, la lógica y la interfaz.
    """

    def __init__(self, titulo, descripcion, estado='pendiente', id_task=None):
        """
        Constructor de la tarea. id_task se mantiene como None si la tarea 
        no ha sido guardada todavía en la base de datos.
        """
        self.id_task = id_task
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = estado

    def __str__(self):
        """
        Representación legible de la tarea, útil para depuración y logs.
        """
        return f"[{self.estado}] {self.titulo}: {self.descripcion}"

    def to_dict(self):
        """
        Serializa el objeto a un diccionario. Útil para facilitar 
        las pruebas unitarias y el manejo de datos en la interfaz.
        """
        return {
            "id": self.id_task,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "estado": self.estado
        }
