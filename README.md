# Sistema de Carrito de Compras

Proyecto de desarrollo de un sistema de carrito de compras, compuesto por una API REST desarrollada con Flask y PostgreSQL, y una interfaz gráfica desarrollada con Streamlit.

El sistema permite gestionar usuarios, productos, stock y carritos de compras, utilizando una base de datos relacional para almacenar y administrar la información.

## Funcionalidades principales

- Registro, modificación y eliminación de usuarios.
- Inicio y cierre de sesión.
- Almacenamiento seguro de contraseñas mediante hashing.
- Gestión de productos, categorías, precios y stock.
- Creación, consulta, finalización y cancelación de carritos.
- Incorporación y eliminación de productos del carrito.
- Aumento y disminución de cantidades.
- Cálculo automático del importe total del carrito.
- Validación de disponibilidad de productos y stock.
- Manejo de transacciones y restricciones de integridad en la base de datos.
- Comunicación entre frontend y backend mediante una API REST.

## Tecnologías utilizadas

| Tecnología | Finalidad |
|---|---|
| Python | Lenguaje de programación |
| Flask | Desarrollo de la API REST |
| PostgreSQL | Base de datos relacional |
| psycopg2 | Conexión entre Python y PostgreSQL |
| python-dotenv | Gestión de variables de entorno |
| Werkzeug | Hashing y verificación de contraseñas |
| Streamlit | Interfaz gráfica |
| Requests | Comunicación HTTP |
| Postman | Pruebas de endpoints |
| Git y GitHub | Control de versiones |

## Estructura del proyecto

