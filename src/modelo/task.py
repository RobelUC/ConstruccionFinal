class Task:
    def __init__(self, titulo, descripcion, estado='pendiente', id_task=None):
        self.id_task = id_task
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = estado

    def __str__(self):
        return f"[{self.estado}] {self.titulo}: {self.descripcion}"

    def to_dict(self):
        """Convierte la tarea a un diccionario (útil para pruebas o interfaces)."""
        return {
            "id": self.id_task,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "estado": self.estado
        }