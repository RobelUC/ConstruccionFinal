"""
Logica de negocio optimizada.
Gestiona Usuarios y Tareas interactuando con SQLAlchemy.
"""
import hashlib
from src.modelo.modelo import Database, Usuario, Tarea


class TaskManager:
    """
    Clase controladora que centraliza las operaciones CRUD y la lógica de autenticación.
    Implementa el patrón de persistencia mediante SQLAlchemy.
    """

    def __init__(self, db_instance=None):
        """
        Constructor con soporte para Inyección de Dependencias.

        Args:
            db_instance: Opcional. Permite pasar una base de datos en memoria para pruebas
                        unitarias, evitando persistencia en el archivo físico real.
        """
        if db_instance:
            self.db = db_instance
        else:
            self.db = Database()
            self.db.inicializar_db()

        # Referencia global a la sesión para evitar múltiples inicializaciones
        self.Session = self.db.Session

    # ---------------------------------------------------------
    # GESTIÓN DE USUARIOS
    # ---------------------------------------------------------

    def registrar_usuario(self, email, password, nombre):
        """
        Registra un nuevo usuario aplicando hashing SHA-256 a la contraseña
        para cumplir con estándares de seguridad básicos.
        """
        session = self.Session()
        try:
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            nuevo = Usuario(email=email, password=pw_hash, nombre=nombre)
            session.add(nuevo)
            session.commit()  # Persistencia en base de datos
            return True
        except Exception:
            session.rollback()  # Revierte cambios en caso de error de integridad (ej: email duplicado)
            return False
        finally:
            session.close()  # Liberación del pool de conexiones

    def login(self, email, password):
        """
        Valida las credenciales del usuario y maneja excepciones personalizadas
        para ser capturadas por la capa de interfaz (GUI/Consola).
        """
        session = self.Session()
        try:
            user = session.query(Usuario).filter_by(email=email).first()

            if not user:
                # Se lanza excepción controlada para informar a la vista
                raise ValueError("El correo no existe.")

            pw_hash = hashlib.sha256(password.encode()).hexdigest()

            if user.password != pw_hash:
                raise ValueError("Contraseña incorrecta.")

            # Retorno de diccionario para desacoplar el modelo ORM de la vista
            return {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email
            }

        except ValueError as e:
            # Re-lanzamiento de la excepción para propagarla hacia el controlador superior
            raise e
        except Exception as e:
            print(f"Error desconocido: {e}")
            raise ValueError("Error de conexión con la base de datos.")
        finally:
            session.close()

    # ---------------------------------------------------------
    # GESTIÓN DE TAREAS (CRUD)
    # ---------------------------------------------------------

    def listar_tareas_usuario(self, user_id):
        """
        Recupera las tareas de un usuario específico. 
        Aplica validaciones de nulidad en campos opcionales para evitar errores en la interfaz.
        """
        session = self.Session()
        try:
            # Uso de Lazy Loading mediante la consulta filtrada
            tareas = session.query(Tarea).filter_by(user_id=user_id).all()
            return [
                {
                    "id": t.id,
                    "titulo": t.titulo,
                    "descripcion": t.descripcion if t.descripcion else "",
                    "fecha": t.fecha if t.fecha else "Sin fecha",
                    "prioridad": t.prioridad,
                    "estado": t.estado
                }
                for t in tareas
            ]
        finally:
            session.close()

    def agregar_tarea_usuario(self, user_id, titulo, descripcion, fecha=None, prioridad="Media"):
        """ Crea y persiste una nueva tarea vinculada al ID del usuario logueado. """
        session = self.Session()
        try:
            nueva = Tarea(
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                prioridad=prioridad,
                estado="pendiente",
                user_id=user_id
            )
            session.add(nueva)
            session.commit()
            return True
        except Exception as e:
            print(f"Error al guardar tarea: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def editar_tarea(self, id_task, titulo, descripcion, fecha, prioridad):
        """ Actualiza los campos de una tarea existente buscando por su Clave Primaria (ID). """
        session = self.Session()
        try:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                tarea.titulo = titulo
                tarea.descripcion = descripcion
                tarea.fecha = fecha
                tarea.prioridad = prioridad
                session.commit()
        finally:
            session.close()

    def eliminar_tarea(self, id_task):
        """ Elimina un registro físico de la base de datos mediante su ID. """
        session = self.Session()
        try:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                session.delete(tarea)
                session.commit()
        finally:
            session.close()

    def marcar_completada(self, id_task):
        """
        Implementa una lógica de 'Toggle' (Alternancia).
        Cambia el estado entre 'pendiente' y 'completada' según el valor actual.
        """
        session = self.Session()
        try:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                tarea.estado = "completada" if tarea.estado == "pendiente" else "pendiente"
                session.commit()
        finally:
            session.close()

    def buscar_tareas(self, user_id, texto):
        """
        Realiza una búsqueda filtrada utilizando el operador LIKE de SQL
        para coincidencias parciales en el título de la tarea.
        """
        session = self.Session()
        try:
            tareas = session.query(Tarea).filter(
                Tarea.user_id == user_id,
                Tarea.titulo.like(f"%{texto}%")
            ).all()
            return [
                {
                    "id": t.id,
                    "titulo": t.titulo,
                    "descripcion": t.descripcion if t.descripcion else "",
                    "fecha": t.fecha,
                    "prioridad": t.prioridad,
                    "estado": t.estado
                }
                for t in tareas
            ]
        finally:
            session.close()

    def filtrar_tareas_usuario(self, user_id, estado=None):
        """
        Implementa filtrado dinámico en el servidor. 
        Si se provee un estado, se añade la cláusula filter_by al objeto query.
        """
        session = self.Session()
        try:
            # Construcción dinámica de la consulta
            query = session.query(Tarea).filter_by(user_id=user_id)

            if estado:
                query = query.filter_by(estado=estado)

            tareas = query.all()

            return [
                {
                    "id": t.id,
                    "titulo": t.titulo,
                    "descripcion": t.descripcion or "",
                    "fecha": t.fecha or "Sin fecha",
                    "prioridad": t.prioridad,
                    "estado": t.estado
                }
                for t in tareas
            ]
        finally:
            session.close()
