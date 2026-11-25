-- =====================================================
-- SISTEMA DE CARRITO DE COMPRAS
-- Base de datos PostgreSQL
-- Incluye las migraciones 001, 002 y 003.
-- Ejecutar sobre una base de datos vacia.
-- =====================================================

BEGIN;

-- =====================================================
-- TIPOS ENUM
-- =====================================================

CREATE TYPE public.categoria AS ENUM (
    'Electronico',
    'Comida'
);

CREATE TYPE public.estadocarrito AS ENUM (
    'Pendiente',
    'Finalizado',
    'Cancelado'
);

CREATE TYPE public.rol AS ENUM (
    'Administrador',
    'Cliente'
);

-- =====================================================
-- TABLA USUARIO
-- =====================================================

CREATE TABLE public.usuario (
    idusuario integer NOT NULL,
    nombre character varying(100) NOT NULL,
    mail character varying(150) NOT NULL,
    contrasenia character varying(255) NOT NULL,
    rol public.rol NOT NULL
);

ALTER TABLE public.usuario
    ALTER COLUMN idusuario ADD GENERATED ALWAYS AS IDENTITY (
        SEQUENCE NAME public.usuario_idusuario_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    );

-- =====================================================
-- TABLA PRODUCTO
-- =====================================================

CREATE TABLE public.producto (
    idproducto integer NOT NULL,
    nombre character varying(150) NOT NULL,
    precio numeric(10,2) NOT NULL,
    stock integer DEFAULT 1 NOT NULL,
    categoria public.categoria NOT NULL,
    fecha date DEFAULT CURRENT_DATE NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    descripcion text,

    CONSTRAINT chk_producto_precio
        CHECK (precio > 0),

    CONSTRAINT chk_producto_stock
        CHECK (stock >= 0)
);

ALTER TABLE public.producto
    ALTER COLUMN idproducto ADD GENERATED ALWAYS AS IDENTITY (
        SEQUENCE NAME public.producto_idproducto_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    );

-- =====================================================
-- TABLA CARRITO
-- =====================================================

CREATE TABLE public.carrito (
    idcarrito integer NOT NULL,
    idusuario integer NOT NULL,
    fecha date DEFAULT CURRENT_DATE NOT NULL,
    estado public.estadocarrito DEFAULT 'Pendiente' NOT NULL
);

ALTER TABLE public.carrito
    ALTER COLUMN idcarrito ADD GENERATED ALWAYS AS IDENTITY (
        SEQUENCE NAME public.carrito_idcarrito_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    );

-- =====================================================
-- TABLA ITEM_CARRITO
-- =====================================================

CREATE TABLE public.item_carrito (
    id_item_carrito integer NOT NULL,
    idcarrito integer NOT NULL,
    id_item_producto integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,

    CONSTRAINT chk_item_cantidad
        CHECK (cantidad > 0),

    CONSTRAINT chk_item_precio
        CHECK (precio_unitario > 0)
);

ALTER TABLE public.item_carrito
    ALTER COLUMN id_item_carrito ADD GENERATED ALWAYS AS IDENTITY (
        SEQUENCE NAME public.item_carrito_id_item_carrito_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    );

-- =====================================================
-- CLAVES PRIMARIAS
-- =====================================================

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey
    PRIMARY KEY (idusuario);

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey
    PRIMARY KEY (idproducto);

ALTER TABLE ONLY public.carrito
    ADD CONSTRAINT carrito_pkey
    PRIMARY KEY (idcarrito);

ALTER TABLE ONLY public.item_carrito
    ADD CONSTRAINT item_carrito_pkey
    PRIMARY KEY (id_item_carrito);

-- =====================================================
-- RESTRICCIONES DE UNICIDAD
-- =====================================================

-- Impide registrar correos electronicos duplicados.

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_mail_key
    UNIQUE (mail);

-- Impide registrar correos duplicados aunque
-- existan diferencias entre mayusculas y minusculas.

CREATE UNIQUE INDEX usuario_mail_lower_unique
    ON public.usuario USING btree (lower(mail::text));

-- Impide duplicar un mismo producto dentro de un carrito.

ALTER TABLE ONLY public.item_carrito
    ADD CONSTRAINT uq_carrito_producto
    UNIQUE (idcarrito, id_item_producto);

-- =====================================================
-- CLAVES FORANEAS
-- =====================================================

-- Impide eliminar usuarios con carritos asociados.

ALTER TABLE ONLY public.carrito
    ADD CONSTRAINT fk_carrito_usuario
    FOREIGN KEY (idusuario)
    REFERENCES public.usuario(idusuario)
    ON DELETE RESTRICT;

-- Elimina los items asociados cuando se elimina un carrito.

ALTER TABLE ONLY public.item_carrito
    ADD CONSTRAINT fk_item_carrito_carrito
    FOREIGN KEY (idcarrito)
    REFERENCES public.carrito(idcarrito)
    ON DELETE CASCADE;

-- Impide eliminar productos asociados a items de carritos.

ALTER TABLE ONLY public.item_carrito
    ADD CONSTRAINT fk_item_carrito_producto
    FOREIGN KEY (id_item_producto)
    REFERENCES public.producto(idproducto)
    ON DELETE RESTRICT;

COMMIT;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================