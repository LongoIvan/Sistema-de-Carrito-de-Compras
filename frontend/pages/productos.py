import streamlit as st
from services import api


def _extraer_lista_productos(data) -> list[dict]:
    """Adapta distintas formas de respuesta JSON (lista directa o dict con clave)."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for clave in ("productos", "items", "data", "resultados"):
            if isinstance(data.get(clave), list):
                return data[clave]
    return []


def _obtener_id_producto(prod: dict) -> int | None:
    for clave in ("idproducto", "id_producto", "id"):
        if clave in prod and prod[clave] is not None:
            return int(prod[clave])
    return None


@st.cache_data(ttl=15, show_spinner="Cargando productos...")
def _cargar_productos_cache() -> dict:
    return api.listar_productos()


def _refrescar_productos() -> None:
    _cargar_productos_cache.clear()


def render_productos() -> None:
    st.title("Catálogo y Gestión de Productos")

    # Estado de sesión compartido con el resto de la app
    id_carrito = st.session_state.get("id_carrito")

    col_top_1, col_top_2 = st.columns([3, 1])
    with col_top_1:
        busqueda = st.text_input("Buscar producto por nombre o categoría", placeholder="Ej. teclado, periféricos...")
    with col_top_2:
        st.write("")
        st.write("")
        if st.button("Actualizar catálogo", use_container_width=True):
            _refrescar_productos()
            st.rerun()

    # ---------------------------------------------------------
    # 1. LISTADO DE PRODUCTOS
    # ---------------------------------------------------------
    res_lista = _cargar_productos_cache()
    if not res_lista["ok"]:
        st.error(f"No se pudieron obtener los productos ({res_lista['status_code']}): {res_lista['data']}")
        productos = []
    else:
        productos = _extraer_lista_productos(res_lista["data"])

    if busqueda:
        q = busqueda.strip().lower()
        productos_filtrados = [
            p for p in productos
            if q in str(p.get("nombre", "")).lower()
            or q in str(p.get("categoria", "")).lower()
            or q in str(p.get("descripcion", "")).lower()
        ]
    else:
        productos_filtrados = productos

    st.subheader("Productos disponibles")
    if not productos_filtrados:
        st.info("No hay productos para mostrar o aún no se cargaron desde la API.")
    else:
        st.dataframe(productos_filtrados, use_container_width=True)

        # Selector rápido para operar sobre un producto concreto
        opciones_ids = []
        etiquetas = {}
        for p in productos_filtrados:
            pid = _obtener_id_producto(p)
            if pid is not None:
                opciones_ids.append(pid)
                nombre = p.get("nombre", "Sin nombre")
                stock = p.get("stock", "?")
                etiquetas[pid] = f"#{pid} - {nombre} (stock: {stock})"

        if opciones_ids:
            id_sel = st.selectbox(
                "Seleccionar producto para acciones rápidas",
                options=opciones_ids,
                format_func=lambda x: etiquetas.get(x, str(x)),
            )

            col_acc_1, col_acc_2 = st.columns(2)

            # Agregar al carrito pendiente (no descuenta stock hasta finalizar)
            with col_acc_1:
                st.markdown("#### Agregar al carrito")
                if not id_carrito:
                    st.warning("No hay un carrito activo en sesión (`id_carrito`). Crea o selecciona uno primero.")
                else:
                    cant_agregar = st.number_input("Cantidad", min_value=1, value=1, step=1, key="cant_add_prod")
                    if st.button("Agregar al carrito", type="primary", use_container_width=True):
                        with st.spinner("Agregando ítem al carrito..."):
                            res_add = api.agregar_item_carrito(
                                id_carrito=int(id_carrito),
                                id_producto=int(id_sel),
                                cantidad=int(cant_agregar),
                            )
                        if res_add["ok"]:
                            st.toast("Ítem agregado al carrito.")
                            st.success("Producto agregado al carrito pendiente.")
                        else:
                            st.error(f"Error ({res_add['status_code']}): {res_add['data']}")

            # Administrar stock (PATCH /productos/{id}/stock/agregar y quitar)
            with col_acc_2:
                st.markdown("#### Administrar stock")
                cant_stock = st.number_input("Unidades de stock", min_value=1, value=5, step=1, key="cant_stock_prod")
                c_stk_1, c_stk_2 = st.columns(2)
                with c_stk_1:
                    if st.button("Agregar stock", use_container_width=True):
                        with st.spinner("Agregando existencias..."):
                            res_stk = api.agregar_stock_producto(int(id_sel), int(cant_stock))
                        if res_stk["ok"]:
                            _refrescar_productos()
                            st.success("Stock agregado (producto reactivado si correspondía).")
                            st.rerun()
                        else:
                            st.error(f"Error ({res_stk['status_code']}): {res_stk['data']}")
                with c_stk_2:
                    if st.button("Quitar stock", use_container_width=True):
                        with st.spinner("Descontando existencias..."):
                            res_stk = api.quitar_stock_producto(int(id_sel), int(cant_stock))
                        if res_stk["ok"]:
                            _refrescar_productos()
                            st.success("Stock descontado.")
                            st.rerun()
                        else:
                            st.error(f"Error ({res_stk['status_code']}): {res_stk['data']}")

    st.divider()

    # ---------------------------------------------------------
    # 2. CREAR NUEVO PRODUCTO (POST)
    # ---------------------------------------------------------
    st.subheader("Crear producto")
    with st.form("form_crear_producto", clear_on_submit=True):
        nombre = st.text_input("Nombre")
        precio = st.number_input("Precio", min_value=0.0, value=0.0, step=100.0)
        categoria = st.text_input("Categoría")
        descripcion = st.text_area("Descripción")
        stock_inicial = st.number_input("Stock inicial", min_value=0, value=0, step=1)

        submitted = st.form_submit_button("Guardar producto")
        if submitted:
            if not nombre.strip():
                st.warning("El nombre del producto es obligatorio.")
            else:
                # Ajusta estas claves si tu controller_productos.py espera otros nombres
                payload = {
                    "nombre": nombre.strip(),
                    "precio": precio,
                    "categoria": categoria.strip(),
                    "descripcion": descripcion.strip(),
                    "stock": int(stock_inicial),
                }
                with st.spinner("Creando producto..."):
                    res_create = api.crear_producto(payload)
                if res_create["ok"]:
                    _refrescar_productos()
                    st.success("Producto creado correctamente.")
                    st.rerun()
                else:
                    st.error(f"Error ({res_create['status_code']}): {res_create['data']}")


# Permite ejecutarlo tanto desde st.navigation como archivo de página
render_productos()