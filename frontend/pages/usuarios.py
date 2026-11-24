import streamlit as st
from services import api


def _validar_nombre_local(nombre: str) -> str | None:
    limpio = nombre.strip()
    if len(limpio) <= 3 or len(limpio) >= 50:
        return "El nombre debe tener entre 4 y 49 caracteres."
    if not limpio.replace(" ", "").isalpha():
        return "El nombre solo puede contener letras y espacios."
    return None


def _validar_mail_local(mail: str) -> str | None:
    limpio = mail.strip().lower()
    if len(limpio) <= 5 or len(limpio) >= 50:
        return "El mail debe tener entre 6 y 49 caracteres."
    if limpio.count("@") != 1 or any(c.isspace() for c in limpio):
        return "Formato de mail inválido."
    parte_local, dominio = limpio.split("@")
    if not parte_local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        return "Formato de mail inválido."
    return None


def _validar_contrasenia_local(contrasenia: str) -> str | None:
    if len(contrasenia) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not any(c.isupper() for c in contrasenia):
        return "La contraseña debe contener al menos una mayúscula."
    return None


@st.dialog("Confirmar eliminación de usuario")
def _dialog_eliminar_usuario(id_usuario: int) -> None:
    st.warning(
        f"¿Seguro que querés eliminar el usuario #{id_usuario}? "
        "Si tiene carritos asociados, el servidor devolverá 409."
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sí, eliminar", type="primary", use_container_width=True):
            with st.spinner("Eliminando usuario..."):
                res = api.eliminar_usuario(id_usuario)
            if res["ok"]:
                if st.session_state.get("id_usuario") == id_usuario:
                    st.session_state.pop("id_usuario", None)
                st.success(f"Usuario #{id_usuario} eliminado correctamente.")
                st.rerun()
            elif res["status_code"] == 409:
                st.error(f"Conflicto (409): {res['data'].get('error', 'No se puede eliminar un usuario con carritos asociados')}")
            else:
                st.error(f"Error ({res['status_code']}): {res['data']}")
    with c2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()


def render_usuario() -> None:
    st.title("Gestión de Usuarios")

    id_actual = int(st.session_state.get("id_usuario") or 1)

    # ---------------------------------------------------------
    # 1. USUARIO ACTIVO EN SESIÓN (SIN LOGIN)
    # ---------------------------------------------------------
    st.subheader("Usuario activo en sesión")
    col_id, col_fijar = st.columns([2, 1])
    with col_id:
        id_usuario = int(
            st.number_input("ID de usuario", min_value=1, step=1, value=id_actual)
        )
    with col_fijar:
        st.write("")
        st.write("")
        if st.button("Fijar ID en sesión", type="primary", use_container_width=True):
            st.session_state["id_usuario"] = id_usuario
            st.toast(f"Usuario activo: #{id_usuario}")
            st.rerun()

    st.divider()

    # ---------------------------------------------------------
    # 2. CREAR USUARIO (POST /usuario)
    # ---------------------------------------------------------
    st.subheader("Crear nuevo usuario")
    with st.form("form_crear_usuario", clear_on_submit=True):
        nombre = st.text_input("Nombre", placeholder="Juan Perez")
        mail = st.text_input("Correo electrónico", placeholder="juan@gmail.com")
        contrasenia = st.text_input(
            "Contraseña",
            type="password",
            help="Mínimo 8 caracteres y al menos una letra mayúscula.",
        )
        enviar = st.form_submit_button("Crear usuario")

        if enviar:
            err = (
                _validar_nombre_local(nombre)
                or _validar_mail_local(mail)
                or _validar_contrasenia_local(contrasenia)
            )
            if err:
                st.warning(err)
            else:
                with st.spinner("Registrando usuario..."):
                    res = api.crear_usuario(
                        nombre=nombre.strip(),
                        mail=mail.strip().lower(),
                        contrasenia=contrasenia,
                    )
                if res["ok"]:
                    st.success("Usuario creado correctamente.")
                    st.json(res["data"])
                elif res["status_code"] == 409:
                    st.error(f"Conflicto (409): {res['data'].get('error', 'El mail ya esta registrado')}")
                else:
                    st.error(f"Error ({res['status_code']}): {res['data']}")

    st.divider()

    # ---------------------------------------------------------
    # 3. CONSULTAR USUARIO (GET /api/usuario/<id>/completo y /usuario/<id>/...)
    # ---------------------------------------------------------
    st.subheader(f"Consultar usuario #{id_usuario}")
    opcion_consulta = st.selectbox(
        "Endpoint a consultar",
        options=[
            "Completo (/api/usuario/<id>/completo)",
            "Solo ID (/usuario/<id>)",
            "Solo nombre (/usuario/<id>/nombre)",
            "Solo mail (/usuario/<id>/mail)",
            "Solo rol (/usuario/<id>/rol)",
        ],
    )

    if st.button("Consultar"):
        with st.spinner("Consultando usuario..."):
            if opcion_consulta.startswith("Completo"):
                res = api._request("GET", f"/api/usuario/{id_usuario}/completo")
            elif opcion_consulta.startswith("Solo ID"):
                res = api.obtener_usuario(id_usuario)
            elif opcion_consulta.startswith("Solo nombre"):
                res = api.obtener_usuario_nombre(id_usuario)
            elif opcion_consulta.startswith("Solo mail"):
                res = api.obtener_usuario_mail(id_usuario)
            else:
                res = api.obtener_usuario_rol(id_usuario)

        if res["ok"]:
            st.json(res["data"])
        else:
            st.error(f"Error ({res['status_code']}): {res['data']}")

    st.divider()

    # ---------------------------------------------------------
    # 4. MODIFICAR DATOS (PATCH /usuario/<id>/nombre | mail | contrasenia)
    # ---------------------------------------------------------
    st.subheader(f"Modificar datos del usuario #{id_usuario}")
    t_nom, t_mail, t_pass = st.tabs(["Nombre", "Mail", "Contraseña"])

    with t_nom:
        with st.form("form_mod_nombre"):
            nuevo_nombre = st.text_input("Nuevo nombre", placeholder="Juan Garcia")
            if st.form_submit_button("Guardar nombre"):
                err = _validar_nombre_local(nuevo_nombre)
                if err:
                    st.warning(err)
                else:
                    with st.spinner("Actualizando nombre..."):
                        res = api.actualizar_usuario_nombre(id_usuario, nuevo_nombre.strip())
                    if res["ok"]:
                        st.success("Nombre actualizado.")
                        st.json(res["data"])
                    else:
                        st.error(f"Error ({res['status_code']}): {res['data']}")

    with t_mail:
        with st.form("form_mod_mail"):
            nuevo_mail = st.text_input("Nuevo mail", placeholder="nuevo@gmail.com")
            if st.form_submit_button("Guardar mail"):
                err = _validar_mail_local(nuevo_mail)
                if err:
                    st.warning(err)
                else:
                    with st.spinner("Actualizando mail..."):
                        res = api.actualizar_usuario_mail(id_usuario, nuevo_mail.strip().lower())
                    if res["ok"]:
                        st.success("Mail actualizado.")
                        st.json(res["data"])
                    elif res["status_code"] == 409:
                        st.error(f"Conflicto (409): {res['data'].get('error', 'El mail ya esta registrado')}")
                    else:
                        st.error(f"Error ({res['status_code']}): {res['data']}")

    with t_pass:
        with st.form("form_mod_pass", clear_on_submit=True):
            nueva_pass = st.text_input("Nueva contraseña", type="password")
            if st.form_submit_button("Guardar contraseña"):
                err = _validar_contrasenia_local(nueva_pass)
                if err:
                    st.warning(err)
                else:
                    with st.spinner("Actualizando contraseña..."):
                        res = api.actualizar_usuario_contrasenia(id_usuario, nueva_pass)
                    if res["ok"]:
                        st.success("Contraseña actualizada.")
                        st.json(res["data"])
                    else:
                        st.error(f"Error ({res['status_code']}): {res['data']}")

    st.divider()

    # ---------------------------------------------------------
    # 5. ELIMINAR USUARIO (DELETE /usuario/<id>)
    # ---------------------------------------------------------
    st.subheader(f"Eliminar usuario #{id_usuario}")
    if st.button("Eliminar usuario"):
        _dialog_eliminar_usuario(id_usuario)


render_usuario()