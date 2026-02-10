"""
Lógica principal del negocio.
Controla la interacción entre la base de datos, los usuarios y las tareas.
"""

from src.modelo.modelo import Database
from src.modelo.task import Task
import hashlib


class TaskManager:
    """
    Controlador principal. 
    Maneja la autenticación de usuarios y las operaciones CRUD de tareas.
    """

    def __init__(self):
        self.db = Database()
        # Guardamos la ruta en una variable para poder modificarla en los tests
        self.db_path = self.db.db_path

    def _conectar(self):
        """
        Actualiza la ruta de la BD y establece la conexión.
        Es necesario actualizar self.db.db_path aquí para soportar el cambio de BD en tests.
        """
        self.db.db_path = self.db_path
        return self.db.conectar()

    def inicializar_db(self):
        """Genera las tablas de usuarios y tareas si no existen."""
        self.db.db_path = self.db_path

        conn = self._conectar()
        if conn:
            cursor = conn.cursor()

            # Tabla Tareas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    estado TEXT NOT NULL DEFAULT 'pendiente'
                )
            ''')

            # Tabla Usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    nombre TEXT,
                    apellido TEXT,
                    fecha_nacimiento TEXT,
                    genero TEXT
                )
            ''')
            conn.commit()
            conn.close()

    # ---------------------------------------------------------
    # GESTIÓN DE USUARIOS
    # ---------------------------------------------------------

    def registrar_usuario(self, email, password, nombre, apellido, fecha, genero):
        """
        Registra un nuevo usuario en la base de datos.
        Aplica hash SHA-256 a la contraseña antes de guardar.
        """
        conn = self._conectar()
        if conn:
            cursor = conn.cursor()
            try:
                pass_hash = hashlib.sha256(password.encode()).hexdigest()

                cursor.execute('''
                    INSERT INTO usuarios (email, password, nombre, apellido, fecha_nacimiento, genero)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (email, pass_hash, nombre, apellido, fecha, genero))
                conn.commit()
            except Exception as e:
                conn.close()
                raise ValueError(f"Error al registrar: {e}")
            conn.close()

    def login(self, email, password):
        """
        Verifica las credenciales del usuario.
        Retorna el ID del usuario si el login es correcto, o None si falla.
        """
        conn = self._conectar()
        user_id = None
        if conn:
            cursor = conn.cursor()
            # Hasheamos la entrada para comparar con la BD
            pass_hash = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute(
                'SELECT id FROM usuarios WHERE email = ? AND password = ?', (email, pass_hash))
            resultado = cursor.fetchone()

            if resultado:
                user_id = resultado[0]
            conn.close()
        return user_id

    # ---------------------------------------------------------
    # GESTIÓN DE TAREAS
    # ---------------------------------------------------------

    def agregar_tarea(self, titulo, descripcion):
        """Guarda una nueva tarea con estado 'pendiente'."""
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
        """Recupera todas las tareas y retorna una lista de objetos Task."""
        conn = self._conectar()
        tareas = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT titulo, descripcion, estado, id FROM tasks")
            rows = cursor.fetchall()
            for row in rows:
                nueva_tarea = Task(
                    titulo=row[0], descripcion=row[1], estado=row[2], id_task=row[3])
                tareas.append(nueva_tarea)
            conn.close()
        return tareas

    def eliminar_tarea(self, id_task):
        """Elimina una tarea basada en su ID."""
        conn = self._conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (id_task,))
            if not cursor.fetchone():
                conn.close()
                raise ValueError("La tarea no existe")

            cursor.execute("DELETE FROM tasks WHERE id = ?", (id_task,))
            conn.commit()
            conn.close()
