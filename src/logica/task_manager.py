import hashlib
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

# 1. Definimos la Base del ORM
Base = declarative_base()

# 2. Definimos la Tabla 'Usuario' como una Clase
class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    nombre = Column(String)
    apellido = Column(String)
    fecha_nacimiento = Column(String)
    genero = Column(String)
    
    # Relación: Un usuario tiene muchas tareas
    tareas = relationship("Tarea", back_populates="usuario")

# 3. Definimos la Tabla 'Tarea' como una Clase
class Tarea(Base):
    __tablename__ = 'tareas'
    
    id_task = Column(Integer, primary_key=True) # Usamos id_task para compatibilidad con tu main.py
    titulo = Column(String, nullable=False)
    descripcion = Column(String)
    estado = Column(String, default='pendiente')
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relación inversa
    usuario = relationship("Usuario", back_populates="tareas")

# 4. El Gestor Principal (Logic Layer)
class TaskManager:
    def __init__(self):
        # Configuración de la Base de Datos
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, '..', '..'))
        db_path = os.path.join(project_root, 'tasks.db')
        
        # Conexión con SQLAlchemy (SQLite)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.usuario_actual_id = None

    def inicializar_db(self):
        # Esto crea las tablas automáticamente si no existen
        Base.metadata.create_all(self.engine)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def registrar_usuario(self, email, password, nombre, apellido, nacimiento, genero):
        if not email or not password:
            raise ValueError("El email y la contraseña son obligatorios")
            
        session = self.Session()
        try:
            nuevo_usuario = Usuario(
                email=email,
                password=self._hash_password(password),
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=nacimiento,
                genero=genero
            )
            session.add(nuevo_usuario)
            session.commit()
            return True
        except IntegrityError:
            session.rollback() # Cancelar si hay error (ej: correo duplicado)
            raise ValueError("El correo ya está registrado.")
        finally:
            session.close()

    def login(self, email, password):
        session = self.Session()
        pass_cifrada = self._hash_password(password)
        
        # Buscamos al usuario usando filtros de objetos, no SQL
        usuario = session.query(Usuario).filter_by(email=email, password=pass_cifrada).first()
        
        session.close()
        
        if usuario:
            self.usuario_actual_id = usuario.id
            return self.usuario_actual_id
        else:
            return None

    def listar_tareas(self):
        if self.usuario_actual_id is None:
            return []
            
        session = self.Session()
        # Traemos todas las tareas de este usuario
        tareas = session.query(Tarea).filter_by(usuario_id=self.usuario_actual_id).all()
        session.close()
        return tareas

    def agregar_tarea(self, titulo, descripcion):
        if not self.usuario_actual_id: return
        
        session = self.Session()
        nueva_tarea = Tarea(
            titulo=titulo, 
            descripcion=descripcion, 
            usuario_id=self.usuario_actual_id
        )
        session.add(nueva_tarea)
        session.commit()
        session.close()

    def marcar_completada(self, id_tarea):
        session = self.Session()
        tarea = session.query(Tarea).get(id_tarea)
        if tarea:
            tarea.estado = 'completada' if tarea.estado == 'pendiente' else 'pendiente'
            session.commit()
        session.close()

    def eliminar_tarea(self, id_tarea):
        session = self.Session()
        tarea = session.query(Tarea).get(id_tarea)
        if tarea:
            session.delete(tarea)
            session.commit()
        session.close()