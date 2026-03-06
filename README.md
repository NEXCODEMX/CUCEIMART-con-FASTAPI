# CUCEI MART

Plataforma de e-commerce universitario para la comunidad del Centro Universitario de Ciencias Exactas e Ingenierías (CUCEI). Desarrollada por **Nexcode**. 
Ragknos Demian
---

## Descripcion del dominio

CUCEI MART conecta estudiantes y emprendedores dentro del campus universitario. Los estudiantes pueden descubrir y comprar productos de sus compañeros, mientras que los emprendedores pueden publicar sus productos y gestionar su tienda personal. La plataforma incluye sistema de calificaciones con estrellas, comentarios, buscador con filtros avanzados y un ranking de emprendedores destacados al estilo MercadoLibre.

**Roles del sistema:**
- `student` — puede buscar, comprar y dejar reseñas
- `entrepreneur` — puede crear tienda y publicar productos
- `admin` — acceso completo y moderacion

---

## Arquitectura

```
cuceimart/
├── backend/
│   ├── main.py                  # Entry point FastAPI
│   ├── seed.py                  # Script de datos iniciales
│   ├── models/
│   │   └── database.py          # SQLModel + SQLite (tablas, enums)
│   ├── schemas/
│   │   └── schemas.py           # Pydantic v2 (request/response)
│   ├── services/
│   │   └── auth.py              # JWT, bcrypt, dependencias
│   ├── routers/
│   │   ├── auth.py              # POST /auth/register|login, GET /auth/me
│   │   ├── products.py          # CRUD productos + subida de imagenes
│   │   ├── stores.py            # CRUD tiendas + logos
│   │   ├── reviews.py           # Sistema de reseñas
│   │   ├── categories.py        # Categorias (admin)
│   │   └── stats.py             # Estadisticas y busqueda global
│   └── static/
│       └── uploads/             # Imagenes subidas
├── frontend/
│   └── pages/
│       ├── login.html           # Pagina de login/registro
│       └── marketplace.html     # Marketplace principal
└── requirements.txt
```

**Stack tecnologico:**
- Backend: FastAPI + SQLModel + SQLite
- Autenticacion: JWT (python-jose) + bcrypt (passlib)
- Frontend: HTML5 + CSS3 + Vanilla JS
- Fuentes: Syne (display) + DM Sans (cuerpo)
- Iconos: FontAwesome 6

---

## Instalacion

### 1. Clonar y preparar entorno

```bash
git clone <repo-url>
cd cuceimart

# Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Poblar la base de datos con datos iniciales

```bash
cd backend
python seed.py
```

Esto crea `cuceimart.db` con:
- Categorias precargadas (Tecnologia, Comida, Ropa, etc.)
- Usuario admin
- Un emprendedor de prueba con tienda y productos
- Un estudiante de prueba con reseña

Credenciales de prueba:

| Rol           | Email                        | Contrasena       |
|---------------|------------------------------|------------------|
| Admin         | admin@cuceimart.udg.mx       | Admin1234!       |
| Emprendedor   | demian@alumnos.udg.mx        | Nexcode2025!     |
| Estudiante    | estudiante@alumnos.udg.mx    | Cucei2025!       |

### 4. Levantar el servidor

```bash
cd backend
uvicorn main:app --reload --port 8000
```

La API estara disponible en `http://localhost:8000`
Documentacion interactiva: `http://localhost:8000/docs`

### 5. Abrir el frontend

Abre directamente en el navegador:
```
cuceimart/frontend/pages/login.html
cuceimart/frontend/pages/marketplace.html
```

O sirve los archivos con un servidor estatico:
```bash
cd frontend
python -m http.server 3000
# Luego visita http://localhost:3000/pages/login.html
```

---

## Endpoints principales

### Autenticacion

```bash
# Registrar usuario
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@alumnos.udg.mx","username":"juan_udg","password":"Pass1234!","full_name":"Juan Lopez","role":"student"}'

# Iniciar sesion
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@alumnos.udg.mx","password":"Pass1234!"}'

# Perfil propio (requiere Bearer token)
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

### Productos

```bash
# Listar con filtros
curl "http://localhost:8000/products/?q=cable&category=tecnologia&min_price=50&max_price=500&sort_by=total_sold"

# Detalle de producto
curl http://localhost:8000/products/1

# Crear producto (emprendedor)
curl -X POST http://localhost:8000/products/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Nuevo producto","description":"Descripcion del producto","price":150.00,"stock":20}'

# Subir imagen a producto
curl -X POST http://localhost:8000/products/1/image \
  -H "Authorization: Bearer <token>" \
  -F "file=@imagen.jpg"
