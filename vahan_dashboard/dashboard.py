import streamlit as st
import plotly.express as px
from scraper import scrape_vahan_data
from analysis import calculate_growth_metrics, filter_data

# Theme configuration
def setup_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Theme toggle with custom styling
    col1, col2 = st.columns([6,1])
    with col2:
        theme_toggle = st.toggle(
            '🌓', 
            value=st.session_state.theme == 'dark',
            key='theme_toggle',
            help='Toggle dark/light mode'
        )
        st.session_state.theme = 'dark' if theme_toggle else 'light'

    # Apply theme colors
    theme_colors = {
        'light': {
            'bg': '#ffffff',
            'card': '#f8f9fa',
            'text': '#2c3e50',
            'border': '#dee2e6'
        },
        'dark': {
            'bg': '#0e1117',
            'card': '#1e2130',
            'text': '#f5f5f5',
            'border': '#2a3042'
        }
    }
    
    st.markdown(f"""
    <style>
        /* Base styles */
        .main {{
            background-color: {theme_colors[st.session_state.theme]['bg']} !important;
            color: {theme_colors[st.session_state.theme]['text']} !important;
        }}
        
        /* Cards */
        .card {{
            background-color: {theme_colors[st.session_state.theme]['card']} !important;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid {theme_colors[st.session_state.theme]['border']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* Tabs */
        .stTabs [role="tablist"] {{
            background-color: {theme_colors[st.session_state.theme]['card']} !important;
            gap: 8px;
            padding: 8px;
            border-radius: 10px;
        }}
        
        .stTabs [role="tab"] {{
            border-radius: 8px !important;
            padding: 8px 16px;
            transition: all 0.3s ease;
            background-color: transparent !important;
        }}
        
        .stTabs [role="tab"][aria-selected="true"] {{
            background-color: {theme_colors['dark']['card'] if st.session_state.theme == 'light' else theme_colors['light']['card']} !important;
            color: {theme_colors['dark']['text'] if st.session_state.theme == 'light' else theme_colors['light']['text']} !important;
        }}
        
        /* Input widgets */
        .stDateInput, .stMultiSelect {{
            background-color: {theme_colors[st.session_state.theme]['card']} !important;
            border-color: {theme_colors[st.session_state.theme]['border']} !important;
        }}
        
        /* Metrics */
        .stMetric {{
            background-color: {theme_colors[st.session_state.theme]['card']} !important;
            border-left: 3px solid #4e79a7;
            padding: 15px;
            border-radius: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)

    return theme_colors[st.session_state.theme]

# Filter section (now at top)
def render_filters(df):
    with st.container():
        st.markdown("### 🔍 Filter Data")
        with st.expander("Filters", expanded=True):
            cols = st.columns(3)
            
            with cols[0]:
                min_date = df['Date'].min().to_pydatetime()
                max_date = df['Date'].max().to_pydatetime()
                date_range = st.date_input(
                    "Date Range",
                    [min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
            
            with cols[1]:
                vehicle_types = st.multiselect(
                    "Vehicle Type",
                    options=df['Vehicle Type'].unique(),
                    default=df['Vehicle Type'].unique()
                )
            
            with cols[2]:
                manufacturers = st.multiselect(
                    "Manufacturer",
                    options=df['Manufacturer'].unique(),
                    default=df['Manufacturer'].unique()
                )
                
    return date_range, vehicle_types, manufacturers

# Modern card component
def card(title, content):
    return f"""
    <div class="card">
        <h3 style="margin-top:0;color:{st.session_state.theme_colors['text']}">{title}</h3>
        {content}
    </div>
    """

def main():
    # Setup theme and colors
    st.session_state.theme_colors = setup_theme()
    
    # Page config
    st.set_page_config(
        page_title="Vehicle Analytics Dashboard",
        layout="wide",
        page_icon="🚗"
    )
    
    # Modern header
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom:16px">
        <h1 style="margin:0; color:{st.session_state.theme_colors['text']}">🚗 Vehicle Registration Analytics</h1>
        <div style="margin-left:auto; font-size:smaller">
            Investor Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    data = scrape_vahan_data()
    if data is None:
        st.error("Failed to load data")
        return
    
    # Filters at top
    date_range, vehicle_types, manufacturers = render_filters(data)
    filtered_data = filter_data(data, date_range, vehicle_types, manufacturers)
    
    # Dashboard tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Overview Dashboard", 
        "🚦 Vehicle Insights", 
        "🏭 Manufacturer Analysis"
    ])
    
    with tab1:
        # Overview metrics
        overall_trend = filtered_data.groupby('Date')['Registrations'].sum().reset_index()
        
        cols = st.columns(3)
        with cols[0]:
            st.markdown(card(
                "Total Registrations",
                f"<h2 style='color:{st.session_state.theme_colors['text']}'>{filtered_data['Registrations'].sum():,}</h2>"
            ), unsafe_allow_html=True)
        
        if len(overall_trend) >= 5:
            with cols[1]:
                yoy = ((overall_trend.iloc[-1]['Registrations'] - 
                      overall_trend.iloc[-5]['Registrations']) / 
                      overall_trend.iloc[-5]['Registrations'] * 100)
                st.markdown(card(
                    "YoY Growth",
                    f"<h2 style='color:{'#2ecc71' if yoy > 0 else '#e74c3c'}'>{yoy:.1f}%</h2>"
                ), unsafe_allow_html=True)
        
        if len(overall_trend) >= 2:
            with cols[2]:
                qoq = ((overall_trend.iloc[-1]['Registrations'] - 
                      overall_trend.iloc[-2]['Registrations']) / 
                      overall_trend.iloc[-2]['Registrations'] * 100)
                st.markdown(card(
                    "QoQ Growth",
                    f"<h2 style='color:{'#2ecc71' if qoq > 0 else '#e74c3c'}'>{qoq:.1f}%</h2>"
                ), unsafe_allow_html=True)
        
        # Main chart
        st.markdown(card(
            "Registration Trends",
            ""
        ), unsafe_allow_html=True)
        fig = px.line(
            overall_trend, 
            x='Date', 
            y='Registrations',
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': st.session_state.theme_colors['text']}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Vehicle type analysis
        st.markdown(card(
            "Vehicle Type Trends",
            ""
        ), unsafe_allow_html=True)
        
        vehicle_growth = calculate_growth_metrics(
            filtered_data.groupby(['Date', 'Vehicle Type'])['Registrations'].sum().reset_index(),
            ['Vehicle Type']
        )
        
        fig = px.line(
            vehicle_growth, 
            x='Date', 
            y='Registrations', 
            color='Vehicle Type',
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': st.session_state.theme_colors['text']}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Manufacturer analysis
        st.markdown(card(
            "Top Manufacturers",
            ""
        ), unsafe_allow_html=True)
        
        top_manufacturers = filtered_data.groupby('Manufacturer')['Registrations'].sum().nlargest(5).index.tolist()
        fig = px.line(
            filtered_data[filtered_data['Manufacturer'].isin(top_manufacturers)],
            x='Date', 
            y='Registrations', 
            color='Manufacturer',
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': st.session_state.theme_colors['text']}
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()