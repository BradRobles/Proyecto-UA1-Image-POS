import pandas as pd
import streamlit as st
import os
import plotly.express as px

DB_PATH = "base_datos/ventas.csv"

def render_dashboard():
    st.markdown("<h2 style='text-align: center; color: #ffffff; padding-bottom: 20px;'>📊 Panel de Inteligencia de Negocios</h2>", unsafe_allow_html=True)
    
    if not os.path.exists(DB_PATH):
        st.info("No hay datos de ventas disponibles aún. Realice algunas ventas en la caja registradora.")
        return
        
    try:
        df = pd.read_csv(DB_PATH)
    except Exception as e:
        st.error(f"Error al leer la base de datos: {e}")
        return
        
    if df.empty:
        st.info("La base de datos de ventas está vacía.")
        return

    # Preparar datos
    df['Price'] = pd.to_numeric(df['Price'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Fecha'] = df['Timestamp'].dt.date
    df['Hora'] = df['Timestamp'].dt.strftime('%H:00')
    
    # Mapeo de Categorías (Estratégico)
    categoria_map = {
        "Pollo": "Alimentos",
        "Tortuga": "Juguetes Infantiles",
        "Cohete": "Juguetes Infantiles",
        "Cartas pokemon": "Coleccionables",
        "Sylveon": "Coleccionables"
    }
    df['Categoria'] = df['ProductName'].map(categoria_map).fillna("Otros")
    
    # Filtro de Fechas Global
    fechas_disponibles = sorted(df['Fecha'].unique(), reverse=True)
    opciones_fecha = ["Histórico Completo"] + [f.strftime("%Y-%m-%d") for f in fechas_disponibles]
    
    col_filt, _ = st.columns([1, 3])
    with col_filt:
        fecha_seleccionada = st.selectbox("📅 Filtrar por Día de Operación", options=opciones_fecha)
        
    if fecha_seleccionada != "Histórico Completo":
        df = df[df['Fecha'].astype(str) == fecha_seleccionada]

    if df.empty:
        st.warning("No hay datos para la fecha seleccionada.")
        return
        
    st.markdown("---")
    
    # ==========================================
    # NIVEL 1: INFORMACIÓN OPERATIVA
    # ==========================================
    st.markdown("<h3 style='color: #3b82f6;'>Nivel 1: Información Operativa (Tiempo Real)</h3>", unsafe_allow_html=True)
    st.caption("Uso: Cajeros y Supervisores de turno. Toma de decisiones inmediatas sobre transacciones.")
    
    total_sales = df['Price'].sum()
    total_items = len(df)
    unique_tickets = df['TicketID'].nunique()
    ticket_promedio = total_sales / unique_tickets if unique_tickets > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="💰 Ingresos del Día", value=f"${total_sales:,.2f}")
    with col2:
        st.metric(label="🛍️ Productos Escaneados", value=total_items)
    with col3:
        st.metric(label="🧾 Tickets Activos", value=unique_tickets)
    with col4:
        st.metric(label="📈 Ticket Promedio", value=f"${ticket_promedio:,.2f}")

    with st.expander("Ver Registro Detallado de Transacciones (Log Operativo)"):
        df_display = df.sort_values('Timestamp', ascending=False)
        st.dataframe(
            df_display[['Timestamp', 'TicketID', 'ProductName', 'Price', 'ScanSource']],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ==========================================
    # NIVEL 2: INFORMACIÓN TÁCTICA
    # ==========================================
    st.markdown("<h3 style='color: #10b981;'>Nivel 2: Información Táctica (Mediano Plazo)</h3>", unsafe_allow_html=True)
    st.caption("Uso: Gerentes de tienda. Decisiones sobre horarios de personal y reabastecimiento de inventario.")
    
    col_tac1, col_tac2 = st.columns(2)
    
    with col_tac1:
        # Táctico: Control de flujo de clientes
        hourly_sales = df.groupby('Hora').agg(Ingresos=('Price', 'sum'), Clientes=('TicketID', 'nunique')).reset_index()
        fig_time = px.line(hourly_sales, x='Hora', y='Ingresos', markers=True,
                           title="Flujo de Ingresos por Hora (Staffing)")
        fig_time.update_traces(line_color='#10b981', line_width=3, marker=dict(size=8))
        fig_time.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=300)
        st.plotly_chart(fig_time, use_container_width=True)
        
    with col_tac2:
        # Táctico: Control de stock individual
        prod_sales = df.groupby('ProductName')['Price'].sum().reset_index().sort_values(by='Price', ascending=True)
        fig_prod = px.bar(prod_sales, x='Price', y='ProductName', orientation='h', 
                          color='Price', color_continuous_scale='Greens',
                          title="Productos de Mayor Rotación (Inventario)")
        fig_prod.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0), height=300)
        st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ==========================================
    # NIVEL 3: INFORMACIÓN ESTRATÉGICA
    # ==========================================
    st.markdown("<h3 style='color: #8b5cf6;'>Nivel 3: Información Estratégica (Largo Plazo)</h3>", unsafe_allow_html=True)
    st.caption("Uso: Directivos y Dueños. Decisiones sobre dirección del negocio, riesgos y diversificación de catálogo.")
    
    col_est1, col_est2 = st.columns(2)
    
    with col_est1:
        # Estratégico: Enfoque de negocio (Categorías)
        cat_sales = df.groupby('Categoria')['Price'].sum().reset_index()
        fig_cat = px.pie(cat_sales, names='Categoria', values='Price', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel,
                         title="Concentración del Negocio por Categoría")
        fig_cat.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=350)
        fig_cat.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_est2:
        # Estratégico: Análisis de Pareto (Riesgo de dependencia)
        import plotly.graph_objects as go
        
        pareto_df = df.groupby('ProductName')['Price'].sum().reset_index().sort_values(by='Price', ascending=False)
        pareto_df['Porcentaje'] = (pareto_df['Price'] / pareto_df['Price'].sum()) * 100
        pareto_df['Acumulado'] = pareto_df['Porcentaje'].cumsum()
        
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=pareto_df['ProductName'], y=pareto_df['Price'], name='Ingresos', marker_color='#8b5cf6'))
        fig_pareto.add_trace(go.Scatter(x=pareto_df['ProductName'], y=pareto_df['Acumulado'], name='% Acumulado', 
                                        yaxis='y2', line=dict(color='#ef4444', width=3)))
        
        fig_pareto.update_layout(
            title="Análisis de Pareto (Dependencia de Catálogo)",
            yaxis=dict(title='Ingresos ($)'),
            yaxis2=dict(title='Porcentaje Acumulado (%)', overlaying='y', side='right', range=[0, 105]),
            margin=dict(l=0, r=0, t=40, b=0),
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig_pareto, use_container_width=True)
