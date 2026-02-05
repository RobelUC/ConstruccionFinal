# Proyecto Gestor de Tareas

## Descripción General

Este proyecto consiste en el desarrollo de una aplicación de gestión de tareas desarrollada en Python como parte del curso de Construcción de Software. La aplicación permite a los usuarios organizar sus tareas diarias de manera eficiente, garantizando la persistencia de los datos mediante una base de datos SQLite.

## Objetivo de la Aplicación

El objetivo principal es ofrecer una herramienta intuitiva y funcional para la gestión de tareas, que permita:

- Añadir nuevas tareas.
- Editar tareas existentes.
- Eliminar tareas.
- Marcar tareas como completadas.
- Almacenar toda la información de manera persistente en una base de datos SQLite.

Adicionalmente, el proyecto tiene como propósito aplicar buenas prácticas de ingeniería de software, incluyendo desarrollo guiado por pruebas (TDD), uso de control de versiones con Git/GitHub, y trabajo colaborativo basado en ramas funcionales.

## Integrantes del Equipo

- [Nombre y apellido del integrante 1]
- [Nombre y apellido del integrante 2]
- [Nombre y apellido del integrante 3]
- [Nombre y apellido del integrante 4]

## Instrucciones para la Ejecución del Proyecto

### Requisitos Previos

- Python 3.8 o superior instalado.
- Git instalado (para clonar el repositorio).
- Conexión a internet (solo para clonar).

### Pasos para Ejecutar

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/RobelUC/ConstruccionFinal.git
   cd ConstruccionFinal
   ```

2. **Instalar dependencias (si existen):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python src/main.py
   ```

4. **Ejecutar las pruebas:**
   ```bash
   python -m pytest tests/
   ```

### Estructura del Proyecto

```
.
├── README.md
├── .gitignore
├── requirements.txt (si aplica)
├── src/
│   ├── main.py
│   ├── modules/
│   └── database/
│       └── DB.sqlite
├── tests/
│   ├── unit/
│   ├── integration/
│   └── system/
└── docs/ (opcional)
```

### Notas Importantes

- La base de datos se crea automáticamente en `src/database/DB.sqlite` al ejecutar la aplicación por primera vez.
- Asegúrate de tener permisos de escritura en el directorio del proyecto.
- El proyecto sigue un enfoque TDD, por lo que todas las funcionalidades están respaldadas por pruebas automatizadas.

---


Este proyecto ha sido desarrollado como parte de la asignatura **Construcción de Software**, siguiendo las buenas prácticas de desarrollo colaborativo, control de versiones y pruebas automatizadas.
```
