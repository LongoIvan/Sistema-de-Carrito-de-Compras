import streamlit as st
from services import api


def _extraer_lista(data, claves_posibles: tuple[str, ...]) -> list[dict]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for clave in claves_posibles:
            if isinstance(data.get(clave), list):
                return [x for x in data[clave] if isinstance(x, dict)]
    return []


def _to_float(val, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _obtener_cantidad_item(item: dict) -> float:
    for clave in ("cantidad", "cant", "unidades", "quantity"):
        if clave in item and item[clave] is not None:
            return _to_float(item[clave], 0.0)
    return 1.0


def _obtener_precio_item(item: dict) -> float:
    for clave in ("precio_unitario", "precio", "valor_unitario", "unit_price"):
        if clave in item and item[clave] is not None:
            return _to_float(item[clave], 0.0)
    return 0.0


def _consultar_estado_carrito(id_carrito: int) -> tuple[str, dict | None]:
    res = api._request("GET", f"/api/carritos/{id_carrito}")
    if not res["ok"]:
        return "Desconocido", res
    data = res["data"] if isinstance(res["data"], dict) else {}
    estado = str(data.get("estado") or st.session_state.get("estado_carrito") or "Desconocido")
    return estado, None


def _consultar_items_y_total(id_carrito: int) -> tuple[list[dict], float, dict | None]:
    res_items = api._request("GET", f"/api/carritos/{id_carrito}/items")
    if not res_items["ok"]:
        return [], 0.0, res_items

    data_items = res_items["data"] if isinstance(res_items["data"], dict) else {}
    items = data_items.get("items") if isinstance(data_items.get("items"), list) else []

    total = 0.0
    res_total = api._request("GET", f"/api/carritos/{id_carrito}/total")
    if res_total["ok"] and isinstance(res_total["data"], dict):
        total = _to_float(res_total["data"].get("total"), 0.0)
    else:
        for it in items:
            if "subtotal" in it and it["subtotal"] is not None:
                total += _to_float(it["subtotal"], 0.0)
            else:
                total += _obtener_cantidad_item(it) * _obtener_precio_item(it)

    return items, total, None


def _render_grafico_stock(productos: list[dict]) -> None:
    if not productos:
        st.info("Sin datos de productos para graficar.")
        return

    filas = []
    for p in productos:
        nombre = str(p.get("nombre") or p.get("titulo") or f"Prod #{p.get('idproducto') or p.get('id') or '?'}")
        stock = _to_float(p.get("stock", p.get("existencias", 0)), 0.0)
        categoria = str(p.get("categoria") or "General")
        filas.append({"Producto": nombre, "Stock": stock, "Categoría": categoria})

    filas_ordenadas = sorted(filas, key=lambda x: x["Stock"])[:12]

    try:
        import plotly.express as px

        fig = px.bar(
            filas_ordenadas,
            x="Stock",
            y="Producto",
            color="Categoría",
            orientation="h",
            title="Productos con menor stock disponible",
        )
        fig.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.caption("Mostrando gráfico nativo de Streamlit (instala `plotly` para gráficos interactivos).")
        mapa_barras = {f["Producto"]: f["Stock"] for f in filas_ordenadas}
        st.bar_chart(mapa_barras, horizontal=True, height=320)


def _render_grafico_categorias(productos: list[dict]) -> None:
    if not productos:
        st.info("Sin categorías para mostrar.")
        return

    conteo_cat: dict[str, int] = {}
    for p in productos:
        cat = str(p.get("categoria") or "Sin categoría").strip()
        conteo_cat[cat] = conteo_cat.get(cat, 0) + 1

    try:
        import plotly.express as px

        datos_cat = [{"Categoría": k, "Cantidad": v} for k, v in conteo_cat.items()]
        fig = px.pie(
            datos_cat,
            names="Categoría",
            values="Cantidad",
            hole=0.45,
            title="Distribución del catálogo por categoría",
        )
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.bar_chart(conteo_cat, height=320)


def render_home() -> None:
    st.markdown("## Panel General — Carrito de Compras")
    st.caption("Resumen del usuario activo, estado e ítems del carrito actual e inventario de productos.")

    id_usuario = int(st.session_state.get("id_usuario") or 1)
    id_carrito = st.session_state.get("id_carrito")

    c_ctx1, c_ctx2, c_ctx3, c_ctx4 = st.columns([1.4, 1.4, 1.4, 1.2])
    with c_ctx1:
        st.info(f"**Usuario activo:** #{id_usuario}")
    with c_ctx2:
        st.info(f"**Carrito actual:** {f'#{int(id_carrito)}' if id_carrito else 'No asignado'}")
    with c_ctx3:
        umbral_bajo_stock = st.number_input("Alerta bajo stock ≤", min_value=0, max_value=100, value=5, step=1)
    with c_ctx4:
        st.write("")
        if st.button("Actualizar todo", type="primary", use_container_width=True):
            st.rerun()

    with st.spinner("Sincronizando datos con el backend..."):
        res_usuario = api._request("GET", f"/api/usuario/{id_usuario}/completo")
        res_productos = api.listar_productos()

        err_carrito = None
        if id_carrito is not None:
            cid = int(id_carrito)
            estado_carrito, err_estado = _consultar_estado_carrito(cid)
            items_carrito, total_carrito, err_items = _consultar_items_y_total(cid)
            err_carrito = err_estado or err_items
            if estado_carrito != "Desconocido":
                st.session_state["estado_carrito"] = estado_carrito
        else:
            items_carrito, total_carrito = [], 0.0
            estado_carrito = "Sin carrito"

    productos = (
        _extraer_lista(res_productos["data"], ("productos", "items", "data", "resultados"))
        if res_productos["ok"]
        else []
    )

    total_productos = len(productos)
    sin_stock = [
        p for p in productos
        if _to_float(p.get("stock", p.get("existencias", 0)), 0.0) <= 0
        or p.get("activo") is False
        or p.get("disponible") is False
    ]
    bajo_stock = [
        p for p in productos
        if 0 < _to_float(p.get("stock", p.get("existencias", 0)), 0.0) <= umbral_bajo_stock
    ]

    unidades_en_carrito = sum(_obtener_cantidad_item(it) for it in items_carrito)

    # ---------------------------------------------------------
    # 1. TARJETAS KPI PRINCIPALES
    # ---------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            label="Productos en catálogo",
            value=total_productos,
            delta=f"{len(sin_stock)} sin stock / inactivos",
            delta_color="inverse",
        )
    with k2:
        st.metric(
            label=f"Alerta bajo stock (≤ {int(umbral_bajo_stock)})",
            value=len(bajo_stock),
            delta="Revisar reposición" if bajo_stock else "Stock saludable",
            delta_color="inverse" if bajo_stock else "normal",
        )
    with k3:
        st.metric(
            label="Unidades en carrito",
            value=int(unidades_en_carrito),
            delta=f"Estado: {estado_carrito}",
        )
    with k4:
        st.metric(
            label="Total carrito",
            value=f"${total_carrito:,.2f}" if id_carrito is not None else "—",
            delta="Se valida al finalizar",
        )

    st.divider()

    # ---------------------------------------------------------
    # 2. GRÁFICOS DE INVENTARIO Y CATEGORÍAS
    # ---------------------------------------------------------
    g1, g2 = st.columns([1.3, 1])
    with g1:
        with st.container(border=True):
            _render_grafico_stock(productos)
    with g2:
        with st.container(border=True):
            _render_grafico_categorias(productos)

    st.divider()

    # ---------------------------------------------------------
    # 3. PERFIL ACTIVO, ALERTAS DE STOCK Y CARRITO
    # ---------------------------------------------------------
    col_izq, col_der = st.columns([1, 1.2])

    with col_izq:
        with st.container(border=True):
            st.subheader("Usuario activo")
            if res_usuario["ok"] and isinstance(res_usuario["data"], dict):
                perfil = res_usuario["data"]
                st.write(f"**ID:** {perfil.get('idusuario', id_usuario)}")
                st.write(f"**Nombre:** {perfil.get('nombre', '—')}")
                st.write(f"**Correo:** {perfil.get('mail', '—')}")
                st.write(f"**Rol:** {perfil.get('rol', '—')}")
            else:
                st.warning(f"No se pudo cargar el usuario #{id_usuario} ({res_usuario['status_code']}).")

        st.write("")

        with st.container(border=True):
            st.subheader("Alertas de inventario")
            if sin_stock:
                st.error(f"**Sin stock o inactivos ({len(sin_stock)}):**")
                for p in sin_stock[:5]:
                    st.write(f"• {p.get('nombre', 'Producto')} (stock: {p.get('stock', 0)})")
            if bajo_stock:
                st.warning(f"**Stock bajo ≤ {int(umbral_bajo_stock)} ({len(bajo_stock)}):**")
                for p in bajo_stock[:5]:
                    st.write(f"• {p.get('nombre', 'Producto')} (stock: {p.get('stock', 0)})")
            if not sin_stock and not bajo_stock:
                st.success("Todos los productos tienen stock suficiente.")

    with col_der:
        with st.container(border=True):
            st.subheader(f"Vista rápida del carrito {f'#{int(id_carrito)}' if id_carrito is not None else ''}")
            st.caption(
                "Agregar ítems no descuenta stock; el descuento ocurre al finalizar. "
                "Si hay cambios de stock o disponibilidad al finalizar, se devuelve 409 y el carrito queda Pendiente."
            )
            if id_carrito is None:
                st.info("Aún no hay un carrito activo en sesión. Crea uno desde la sección de Carrito.")
            elif err_carrito is not None:
                st.error(f"Error al consultar el carrito ({err_carrito['status_code']}): {err_carrito['data']}")
            elif not items_carrito:
                st.info("El carrito actual no tiene ítems.")
            else:
                st.dataframe(items_carrito, use_container_width=True, height=250)

    st.divider()

    # ---------------------------------------------------------
    # 4. ACCESOS RÁPIDOS ENTRE VISTAS
    # ---------------------------------------------------------
    st.subheader("Accesos rápidos")
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("Ir a Productos y Stock", use_container_width=True):
            st.switch_page("pages/producto.py")
    with a2:
        if st.button("Ir a Carrito y Checkout", type="primary", use_container_width=True):
            st.switch_page("pages/carrito.py")
    with a3:
        if st.button("Ir a Usuarios", use_container_width=True):
            st.switch_page("pages/usuario.py")


render_home()