from src.modelo.task import Task
from src.modelo.modelo import Database

class TaskManager:
    def __init__(self):
        self.db = Database()
        # Permitimos cambiar la ruta para tests
        self.db_path = self.db.db_path 

    def _conectar(self):
        # Actualizamos la ruta de la BD por si fue cambiada por el test
        self.db.db_path = self.db_path
        return self.db.conectar()

    def inicializar_db(self):
        self.db.db_path = self.db_path
        self.db.inicializar_db()

    def agregar_tarea(self, titulo, descripcion):
        if not titulo:
            raise ValueError("El título no puede estar vacío")
        
        conn = self._conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (titulo, descripcion, estado) VALUES (?, ?, ?)", 
                           (titulo, descripcion, 'pendiente'))
            conn.commit()
            conn.close()

    def listar_tareas(self):
        conn = self._conectar()
        tareas = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT titulo, descripcion, estado, id FROM tasks")
            rows = cursor.fetchall()
            for row in rows:
                # Reconstruimos el objeto Task desde la BD
                nueva_tarea = Task(titulo=row[0], descripcion=row[1], estado=row[2], id_task=row[3])
                tareas.append(nueva_tarea)
            conn.close()
        return tareas

    def eliminar_tarea(self, id_task):
        conn = self._conectar()
        if conn:
            cursor = conn.cursor()
            # Verificamos si existe primero
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (id_task,))
            if not cursor.fetchone():
                conn.close()
                raise ValueError("La tarea no existe")
            
            cursor.execute("DELETE FROM tasks WHERE id = ?", (id_task,))
            conn.commit()
            conn.close()