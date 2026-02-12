"""
Logica de negocio optimizada.
Gestiona Usuarios y Tareas interactuando con SQLAlchemy.
"""
import hashlib
from src.modelo.modelo import Database, Usuario, Tarea

class TaskManager:
    def __init__(self):
        self.db = Database()
        self.db.inicializar_db()
        self.Session = self.db.Session

    # ---------------------------------------------------------
    # GESTIÓN DE USUARIOS
    # ---------------------------------------------------------
    def registrar_usuario(self, email, password, nombre):
        session = self.Session()
        try:
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            nuevo = Usuario(email=email, password=pw_hash, nombre=nombre)
            session.add(nuevo)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    # En src/logica/task_manager.py
    
    def login(self, email, password):
        session = self.Session()
        try:
            # Tu lógica de buscar usuario...
            user = session.query(Usuario).filter_by(email=email).first()

            if not user:
                # 🛑 IMPORTANTE: 'raise' envía el error a la pantalla
                raise ValueError("El correo no existe.")

            # Tu lógica de hash...
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if user.password != pw_hash:
                # 🛑 IMPORTANTE: 'raise' envía el error a la pantalla
                raise ValueError("Contraseña incorrecta.")

            return {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email
            }

        except ValueError as e:
            # 🛑 ESTO ES LO QUE TE FALTA:
            # Si capturas el error, tienes que volver a lanzarlo (raise)
            # para que main.py se entere.
            raise e 
            
        except Exception as e:
            print(f"Error desconocido: {e}")
            # Aquí también lanzamos un error genérico para que salga en pantalla
            raise ValueError("Error de conexión con la base de datos.")
            
        finally:
            session.close()
    # ---------------------------------------------------------
    # GESTIÓN DE TAREAS (CRUD)
    # ---------------------------------------------------------
    def listar_tareas_usuario(self, user_id):
        """Recupera tareas y las formatea como diccionarios seguros para la interfaz."""
        session = self.Session()
        try:
            tareas = session.query(Tarea).filter_by(user_id=user_id).all()
            return [
                {
                    "id": t.id,
                    "titulo": t.titulo,
                    # Solución al problema de descripción: asegura que nunca sea None
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
        session = self.Session()
        try:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                session.delete(tarea)
                session.commit()
        finally:
            session.close()

    def marcar_completada(self, id_task):
        session = self.Session()
        try:
            tarea = session.query(Tarea).filter_by(id=id_task).first()
            if tarea:
                # Alterna entre pendiente y completada
                tarea.estado = "completada" if tarea.estado == "pendiente" else "pendiente"
                session.commit()
        finally:
            session.close()

    def buscar_tareas(self, user_id, texto):
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