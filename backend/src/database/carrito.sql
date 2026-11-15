--
-- PostgreSQL database dump
--

\restrict B4AbLqDeNAbnZNEjRqCnP4qCBxsvvqhByXBblfwvluB16JKcdpn4CWspfLnmJYb

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-11-15 20:36:46

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 866 (class 1247 OID 16722)
-- Name: categoria; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.categoria AS ENUM (
    'Electronico',
    'Comida'
);


ALTER TYPE public.categoria OWNER TO postgres;

--
-- TOC entry 863 (class 1247 OID 16715)
-- Name: estadocarrito; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estadocarrito AS ENUM (
    'Pendiente',
    'Finalizado',
    'Cancelado'
);


ALTER TYPE public.estadocarrito OWNER TO postgres;

--
-- TOC entry 869 (class 1247 OID 16728)
-- Name: rol; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.rol AS ENUM (
    'Administrador',
    'Cliente'
);


ALTER TYPE public.rol OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 16767)
-- Name: carrito; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carrito (
    idcarrito integer NOT NULL,
    idusuario integer NOT NULL,
    fecha date DEFAULT CURRENT_DATE NOT NULL,
    estado public.estadocarrito DEFAULT 'Pendiente'::public.estadocarrito NOT NULL
);


ALTER TABLE public.carrito OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16766)
-- Name: carrito_idcarrito_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.carrito ALTER COLUMN idcarrito ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.carrito_idcarrito_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 229 (class 1259 OID 16833)
-- Name: carritos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carritos (
    idcarrito integer NOT NULL,
    idusuario integer NOT NULL,
    fecha date NOT NULL,
    estado text DEFAULT 'Pendiente'::text NOT NULL,
    item jsonb DEFAULT '[]'::jsonb NOT NULL
);


ALTER TABLE public.carritos OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16784)
-- Name: item_carrito; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.item_carrito (
    id_item_carrito integer NOT NULL,
    idcarrito integer NOT NULL,
    id_item_producto integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL
);


ALTER TABLE public.item_carrito OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16783)
-- Name: item_carrito_id_item_carrito_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.item_carrito ALTER COLUMN id_item_carrito ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.item_carrito_id_item_carrito_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 230 (class 1259 OID 16847)
-- Name: items_carrito; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.items_carrito (
    id_item_carrito integer NOT NULL,
    id_item_producto integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario double precision NOT NULL
);


ALTER TABLE public.items_carrito OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16749)
-- Name: producto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producto (
    idproducto integer NOT NULL,
    nombre character varying(150) NOT NULL,
    precio numeric(10,2) NOT NULL,
    stock integer DEFAULT 1 NOT NULL,
    categoria public.categoria NOT NULL,
    fecha date DEFAULT CURRENT_DATE NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    descripcion text
);


ALTER TABLE public.producto OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16748)
-- Name: producto_idproducto_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.producto ALTER COLUMN idproducto ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.producto_idproducto_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 228 (class 1259 OID 16816)
-- Name: productos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.productos (
    idproducto integer NOT NULL,
    nombre text NOT NULL,
    precio double precision NOT NULL,
    stock integer DEFAULT 1 NOT NULL,
    categoria text NOT NULL,
    fecha date NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    descripcion text NOT NULL
);


ALTER TABLE public.productos OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16734)
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    idusuario integer NOT NULL,
    nombre character varying(100) NOT NULL,
    mail character varying(150) NOT NULL,
    contrasenia character varying(255) NOT NULL,
    rol public.rol NOT NULL
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16733)
-- Name: usuario_idusuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.usuario ALTER COLUMN idusuario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.usuario_idusuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 227 (class 1259 OID 16804)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    idusuario integer NOT NULL,
    nombre text NOT NULL,
    mail text NOT NULL,
    contrasenia text NOT NULL,
    rol text NOT NULL
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- TOC entry 5078 (class 0 OID 16767)
-- Dependencies: 224
-- Data for Name: carrito; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carrito (idcarrito, idusuario, fecha, estado) FROM stdin;
1	1	2026-11-12	Pendiente
2	2	2026-11-12	Finalizado
\.


--
-- TOC entry 5083 (class 0 OID 16833)
-- Dependencies: 229
-- Data for Name: carritos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carritos (idcarrito, idusuario, fecha, estado, item) FROM stdin;
\.


--
-- TOC entry 5080 (class 0 OID 16784)
-- Dependencies: 226
-- Data for Name: item_carrito; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.item_carrito (id_item_carrito, idcarrito, id_item_producto, cantidad, precio_unitario) FROM stdin;
1	1	1	1	59.99
2	1	3	2	12.00
3	2	2	1	35.50
4	2	4	3	3.50
\.


--
-- TOC entry 5084 (class 0 OID 16847)
-- Dependencies: 230
-- Data for Name: items_carrito; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.items_carrito (id_item_carrito, id_item_producto, cantidad, precio_unitario) FROM stdin;
\.


