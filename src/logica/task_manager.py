from src.modelo.task import Task
from src.modelo.modelo import Database

class TaskManager:
    def __init__(self):
        self.db = Database()
        # Esta variable permite cambiar la ruta de la BD para los tests
        self.db_path = self.db.db_path 

    def _conectar(self):
        """Método interno para conectar. Actualiza la ruta por si los tests la cambiaron."""
        self.db.db_path = self.db_path
        return self.db.conectar()

    def inicializar_db(self):
        """Se asegura de crear la tabla si no existe."""
        self.db.db_path = self.db_path
        self.db.inicializar_db()

    def agregar_tarea(self, titulo, descripcion):
        """Agrega una tarea validando que el título no esté vacío."""
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
        """Recupera todas las tareas y las convierte en objetos Task."""
        conn = self._conectar()
        tareas = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT titulo, descripcion, estado, id FROM tasks")
            rows = cursor.fetchall()
            for row in rows:
                # row[0]=titulo, row[1]=descripcion, row[2]=estado, row[3]=id
                nueva_tarea = Task(titulo=row[0], descripcion=row[1], estado=row[2], id_task=row[3])
                tareas.append(nueva_tarea)
            conn.close()
        return tareas

    def eliminar_tarea(self, id_task):
        """Elimina una tarea por ID. Lanza error si no existe."""
        conn = self._conectar()
        if conn:
            cursor = conn.cursor()
            # 1. Verificamos si existe antes de borrar
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (id_task,))
            if not cursor.fetchone():
                conn.close()
                raise ValueError("La tarea no existe")
            
            # 2. Procedemos a borrar
            cursor.execute("DELETE FROM tasks WHERE id = ?", (id_task,))
            conn.commit()
            conn.close()

    def marcar_completada(self, id_task):
        """Cambia el estado de una tarea a 'completada'."""
        conn = self._conectar()
        if conn:
            cursor = conn.cursor()
            # 1. Verificar existencia
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (id_task,))
            if not cursor.fetchone():
                conn.close()
                raise ValueError("La tarea no existe")
            
            # 2. Actualizar estado
            cursor.execute("UPDATE tasks SET estado = 'completada' WHERE id = ?", (id_task,))
            conn.commit()
            conn.close()

    def editar_tarea(self, id_task, nuevo_titulo, nueva_descripcion):
        """Edita título y descripción. Valida existencia y datos vacíos."""
        if not nuevo_titulo:
            raise ValueError("El título no puede estar vacío")
            
        conn = self._conectar()
        if conn:
            cursor = conn.cursor()
            # 1. Verificar existencia
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (id_task,))
            if not cursor.fetchone():
                conn.close()
                raise ValueError("La tarea no existe")
            
            # 2. Actualizar datos
            cursor.execute("UPDATE tasks SET titulo = ?, descripcion = ? WHERE id = ?", 
                           (nuevo_titulo, nueva_descripcion, id_task))
            conn.commit()
            conn.close()