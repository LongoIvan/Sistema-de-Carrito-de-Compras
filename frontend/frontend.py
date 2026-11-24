import streamlit as st
# from fronend.pages.productos import
# from fronend.pages.home import
# from fronend.pages.usaurios import
# from fronend.pages.carritos import

st.set_page_config(page_title = "Sistema de gestion" Layout = "wide")

st.title("Sistema de gestion")

st.sidebar.title("Menu navegacion")

option = st.sidebar.radio("Seleccionar opcion", ["Home", "Usuarios", "Productos", "Carrito"])

#if option == "Home":
#    mostar.home()
#elif option == "Usuarios":
#    mostrar.usuarios()