```text
Sistema-de-Carrito-de-Compras/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── src/
│       ├── controllers/
│       │   ├── controller_carrito.py
│       │   ├── controller_item_carrito.py
│       │   ├── controller_productos.py
│       │   └── controller_usuarios.py
│       ├── database/
│       │   ├── carrito.sql
│       │   ├── database.py
│       │   ├── migracion_001.sql
│       │   ├── migracion_002.sql
│       │   ├── migracion_003.sql
│       │   └── migrar_contrasenias.py
│       └── models/
│           ├── model_carrito.py
│           ├── model_item_carrito.py
│           └── model_usuarios.py
│
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── carritos.py
│   │   ├── home.py
│   │   ├── productos.py
│   │   └── usuarios.py
│   └── services/
│       └── api.py
│
├── .env.example
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.9 o superior.
- pip.
- PostgreSQL.
- Git.

Herramientas recomendadas:

- Visual Studio Code.
- pgAdmin 4.
- Postman.

## Instalación y configuración

### 1. Clonar el repositorio

```powershell
git clone https://github.com/LongoIvan/Sistema-de-Carrito-de-Compras.git
cd Sistema-de-Carrito-de-Compras
git switch dev
```

### 2. Crear y activar un entorno virtual

Desde la raíz del repositorio:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias del backend

```powershell
python -m pip install -r backend/requirements.txt
```

### 4. Configurar las variables de entorno

Crear el archivo `.env` a partir del archivo de ejemplo, únicamente si todavía no existe:

```powershell
Copy-Item .env.example .env
```

Configurar las siguientes variables:

```env
DATABASE_URL=postgresql://postgres:TU_CONTRASENA@localhost:5432/carrito
SECRET_KEY=TU_CLAVE_SECRETA
```

La variable `DATABASE_URL` contiene los datos necesarios para establecer la conexión con PostgreSQL.

- `postgres`: usuario de PostgreSQL.
- `TU_CONTRASENA`: contraseña del usuario de PostgreSQL.
- `localhost`: servidor local.
- `5432`: puerto predeterminado de PostgreSQL.
- `carrito`: nombre de la base de datos.

El nombre de la base de datos puede modificarse según la configuración local.

La variable `SECRET_KEY` se utiliza para firmar las cookies de sesión de Flask. Para generar una clave aleatoria, ejecutar:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copiar el resultado en la variable `SECRET_KEY`.

El archivo `.env` contiene información privada y no debe compartirse ni subirse al repositorio.

## Configuración de la base de datos

### Instalación desde cero mediante pgAdmin 4

1. Abrir pgAdmin 4 y conectarse al servidor PostgreSQL.
2. Hacer clic derecho sobre **Databases**.
3. Seleccionar **Create > Database**.
4. Crear una base de datos denominada `carrito`.
5. Abrir **Query Tool** sobre la base de datos creada.
6. Abrir el siguiente archivo SQL:

```text
backend/src/database/carrito.sql
```

7. Ejecutar el script completo.
8. Aplicar las migraciones en el orden indicado a continuación.
9. Ejecutar el script de migración de contraseñas.

Si se utiliza otro nombre para la base de datos, deberá coincidir con el configurado en `DATABASE_URL`.

### Migraciones de la base de datos

Las migraciones permiten actualizar la estructura original de la base de datos sin necesidad de eliminarla y volver a crearla.

Antes de aplicar las migraciones sobre una base de datos existente, se recomienda realizar una copia de seguridad y verificar cuáles ya fueron ejecutadas.

Ejecutar los siguientes archivos mediante Query Tool, respetando su orden:

| Orden | Archivo | Finalidad |
|---|---|---|
| 1 | `migracion_001.sql` | Modificar la restricción de eliminación de usuarios con carritos asociados. |
| 2 | `migracion_002.sql` | Incorporar restricciones de integridad sobre precios, stock, cantidades y productos duplicados dentro de un carrito. |
| 3 | `migracion_003.sql` | Eliminar las tablas obsoletas de la estructura anterior. |

Todos los archivos se encuentran en:

```text
backend/src/database/
```

**Importante:** las migraciones SQL no deben ejecutarse nuevamente si ya fueron aplicadas.

Antes de ejecutar `migracion_003.sql`, verificar que las tablas obsoletas estén vacías y que no existan dependencias ni funcionalidades que las utilicen.

### Migración de contraseñas

El archivo SQL original contiene contraseñas de prueba almacenadas en texto plano.

Para convertirlas en contraseñas hasheadas, ejecutar desde la raíz del repositorio:

```powershell
python -m backend.src.database.migrar_contrasenias
```

Este procedimiento:

- Convierte las contraseñas existentes en hashes.
- Conserva las contraseñas originales como credenciales de acceso.
- Omite las contraseñas que ya reconoce como hasheadas.
- Utiliza la conexión configurada en el archivo `.env`.

No es necesario iniciar el servidor Flask para ejecutar este procedimiento, pero PostgreSQL debe estar funcionando.

### Verificación de la base de datos

Para comprobar las tablas existentes, ejecutar:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

Una vez aplicadas las migraciones, las tablas utilizadas por el sistema son:

- `usuario`
- `producto`
- `carrito`
- `item_carrito`

Para consultar los usuarios sin exponer sus contraseñas:

```sql
SELECT idusuario, nombre, mail, rol
FROM usuario;
```

## Ejecución del backend

Desde la raíz del repositorio, ejecutar:

```powershell
python -m flask --app backend.app run --debug
```

El servidor estará disponible en:

```text
http://127.0.0.1:5000
```

Para detener el servidor, presionar `Ctrl + C`.

El modo debug está destinado exclusivamente al desarrollo local.

## Levantar frontend
      pip install streamlit requests  
      streamlit run frontend/app.py   

## Endpoints disponibles

La API cuenta con 39 endpoints distribuidos entre cuatro controladores.

Las respuestas se devuelven en formato JSON y pueden contener objetos, listas, mensajes de confirmación o mensajes de error, según la operación realizada.

### Usuarios

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/usuario` | Registrar usuario |
| GET | `/api/usuario/<id>` | Consultar identificador |
| GET | `/api/usuario/<id>/nombre` | Consultar nombre |
| GET | `/api/usuario/<id>/mail` | Consultar correo electrónico |
| GET | `/api/usuario/<id>/rol` | Consultar rol |
| GET | `/api/usuario/<id>/completo` | Consultar datos del usuario |
| PATCH | `/api/usuario/<id>/nombre` | Modificar nombre |
| PATCH | `/api/usuario/<id>/mail` | Modificar correo electrónico |
| PATCH | `/api/usuario/<id>/contrasenia` | Modificar contraseña |
| DELETE | `/api/usuario/<id>` | Eliminar usuario |
| POST | `/api/usuario/login` | Iniciar sesión |
| GET | `/api/usuario/sesion` | Consultar sesión activa |
| POST | `/api/usuario/logout` | Cerrar sesión |

