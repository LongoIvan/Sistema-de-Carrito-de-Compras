import streamlit as st
from services import api


def _extraer_id_carrito(data) -> int | None:
    if isinstance(data, dict):
        for clave in ("idcarrito", "id_carrito", "id"):
            if clave in data and data[clave] is not None:
                try:
                    return int(data[clave])
                except (ValueError, TypeError):
                    return None
        for subclave in ("carrito", "data"):
            if isinstance(data.get(subclave), dict):
                return _extraer_id_carrito(data[subclave])
    return None


def _consultar_estado_carrito(id_carrito: int) -> tuple[str | None, dict | None]:
    res = api._request("GET", f"/api/carritos/{id_carrito}")
    if not res["ok"]:
        return None, res
    data = res["data"]
    estado = data.get("estado") if isinstance(data, dict) else None
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
        try:
            total = float(res_total["data"].get("total", 0.0))
        except (ValueError, TypeError):
            total = 0.0
    else:
        for it in items:
            try:
                total += float(it.get("subtotal", 0.0))
            except (ValueError, TypeError):
                pass

    return items, total, None



def render_carrito() -> None:
    st.title("Carrito de Compras e Ítems")

    id_usuario_sesion = int(st.session_state.get("id_usuario") or 1)
    id_carrito_sesion = st.session_state.get("id_carrito")

    # ---------------------------------------------------------
    # 1. SELECCIONAR O CREAR CARRITO
    # ---------------------------------------------------------
    st.subheader("Gestión del carrito")

    col_u, col_c, col_crear = st.columns([1.5, 2, 1.5])

    with col_u:
        id_usuario = int(
            st.number_input(
                "ID de usuario",
                min_value=1,
                step=1,
                value=id_usuario_sesion,
            )
        )

    st.session_state["id_usuario"] = id_usuario

    # Si cambia el usuario, se descarta el carrito seleccionado
    usuario_anterior = st.session_state.get("usuario_carrito_anterior")

    if usuario_anterior != id_usuario:
        st.session_state.pop("id_carrito", None)
        st.session_state.pop("sel_id_carrito", None)
        st.session_state["usuario_carrito_anterior"] = id_usuario

    # Consultar los carritos del usuario seleccionado
    with st.spinner("Buscando carritos del usuario..."):
        res_carritos = api.listar_carritos_usuario(id_usuario)

    if not res_carritos["ok"]:
        st.error(
            f"No se pudieron obtener los carritos "
            f"({res_carritos['status_code']}): {res_carritos['data']}"
        )
        return

    carritos = res_carritos["data"].get("carritos", [])

    # Crear diccionario de opciones: ID -> descripción
    opciones_carritos = {
        int(c["idcarrito"]): (
            f"Carrito #{c['idcarrito']} - {c.get('estado', 'Sin estado')}"
        )
        for c in carritos
    }

    with col_c:
        if opciones_carritos:
            ids_carritos = list(opciones_carritos.keys())

            # Si el carrito anterior no pertenece al usuario,
            # se selecciona el primero de su lista.
            if st.session_state.get("sel_id_carrito") not in ids_carritos:
                st.session_state.pop("sel_id_carrito", None)

            id_carrito = st.selectbox(
                "Seleccionar carrito",
                options=ids_carritos,
                format_func=lambda k: opciones_carritos[k],
                key="sel_id_carrito",
            )

            st.session_state["id_carrito"] = int(id_carrito)

        else:
            id_carrito = None
            st.session_state.pop("id_carrito", None)
            st.info("Este usuario todavía no tiene carritos.")

    with col_crear:
        st.write("")
        st.write("")
        if st.button(
            "Crear carrito pendiente",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Creando carrito pendiente..."):
                res_crear = api._request(
                    "POST",
                    "/api/carritos",
                    json_body={"idusuario": id_usuario},
                )

            if res_crear["ok"]:
                nuevo_id = _extraer_id_carrito(res_crear["data"])

                if nuevo_id is not None:
                    st.session_state["id_carrito"] = nuevo_id
                    st.session_state["sel_id_carrito"] = nuevo_id
                    st.session_state["estado_carrito"] = "Pendiente"

                    st.success(
                        f"Carrito pendiente creado (ID: {nuevo_id})."
                    )
                    st.rerun()
                else:
                    st.error(
                        "El carrito se creó, pero no se pudo obtener su ID."
                    )
            else:
                st.error(
                    f"Error ({res_crear['status_code']}): "
                    f"{res_crear['data']}"
                )

    # Si el usuario no tiene carritos, no continuar con las operaciones
    if id_carrito is None:
        return

    st.divider()

    if "ultimo_aviso_carrito" in st.session_state:
        aviso = st.session_state.pop("ultimo_aviso_carrito")
        if aviso["nivel"] == "warning":
            st.warning(aviso["mensaje"])
        elif aviso["nivel"] == "error":
            st.error(aviso["mensaje"])
        elif aviso["nivel"] == "success":
            st.success(aviso["mensaje"])
        if aviso.get("detalle") is not None:
            st.json(aviso["detalle"])

    st.divider()

    # ---------------------------------------------------------
    # 2. ESTADO, TOTAL E ÍTEMS DEL CARRITO
    # ---------------------------------------------------------
    estado_actual, err_estado = _consultar_estado_carrito(id_carrito)
    if err_estado is not None:
        st.error(f"No se pudo consultar el carrito #{id_carrito} ({err_estado['status_code']}): {err_estado['data']}")
        return

    st.session_state["estado_carrito"] = estado_actual or "Desconocido"
    es_pendiente = (estado_actual or "").strip().lower() == "pendiente"

    items, total_carrito, err_items = _consultar_items_y_total(id_carrito)

    col_hdr_1, col_hdr_2, col_hdr_3, col_hdr_4 = st.columns([2, 1, 1, 1])
    with col_hdr_1:
        st.subheader(f"Ítems del carrito #{id_carrito}")
    with col_hdr_2:
        st.metric("Estado", estado_actual or "—")
    with col_hdr_3:
        st.metric("Total", f"${total_carrito:,.2f}")
    with col_hdr_4:
        st.write("")
        if st.button("Refrescar", use_container_width=True):
            st.rerun()

    if err_items is not None:
        st.error(f"Error al obtener ítems ({err_items['status_code']}): {err_items['data']}")
    elif not items:
        st.info("El carrito está vacío.")
    else:
        st.dataframe(items, use_container_width=True)

    st.divider()

    # ---------------------------------------------------------
    # 3. AGREGAR, MODIFICAR O ELIMINAR ÍTEMS (SOLO PENDIENTE)
    # ---------------------------------------------------------
    st.subheader("Administrar ítems (solo carritos Pendientes)")
    if not es_pendiente:
        st.info(f"El carrito está en estado '{estado_actual}'. Solo se modifican ítems cuando está Pendiente.")
    else:
        # Agregar ítem
        col_add_1, col_add_2, col_add_3 = st.columns([2, 1.5, 1.5])
        with col_add_1:
            id_prod_add = int(
                st.number_input("ID de producto", min_value=1, step=1, value=1, key="carrito_id_prod")
            )
        with col_add_2:
            cant_add = int(
                st.number_input("Cantidad a agregar", min_value=1, step=1, value=1, key="carrito_cant_prod")
            )
        with col_add_3:
            st.write("")
            st.write("")
            if st.button("Agregar ítem", use_container_width=True):
                with st.spinner("Agregando ítem..."):
                    res_add = api._request(
                        "POST",
                        f"/api/carritos/{id_carrito}/items",
                        json_body={"idproducto": id_prod_add, "cantidad": cant_add},
                    )
                if res_add["ok"]:
                    st.toast("Ítem agregado/actualizado (no descuenta stock hasta finalizar).")
                    st.rerun()
                else:
                    st.error(f"Error ({res_add['status_code']}): {res_add['data']}")

        # Aumentar / disminuir / eliminar ítem existente por id_item_carrito
        if items:
            st.markdown("#### Modificar o quitar un ítem existente")
            opciones_items = {
                int(it["id_item_carrito"]): (
                    f"Ítem #{it['id_item_carrito']} — {it.get('nombre', 'Prod')} "
                    f"(ID prod: {it.get('idproducto')}, cant: {it.get('cantidad')})"
                )
                for it in items
                if it.get("id_item_carrito") is not None
            }

            if opciones_items:
                c_sel, c_delta, c_mas, c_menos, c_del = st.columns([2.4, 1.2, 1.1, 1.1, 1.1])
                with c_sel:
                    id_item_sel = int(
                        st.selectbox(
                            "Seleccionar ítem del carrito",
                            options=list(opciones_items.keys()),
                            format_func=lambda k: opciones_items[k],
                            key="sel_id_item_carrito",
                        )
                    )
                with c_delta:
                    delta = int(
                        st.number_input("Unidades", min_value=1, step=1, value=1, key="delta_unidades_item")
                    )
                with c_mas:
                    st.write("")
                    st.write("")
                    if st.button("+ Subir", use_container_width=True):
                        with st.spinner("Aumentando cantidad..."):
                            res_inc = api._request(
                                "PATCH",
                                f"/api/carritos/{id_carrito}/items/{id_item_sel}/aumentar",
                                json_body={"cantidad": delta},
                            )
                        if res_inc["ok"]:
                            st.toast("Cantidad aumentada.")
                            st.rerun()
                        else:
                            st.error(f"Error ({res_inc['status_code']}): {res_inc['data']}")
                with c_menos:
                    st.write("")
                    st.write("")
                    if st.button("- Bajar", use_container_width=True):
                        with st.spinner("Disminuyendo cantidad..."):
                            res_dec = api._request(
                                "PATCH",
                                f"/api/carritos/{id_carrito}/items/{id_item_sel}/disminuir",
                                json_body={"cantidad": delta},
                            )
                        if res_dec["ok"]:
                            st.toast("Cantidad actualizada (si llegó a 0, el ítem fue eliminado).")
                            st.rerun()
                        else:
                            st.error(f"Error ({res_dec['status_code']}): {res_dec['data']}")
                with c_del:
                    st.write("")
                    st.write("")
                    if st.button("Quitar", use_container_width=True):
                        with st.spinner("Eliminando ítem..."):
                            res_rm = api._request(
                                "DELETE",
                                f"/api/carritos/{id_carrito}/items/{id_item_sel}",
                            )
                        if res_rm["ok"]:
                            st.toast("Ítem eliminado del carrito.")
                            st.rerun()
                        else:
                            st.error(f"Error ({res_rm['status_code']}): {res_rm['data']}")

    st.divider()

    # ---------------------------------------------------------
    # 4. FINALIZAR O CANCELAR COMPRA
    # ---------------------------------------------------------
    st.subheader("Cierre del carrito")
    col_fin, col_can = st.columns(2)

    with col_fin:
        if st.button("Finalizar compra", type="primary", use_container_width=True, disabled=not es_pendiente):
            with st.spinner("Validando disponibilidad, stock y procesando compra..."):
                res_fin = api._request("PATCH", f"/api/carritos/{id_carrito}/finalizar")

            if res_fin["ok"]:
                st.session_state["estado_carrito"] = "Finalizado"
                st.session_state["ultimo_aviso_carrito"] = {
                    "nivel": "success",
                    "mensaje": f"Carrito #{id_carrito} finalizado correctamente. Stock descontado.",
                    "detalle": res_fin["data"],
                }
                st.rerun()
            elif res_fin["status_code"] == 409:
                st.session_state["estado_carrito"] = "Pendiente"
                st.session_state["ultimo_aviso_carrito"] = {
                    "nivel": "warning",
                    "mensaje": (
                        "Compra rechazada (409): el carrito sigue Pendiente y no se descontó stock. "
                        "Se ajustaron o eliminaron ítems no disponibles; revisa el listado actualizado."
                    ),
                    "detalle": res_fin["data"],
                }
                st.rerun()
            else:
                st.session_state["ultimo_aviso_carrito"] = {
                    "nivel": "error",
                    "mensaje": f"No se pudo finalizar el carrito ({res_fin['status_code']}).",
                    "detalle": res_fin["data"],
                }
                st.rerun()

    with col_can:
        if st.button("Cancelar carrito", use_container_width=True, disabled=not es_pendiente):
            with st.spinner("Cancelando carrito..."):
                res_can = api._request("PATCH", f"/api/carritos/{id_carrito}/cancelar")

            if res_can["ok"]:
                st.session_state["estado_carrito"] = "Cancelado"
                st.session_state["ultimo_aviso_carrito"] = {
                    "nivel": "success",
                    "mensaje": f"Carrito #{id_carrito} cancelado correctamente.",
                    "detalle": res_can["data"],
                }
                st.rerun()
            else:
                st.session_state["ultimo_aviso_carrito"] = {
                    "nivel": "error",
                    "mensaje": f"No se pudo cancelar el carrito ({res_can['status_code']}).",
                    "detalle": res_can["data"],
                }
                st.rerun()


render_carrito()