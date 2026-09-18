# Force reload 4
import streamlit as st
import pandas as pd
import datetime
import time
import streamlit.components.v1 as components
from modulo_pos import POSLogic, CATALOGO
from modulo_dashboard import render_dashboard

st.set_page_config(page_title="Brighton's Supermarket POS", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Supermarket look
st.markdown("""
<style>
.pos-header {
    background-color: #1e3a8a;
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 2rem;
    font-family: 'Arial', sans-serif;
}
.ticket-container {
    background-color: #ffffe0;
    padding: 20px;
    border: 2px dashed #999;
    font-family: 'Courier New', Courier, monospace;
    color: #000;
    min-height: 500px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
}
.ticket-header {
    text-align: center;
    margin-bottom: 15px;
}
.item-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 1.1em;
}
.total-row {
    display: flex;
    justify-content: space-between;
    font-weight: bold;
    font-size: 1.5em;
    margin-top: 15px;
    padding-top: 10px;
    border-top: 2px dashed #000;
}
</style>
""", unsafe_allow_html=True)

if "pos_logic" not in st.session_state:
    st.session_state.pos_logic = POSLogic()

tab_pos, tab_dashboard = st.tabs(["🛒 Caja Registradora", "📊 Panel de Gerencia"])

with tab_pos:
    st.markdown('<div class="pos-header"><h1>🛒 Brighton\'s Supermarket POS</h1><p>Caja: 01 | Cajero: Turno Mañana</p></div>', unsafe_allow_html=True)
    
    col_scanner, col_ticket = st.columns([6, 4])
    
    with col_scanner:
        st.markdown("### 📷 Escáner Inteligente (Motor: Web AI)")
        run_camera = st.toggle("Activar Cinta / Mostrar Cámara", value=False)
        
        if run_camera:
            # Declare the custom component
            scanner_component = components.declare_component("scanner", path="scanner_component")
            scan_event = scanner_component(key="web_scanner")
            
            # Process the scanned label
            if scan_event and scan_event.get("ts") != st.session_state.get('last_scanned_ts'):
                st.session_state.last_scanned_ts = scan_event.get("ts")
                label = scan_event.get("label")
                if label in CATALOGO:
                    st.session_state.pos_logic.add_item_to_ticket(label, source="Visión IA")
        else:
            st.info("La cámara está apagada. Activa el interruptor arriba para escanear.")
            st.session_state.last_scanned_ts = None
        
        st.markdown("---")
        st.markdown("### 🔢 Teclado PLU (Ingreso Manual)")
        
        cols = st.columns(3)
        col_idx = 0
        for product_name in CATALOGO.keys():
            with cols[col_idx % 3]:
                if st.button(f"{product_name}\n${CATALOGO[product_name]['price']:.2f}", use_container_width=True):
                    st.session_state.pos_logic.add_item_to_ticket(product_name, source="Botón Manual")
            col_idx += 1
            
    with col_ticket:
        st.markdown("<br>", unsafe_allow_html=True)
        
        ticket = st.session_state.pos_logic.get_current_ticket()
        total = st.session_state.pos_logic.get_ticket_total()
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Call custom ticket component
        ticket_comp = components.declare_component("ticket", path="ticket_component")
        del_event = ticket_comp(key="ticket_view", items=ticket, total=total, date_str=now_str)
        
        if del_event and del_event.get("ts") != st.session_state.get('last_deleted_ts'):
            st.session_state.last_deleted_ts = del_event.get("ts")
            st.session_state.pos_logic.remove_item(del_event.get("index"))
            # Re-render immediately
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💳 COBRAR Y EMITIR TICKET", type="primary", use_container_width=True, key="btn_cobrar"):
            if st.session_state.pos_logic.checkout():
                st.success("¡Venta registrada exitosamente! El ticket se ha guardado.")
                st.session_state.last_scanned_ts = None
                st.session_state.last_deleted_ts = None
                time.sleep(1)
                st.rerun()
            else:
                st.warning("El carrito está vacío. Escanee productos primero.")

with tab_dashboard:
    render_dashboard()