### Productos

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/productos` | Listar productos |
| POST | `/api/productos` | Agregar producto |
| GET | `/api/productos/<id>/nombre` | Consultar nombre |
| GET | `/api/productos/<id>/precio` | Consultar precio |
| GET | `/api/productos/<id>/stock` | Consultar stock |
| GET | `/api/productos/<id>/categoria` | Consultar categoría |
| GET | `/api/productos/<id>/fecha` | Consultar fecha |
| GET | `/api/productos/<id>/descripcion` | Consultar descripción |
| PATCH | `/api/productos/<id>/nombre` | Modificar nombre |
| PATCH | `/api/productos/<id>/precio` | Modificar precio |
| PATCH | `/api/productos/<id>/stock` | Modificar stock |
| PATCH | `/api/productos/<id>/categoria` | Modificar categoría |
| PATCH | `/api/productos/<id>/descripcion` | Modificar descripción |
| PATCH | `/api/productos/<id>/stock/agregar` | Aumentar stock |
| PATCH | `/api/productos/<id>/stock/quitar` | Disminuir stock |
| DELETE | `/api/productos/<id>` | Eliminar producto |

### Carritos

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/carritos` | Crear carrito |
| GET | `/api/carritos/<id>` | Consultar carrito |
| GET | `/api/carritos/<id>/total` | Calcular importe total |
| GET | `/api/carritos/<id>/items` | Consultar productos del carrito |
| PATCH | `/api/carritos/<id>/finalizar` | Finalizar carrito |
| PATCH | `/api/carritos/<id>/cancelar` | Cancelar carrito |

