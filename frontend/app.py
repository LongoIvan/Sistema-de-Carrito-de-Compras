import os
import streamlit as st

st.set_page_config(
    page_title="Sistema de Carrito de Compras",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inicializar_estado() -> None:
    """Inicializa claves compartidas entre vistas sin pisar valores existentes."""
    defaults = {
        "api_base_url": os.getenv("API_BASE_URL", "http://127.0.0.1:5000"),
        "id_usuario": 1,
        "id_carrito": None,
        "estado_carrito": "Sin carrito",
    }
    for clave, valor in defaults.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def _render_sidebar_contexto() -> None:
    with st.sidebar:
        st.markdown("### 🛒 Carrito de Compras")
        st.divider()
        id_usuario = st.session_state.get("id_usuario")
        id_carrito = st.session_state.get("id_carrito")
        estado_carrito = st.session_state.get("estado_carrito", "Sin carrito")

        st.write(f"**Usuario activo:** {f'#{id_usuario}' if id_usuario else 'No fijado'}")
        st.write(f"**Carrito activo:** {f'#{id_carrito}' if id_carrito else 'No asignado'}")
        st.write(f"**Estado carrito:** `{estado_carrito}`")

        st.divider()

      

def main() -> None:
    _inicializar_estado()
    _render_sidebar_contexto()
    
    pagina_home = st.Page("pages/home.py", title="home", icon="📊", default=True)
    pagina_usuario = st.Page("pages/usuarios.py", title="Usuarios", icon="👤")
    pagina_producto = st.Page("pages/productos.py", title="Productos", icon="📦")
    pagina_carrito = st.Page("pages/carritos.py", title="Carrito", icon="🛍️")

    nav = st.navigation(
        {
            "General": [pagina_home],
            "Gestión": [pagina_usuario, pagina_producto, pagina_carrito],
        }
    )
    nav.run()


if __name__ == "__main__":
    main()