```

### Tiendas

```bash
# Listar tiendas con busqueda
curl "http://localhost:8000/stores/?q=tech"

# Tiendas destacadas
curl http://localhost:8000/stores/featured

# Crear tienda (requiere rol entrepreneur)
curl -X POST http://localhost:8000/stores/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Mi Tienda","description":"Descripcion","category":"Tecnologia"}'
```

### Reseñas

```bash
# Ver reseñas de una tienda
curl http://localhost:8000/reviews/store/1

# Dejar reseña (usuario autenticado)
curl -X POST http://localhost:8000/reviews/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"store_id":1,"rating":5,"title":"Excelente","comment":"Muy buen servicio"}'
```

### Estadisticas y busqueda global

```bash
# Estadisticas de la plataforma
curl http://localhost:8000/stats/platform

# Busqueda global (productos + tiendas)
curl "http://localhost:8000/stats/search?q=cable"
```

---

## Entidades de la base de datos

| Tabla         | Descripcion                                           |
|---------------|-------------------------------------------------------|
| `users`       | Usuarios (estudiante, emprendedor, admin)              |
| `stores`      | Tiendas de los emprendedores                          |
| `products`    | Productos publicados en las tiendas                   |
| `categories`  | Categorias de productos                               |
| `reviews`     | Reseñas de 1-5 estrellas por tienda                   |
| `cart_items`  | Carrito de compras por usuario                        |
| `orders`      | Pedidos con estado (pending, confirmed, completed)    |
| `order_items` | Items individuales dentro de cada pedido              |

---

## Queries utiles para VSCode (SQLite Viewer)

Abre `backend/cuceimart.db` con la extension **SQLite Viewer** en VSCode y usa:

```sql
-- Ver todos los usuarios
SELECT id, email, username, role, is_verified, created_at FROM users;

-- Emprendedores con sus tiendas
SELECT u.username, u.email, s.name AS tienda, s.total_sales, s.is_featured
FROM users u JOIN stores s ON u.id = s.owner_id;

-- Productos activos con categoria
SELECT p.name, p.price, p.stock, p.total_sold, c.name AS categoria, s.name AS tienda
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
JOIN stores s ON p.store_id = s.id
WHERE p.status = 'active'
ORDER BY p.total_sold DESC;

-- Ranking de tiendas por calificacion promedio
SELECT s.name, s.category, s.total_sales,
       ROUND(AVG(r.rating), 2) AS avg_rating,
       COUNT(r.id) AS num_reviews
FROM stores s
LEFT JOIN reviews r ON s.id = r.store_id
GROUP BY s.id
ORDER BY avg_rating DESC, num_reviews DESC;

-- Productos sin ventas (inventario sin movimiento)
SELECT p.name, p.price, p.stock, s.name AS tienda
FROM products p JOIN stores s ON p.store_id = s.id
WHERE p.total_sold = 0 AND p.status = 'active';

-- Insertar nueva categoria
INSERT INTO categories (name, slug, icon, color)
VALUES ('Impresion 3D', 'impresion-3d', 'fa-cube', '#6366f1');

-- Hacer a un usuario emprendedor
UPDATE users SET role = 'entrepreneur' WHERE email = 'usuario@alumnos.udg.mx';

-- Destacar una tienda
UPDATE stores SET is_featured = 1 WHERE name = 'Nombre de la tienda';
```

---

## Expandir la base de datos

Para agregar nuevas columnas o tablas:

1. Agrega el campo en `backend/models/database.py`
2. Ejecuta `python seed.py` (si la columna es nueva, podria requerir recrear la DB o usar ALTER TABLE)
3. Actualiza el schema en `backend/schemas/schemas.py`
4. Actualiza el router correspondiente

Para una migracion limpia durante desarrollo:
```bash
rm backend/cuceimart.db
python backend/seed.py
```

---

## Variables de entorno (produccion)

Crea un archivo `.env` en `backend/`:

```env
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
DATABASE_URL=sqlite:///./cuceimart.db
```

---

## Funcionalidades implementadas

- CRUD completo: usuarios, tiendas, productos, reseñas, categorias, pedidos
- Autenticacion JWT con bcrypt
- Roles de usuario con proteccion de endpoints
- Busqueda con multiples filtros (texto, categoria, precio, orden)
- Sistema de calificaciones 1-5 estrellas con promedio por tienda
- Emprendedores destacados ordenados por ventas
- Subida y servicio de imagenes (productos y logos)
- Paginacion en listados
- Estadisticas de plataforma
- Frontend: login/registro con animaciones + marketplace completo
- Documentacion automatica en /docs (Swagger UI)