### Items del carrito

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/carritos/<idcarrito>/items` | Agregar producto al carrito |
| PATCH | `/api/carritos/<idcarrito>/items/<iditem>/aumentar` | Aumentar cantidad |
| PATCH | `/api/carritos/<idcarrito>/items/<iditem>/disminuir` | Disminuir cantidad |
| DELETE | `/api/carritos/<idcarrito>/items/<iditem>` | Eliminar item |

Los parámetros `<id>`, `<idcarrito>` e `<iditem>` deben reemplazarse por sus respectivos identificadores numéricos.

Para consultar las rutas registradas en Flask:

```powershell
python -m flask --app backend.app routes
```

## Ejemplos de solicitudes HTTP

Las solicitudes que requieren un cuerpo JSON deben enviarse utilizando el encabezado:

```text
Content-Type: application/json
```

### Registrar usuario

**POST** `/api/usuario`

```json
{
    "nombre": "Usuario Prueba",
    "mail": "usuario@gmail.com",
    "contrasenia": "Prueba123"
}
```

### Iniciar sesión

**POST** `/api/usuario/login`

```json
{
    "mail": "usuario@gmail.com",
    "contrasenia": "Prueba123"
}
```

Las solicitudes relacionadas con una sesión deben conservar la cookie recibida durante el inicio de sesión.

### Agregar producto

**POST** `/api/productos`

```json
{
    "nombre": "Cafe en grano",
    "precio": 15000,
    "stock": 20,
    "categoria": "Comida",
    "descripcion": "Cafe en grano de 500 gramos"
}
```

### Crear carrito

**POST** `/api/carritos`

```json
{
    "idusuario": 1
}
```

### Agregar producto al carrito

**POST** `/api/carritos/1/items`

```json
{
    "idproducto": 3,
    "cantidad": 2
}
```

Los identificadores utilizados en los ejemplos son ilustrativos y deben corresponder a registros existentes. El carrito debe encontrarse pendiente y el producto debe estar activo y disponer de stock suficiente.

## Códigos de respuesta HTTP

| Código | Significado |
|---|---|
| 200 OK | Operación realizada correctamente |
| 201 Created | Registro creado correctamente |
| 400 Bad Request | Datos inválidos o incumplimiento de una validación |
| 401 Unauthorized | Credenciales incorrectas o ausencia de sesión activa |
| 404 Not Found | Recurso no encontrado |
| 409 Conflict | Conflicto con el estado o la integridad de los datos |
| 500 Internal Server Error | Error interno del servidor |

## Funcionamiento del carrito

Un carrito puede encontrarse en tres estados:

| Estado | Descripción |
|---|---|
| Pendiente | Permite incorporar, modificar y eliminar productos. |
| Finalizado | La compra fue confirmada y se descontó el stock correspondiente. |
| Cancelado | El carrito fue cancelado y no puede continuar modificándose. |

Durante la gestión de un carrito:

- Se verifica que los productos estén activos.
- Se comprueba que exista stock suficiente.
- Si se agrega un producto que ya está en el carrito, se incrementa su cantidad.
- Se conserva el precio unitario registrado al incorporar el producto.
- El importe total se calcula multiplicando la cantidad por el precio unitario de cada item.
- El stock se descuenta al finalizar correctamente la compra.
- Si cambia la disponibilidad de los productos antes de finalizar, el carrito puede corregirse y permanecer pendiente para una nueva confirmación.

## Seguridad e integridad de los datos

El backend incorpora los siguientes mecanismos:

- Hashing de contraseñas mediante Werkzeug.
- Verificación de credenciales durante el inicio de sesión.
- Gestión de sesiones mediante cookies de Flask.
- Cookies configuradas con `HttpOnly` y `SameSite=Lax`.
- Consultas SQL parametrizadas.
- Validación de los datos recibidos.
- Restricciones de unicidad y claves foráneas.
- Restricciones CHECK para precios, stock y cantidades.
- Manejo de transacciones mediante commit y rollback.
- Bloqueos de registros mediante `SELECT FOR UPDATE` en operaciones críticas.
- Prevención de eliminación de usuarios y productos asociados a carritos.
- Exclusión de credenciales y archivos temporales mediante `.gitignore`.

### Consideraciones de seguridad

El proyecto se encuentra en etapa de desarrollo.

La autenticación mediante sesiones está implementada, pero todavía no se exige una sesión activa ni se verifica la autorización del usuario en todos los endpoints.

La configuración actual permite cookies de sesión mediante HTTP para facilitar las pruebas locales. Para un entorno de producción deberá utilizarse HTTPS y habilitarse `SESSION_COOKIE_SECURE`.

El archivo SQL original contiene credenciales de prueba y no debe utilizarse con información real o sensible.

## Pruebas realizadas

Se realizaron pruebas manuales mediante Postman y verificaciones de los registros y restricciones mediante pgAdmin 4.

Entre los escenarios comprobados se encuentran:

- Registro y eliminación de usuarios.
- Validación de nombres, correos electrónicos y contraseñas.
- Prevención de correos electrónicos duplicados.
- Inicio y cierre de sesión.
- Modificación de contraseñas y rechazo de credenciales anteriores.
- Consulta y modificación de productos.
- Validación de precios y stock.
- Descuento concurrente de stock.
- Creación y consulta de carritos.
- Cálculo del importe total.
- Incorporación y eliminación de items.
- Aumento y disminución de cantidades.
- Conservación del precio unitario dentro del carrito.
- Finalización y cancelación de carritos.
- Manejo de productos sin stock o inactivos.
- Prevención de modificaciones sobre carritos finalizados o cancelados.
- Manejo de restricciones de integridad referencial.

Estas verificaciones corresponden a pruebas manuales de desarrollo y no constituyen una suite automatizada exhaustiva.

## Control de versiones

El proyecto utiliza Git y GitHub para gestionar los cambios realizados durante el desarrollo colaborativo.

La rama de desarrollo es `dev`.

Para actualizar el repositorio local:

```powershell
git switch dev
git pull origin dev
```

## Estado del proyecto

Proyecto académico en desarrollo, orientado a la aplicación de conocimientos de programación en Python, bases de datos relacionales, desarrollo de API REST y trabajo colaborativo.