--
-- TOC entry 5076 (class 0 OID 16749)
-- Dependencies: 222
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto (idproducto, nombre, precio, stock, categoria, fecha, activo, descripcion) FROM stdin;
1	Auriculares Inalámbricos	59.99	25	Electronico	2026-11-12	t	Auriculares Bluetooth con cancelación de ruido.
2	Mouse Gamer RGB	35.50	15	Electronico	2026-11-12	t	Mouse ergonómico con luces RGB y 6 botones programables.
3	Café en Grano 500g	12.00	50	Comida	2026-11-12	t	Café arábica tostado de altura.
4	Barra de Chocolate Amargo	3.50	100	Comida	2026-11-12	t	Chocolate 70% cacao sin azúcares añadidos.
\.


--
-- TOC entry 5082 (class 0 OID 16816)
-- Dependencies: 228
-- Data for Name: productos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.productos (idproducto, nombre, precio, stock, categoria, fecha, activo, descripcion) FROM stdin;
\.


--
-- TOC entry 5074 (class 0 OID 16734)
-- Dependencies: 220
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (idusuario, nombre, mail, contrasenia, rol) FROM stdin;
1	Ana Gómez	ana@mail.com	ejemplo123	Cliente
2	Carlos Pérez	carlos@mail.com	ejemplo1234	Cliente
3	Administrador	admin@mail.com	admin123	Administrador
\.


--
-- TOC entry 5081 (class 0 OID 16804)
-- Dependencies: 227
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (idusuario, nombre, mail, contrasenia, rol) FROM stdin;
\.


--
-- TOC entry 5090 (class 0 OID 0)
-- Dependencies: 223
-- Name: carrito_idcarrito_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.carrito_idcarrito_seq', 2, true);


--
-- TOC entry 5091 (class 0 OID 0)
-- Dependencies: 225
-- Name: item_carrito_id_item_carrito_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.item_carrito_id_item_carrito_seq', 4, true);


--
-- TOC entry 5092 (class 0 OID 0)
-- Dependencies: 221
-- Name: producto_idproducto_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.producto_idproducto_seq', 4, true);


--
-- TOC entry 5093 (class 0 OID 0)
-- Dependencies: 219
-- Name: usuario_idusuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_idusuario_seq', 4, true);


--
-- TOC entry 4912 (class 2606 OID 16777)
-- Name: carrito carrito_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carrito
    ADD CONSTRAINT carrito_pkey PRIMARY KEY (idcarrito);


--
-- TOC entry 4920 (class 2606 OID 16846)
-- Name: carritos carritos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carritos
    ADD CONSTRAINT carritos_pkey PRIMARY KEY (idcarrito);


--
-- TOC entry 4914 (class 2606 OID 16793)
-- Name: item_carrito item_carrito_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_carrito
    ADD CONSTRAINT item_carrito_pkey PRIMARY KEY (id_item_carrito);


--
-- TOC entry 4922 (class 2606 OID 16855)
-- Name: items_carrito items_carrito_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.items_carrito
    ADD CONSTRAINT items_carrito_pkey PRIMARY KEY (id_item_carrito);


--
-- TOC entry 4910 (class 2606 OID 16765)
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (idproducto);


--
-- TOC entry 4918 (class 2606 OID 16832)
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (idproducto);


--
-- TOC entry 4906 (class 2606 OID 16747)
-- Name: usuario usuario_mail_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_mail_key UNIQUE (mail);


--
-- TOC entry 4908 (class 2606 OID 16745)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (idusuario);


--
-- TOC entry 4916 (class 2606 OID 16815)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (idusuario);


--
-- TOC entry 4923 (class 2606 OID 16778)
-- Name: carrito fk_carrito_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carrito
    ADD CONSTRAINT fk_carrito_usuario FOREIGN KEY (idusuario) REFERENCES public.usuario(idusuario) ON DELETE CASCADE;


--
-- TOC entry 4924 (class 2606 OID 16794)
-- Name: item_carrito fk_item_carrito_carrito; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_carrito
    ADD CONSTRAINT fk_item_carrito_carrito FOREIGN KEY (idcarrito) REFERENCES public.carrito(idcarrito) ON DELETE CASCADE;


--
-- TOC entry 4925 (class 2606 OID 16799)
-- Name: item_carrito fk_item_carrito_producto; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item_carrito
    ADD CONSTRAINT fk_item_carrito_producto FOREIGN KEY (id_item_producto) REFERENCES public.producto(idproducto) ON DELETE RESTRICT;


-- Completed on 2026-11-15 20:36:47

--
-- PostgreSQL database dump complete
--

\unrestrict B4AbLqDeNAbnZNEjRqCnP4qCBxsvvqhByXBblfwvluB16JKcdpn4CWspfLnmJYb

