Sistema de Carrito de Compras
   API backend desarrollada con Flask y PostgreSQL.

## Requisitos

- Python 3.9 o superior
- pip

## Ejecución local en Windows (PowerShell)

Desde la raíz del repositorio:

1. Crea y activa un entorno virtual:

   ```powershell
               py -m venv .venv
               .\.venv\Scripts\Activate.ps1
   ```

2. Instala las dependencias:

   ```powershell
            pip install -r backend\requirements.txt
   ```

3. Crea tu archivo local de variables de entorno a partir del ejemplo:

   ```powershell
            Copy-Item .env.example .env
   ```

   Crear el archivo .env y agregar: 
      DATABASE_URL=postgresql://postgres:usuario@localhost:5432/carrito


4. Inicia el servidor de desarrollo:

   ```powershell
            flask --app backend.app run --debug
   ```

## Endpoints disponibles

Todos los endpoints devuelven una lista JSON; si aún no hay registros, la
respuesta es `[]`.

| Método | Ruta                  | Entidad          |
| ---    | ---                   | ---              |
| GET    | `/api/usuarios`       | Usuarios         |
| GET    | `/api/productos`      | Productos        |
| GET    | `/api/carritos`       | Carritos         |
| GET    | `/api/items-carrito`  | Items de carrito |

## Pasos para importar la base de datos en pgAdmin 4

1. **Crear la base de datos**
   1. Abre pgAdmin 4 y conéctate al servidor PostgreSQL.
   2. Haz clic derecho en **Databases** y selecciona **Create > Database...**.
   3. Escribe `carrito` en el campo **Database** y haz clic en **Save**.

2. **Ejecutar el script SQL**
   1. Expande la base de datos `carrito` y abre **Schemas > public > Tables**.
   2. Haz clic derecho en **Tables** y selecciona **Query Tool**.
   3. En **Query Tool**, selecciona **Open File** y abre `carrito_backup.sql` desde el repositorio.
   4. Haz clic en **Execute** (ícono de Play)

3. **Verificar la importación**
   1. Abre **Query Tool** sobre la base de datos `carrito`.
   2. Ejecuta una consulta para comprobar que se importaron los registros:

      ```sql
      SELECT * FROM usuario;
      ```