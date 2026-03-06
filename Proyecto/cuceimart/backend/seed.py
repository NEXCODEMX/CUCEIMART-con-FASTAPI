import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sqlmodel import Session, select
from models.database import (
    create_db_and_tables, engine,
    User, Store, Product, Category, Review, UserRole, ProductStatus
)
from services.auth import hash_password
from datetime import datetime
def seed():
    create_db_and_tables()
    with Session(engine) as session:
        # ── Categories ─────────────────────────────────────────────────────
        categories_data = [
            {"name": "Tecnologia",    "slug": "tecnologia",    "icon": "fa-microchip",     "color": "#4F46E5"},
            {"name": "Comida",        "slug": "comida",        "icon": "fa-utensils",       "color": "#F59E0B"},
            {"name": "Ropa y Moda",   "slug": "ropa",          "icon": "fa-shirt",          "color": "#EC4899"},
            {"name": "Libros",        "slug": "libros",        "icon": "fa-book",           "color": "#10B981"},
            {"name": "Arte",          "slug": "arte",          "icon": "fa-palette",        "color": "#8B5CF6"},
            {"name": "Servicios",     "slug": "servicios",     "icon": "fa-briefcase",      "color": "#0EA5E9"},
            {"name": "Electronica",   "slug": "electronica",   "icon": "fa-bolt",           "color": "#F97316"},
            {"name": "Manualidades",  "slug": "manualidades",  "icon": "fa-scissors",       "color": "#14B8A6"},
        ]
        cats = {}
        for cd in categories_data:
            existing = session.exec(select(Category).where(Category.slug == cd["slug"])).first()
            if not existing:
                cat = Category(**cd)
                session.add(cat)
                session.flush()
                cats[cd["slug"]] = cat
            else:
                cats[cd["slug"]] = existing
        session.commit()
        # ── Admin user ─────────────────────────────────────────────────────
        admin = session.exec(select(User).where(User.email == "admin@cuceimart.udg.mx")).first()
        if not admin:
            admin = User(
                email            = "admin@cuceimart.udg.mx",
                username         = "admin",
                hashed_password  = hash_password("Admin1234!"),
                full_name        = "Administrador CUCEI MART",
                role             = UserRole.admin,
                is_verified      = True,
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
            print("Admin creado: admin@cuceimart.udg.mx / Admin1234!")
        # ── Sample entrepreneur ────────────────────────────────────────────
        entrepreneur = session.exec(select(User).where(User.email == "demian@alumnos.udg.mx")).first()
        if not entrepreneur:
            entrepreneur = User(
                email            = "demian@alumnos.udg.mx",
                username         = "demian_nexcode",
                hashed_password  = hash_password("Nexcode2025!"),
                full_name        = "Demian Fernandez Agraz",
                role             = UserRole.entrepreneur,
                is_verified      = True,
                bio              = "Estudiante de Ing. en Computacion, apasionado por la tecnologia.",
            )
            session.add(entrepreneur)
            session.commit()
            session.refresh(entrepreneur)

        # Store
        store = session.exec(select(Store).where(Store.owner_id == entrepreneur.id)).first()
        if not store:
            store = Store(
                owner_id    = entrepreneur.id,
                name        = "TechZone CUCEI",
                description = "Accesorios tecnologicos, cables, memorias USB y gadgets para estudiantes de ingenieria.",
                category    = "Tecnologia",
                contact_email = "techzone@cucei.udg.mx",
                total_sales = 142,
                is_featured = True,
            )
            session.add(store)
            session.commit()
            session.refresh(store)

        # Products
        if not session.exec(select(Product).where(Product.store_id == store.id)).first():
            products_data = [
                {
                    "name"        : "Cable USB-C Trenzado 2m",
                    "description" : "Cable de nylon trenzado USB-C a USB-A, carga rapida 65W, transferencia 480Mbps. Compatible con laptops, tablets y smartphones.",
                    "price"       : 129.00,
                    "stock"       : 50,
                    "total_sold"  : 87,
                    "tags"        : "cable,usb-c,carga,electronica",
                    "category_id" : cats["tecnologia"].id,
                },
                {
                    "name"        : "Hub USB 4 Puertos",
                    "description" : "Concentrador USB 3.0 de 4 puertos con indicador LED. Ideal para laboratorios y clase.",
                    "price"       : 189.00,
                    "stock"       : 25,
                    "total_sold"  : 55,
                    "tags"        : "hub,usb,puertos,electronica",
                    "category_id" : cats["tecnologia"].id,
                },
                {
                    "name"        : "Memoria USB 64GB Kingston",
                    "description" : "Memoria USB 3.2 de alta velocidad, 64GB. Velocidad de lectura hasta 200MB/s.",
                    "price"       : 219.00,
                    "stock"       : 30,
                    "total_sold"  : 120,
                    "tags"        : "memoria,usb,almacenamiento",
                    "category_id" : cats["tecnologia"].id,
                },
            ]
            for pd in products_data:
                p = Product(store_id=store.id, **pd)
                session.add(p)
            session.commit()

        # ── Sample student ─────────────────────────────────────────────────
        student = session.exec(select(User).where(User.email == "estudiante@alumnos.udg.mx")).first()
        if not student:
            student = User(
                email           = "estudiante@alumnos.udg.mx",
                username        = "estudiante_cucei",
                hashed_password = hash_password("Cucei2025!"),
                full_name       = "Juan Carlos Estudiante",
                role            = UserRole.student,
                is_verified     = True,
            )
            session.add(student)
            session.commit()
            session.refresh(student)

        # Review
        if not session.exec(select(Review).where(Review.store_id == store.id, Review.reviewer_id == student.id)).first():
            review = Review(
                store_id    = store.id,
                reviewer_id = student.id,
                rating      = 5,
                title       = "Excelente servicio",
                comment     = "Recibi mi pedido rapidamente y el cable es de muy buena calidad. Totalmente recomendable para los estudiantes de CUCEI.",
                is_verified_purchase = True,
            )
            session.add(review)
            session.commit()

        print("\nBase de datos inicializada correctamente.")
        print("Usuarios de prueba:")
        print("  Admin:        admin@cuceimart.udg.mx / Admin1234!")
        print("  Emprendedor:  demian@alumnos.udg.mx / Nexcode2025!")
        print("  Estudiante:   estudiante@alumnos.udg.mx / Cucei2025!")


if __name__ == "__main__":
    seed()
