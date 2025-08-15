import streamlit as st
import plotly.express as px
from scraper import scrape_vahan_data
from analysis import calculate_growth_metrics, filter_data

# Dark theme configuration only
def setup_theme():
    # Set theme to dark always
    st.session_state.theme = 'dark'
    
    # Dark theme colors
    theme_colors = {
        'bg': '#0f172a',
        'card': '#1e293b',
        'text': '#f8fafc',
        'text_secondary': '#94a3b8',
        'border': '#334155',
        'primary': '#60a5fa',
        'positive': '#4ade80',
        'negative': '#f87171',
        'widget_bg': '#1e293b',
        'axis_title': '#f8fafc',
        'axis_text': '#cbd5e1',
        'grid_color': '#334155',
        'expand_icon': '#94a3b8',
        'legend_bg': '#1e293b',
        'legend_text': '#f8fafc'
    }
    
    st.markdown(f"""
    <style>
        /* Base styles */
        .stApp {{
            background-color: {theme_colors['bg']} !important;
        }}
        
        /* Filter section */
        .stExpander {{
            background-color: {theme_colors['card']} !important;
            border: 1px solid {theme_colors['border']} !important;
            border-radius: 8px !important;
        }}
        
        .stExpander .st-emotion-cache-1q7spjk {{
            background-color: {theme_colors['card']} !important;
        }}
        
        .stExpander .st-emotion-cache-1h9us5l {{
            color: {theme_colors['expand_icon']} !important;
        }}
        
        /* Input widgets */
        .stDateInput, .stMultiSelect, .stSelectbox {{
            background-color: {theme_colors['widget_bg']} !important;
            color: {theme_colors['text']} !important;
            border-color: {theme_colors['border']} !important;
        }}
        
        /* Input labels */
        .st-emotion-cache-16idsys p {{
            color: {theme_colors['text']} !important;
        }}
        
        /* Cards */
        .card {{
            background-color: {theme_colors['card']} !important;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid {theme_colors['border']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* Tabs */
        .stTabs [role="tablist"] {{
            background-color: {theme_colors['card']} !important;
            gap: 8px;
            padding: 8px;
            border-radius: 10px;
            border: 1px solid {theme_colors['border']} !important;
        }}
        
        .stTabs [role="tab"] {{
            border-radius: 8px !important;
            padding: 8px 16px;
            transition: all 0.3s ease;
            background-color: transparent !important;
            color: {theme_colors['text_secondary']} !important;
        }}
        
        .stTabs [role="tab"][aria-selected="true"] {{
            background-color: {theme_colors['primary']} !important;
            color: white !important;
            font-weight: 500;
        }}
        
        /* Metrics */
        .metric-card {{
            background-color: {theme_colors['card']} !important;
            border-left: 4px solid {theme_colors['primary']};
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }}
        
        .metric-title {{
            color: {theme_colors['text_secondary']};
            font-size: 0.9rem;
            margin-bottom: 5px;
        }}
        
        .metric-value {{
            color: {theme_colors['text']};
            font-size: 1.5rem;
            font-weight: 600;
        }}
        
        .positive {{
            color: {theme_colors['positive']} !important;
        }}
        
        .negative {{
            color: {theme_colors['negative']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    return theme_colors

def create_themed_chart(data, x, y, color=None, title=None):
    fig = px.line(
        data,
        x=x,
        y=y,
        color=color,
        template='plotly_dark',
        title=title
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color=st.session_state.theme_colors['text'],
        title_font_color=st.session_state.theme_colors['text'],
        xaxis_title_font_color=st.session_state.theme_colors['axis_title'],
        yaxis_title_font_color=st.session_state.theme_colors['axis_title'],
        legend_title_font_color=st.session_state.theme_colors['text_secondary'],
        hoverlabel=dict(
            bgcolor=st.session_state.theme_colors['card'],
            font_color=st.session_state.theme_colors['text']
        )
    )
    
    # Axis styling
    fig.update_xaxes(
        linecolor=st.session_state.theme_colors['border'],
        gridcolor=st.session_state.theme_colors['grid_color'],
        tickfont_color=st.session_state.theme_colors['axis_text']
    )
    
    fig.update_yaxes(
        linecolor=st.session_state.theme_colors['border'],
        gridcolor=st.session_state.theme_colors['grid_color'],
        tickfont_color=st.session_state.theme_colors['axis_text']
    )
    
    return fig

# Filter section
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

def metric_card(title, value, is_positive=None):
    value_class = ""
    if is_positive is not None:
        value_class = "positive" if is_positive else "negative"
    
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value {value_class}">{value}</div>
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
    
    # Modern header with better spacing
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom:24px; border-bottom: 1px solid {st.session_state.theme_colors['border']}; padding-bottom:16px">
        <h1 style="margin:0; color:{st.session_state.theme_colors['text']}">🚗 Vehicle Registration Analytics</h1>
        <div style="margin-left:auto; color:{st.session_state.theme_colors['text_secondary']}; font-size:0.9rem">
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
            st.markdown(metric_card(
                "Total Registrations",
                f"{filtered_data['Registrations'].sum():,}"
            ), unsafe_allow_html=True)
        
        if len(overall_trend) >= 5:
            with cols[1]:
                yoy = ((overall_trend.iloc[-1]['Registrations'] - 
                      overall_trend.iloc[-5]['Registrations']) / 
                      overall_trend.iloc[-5]['Registrations'] * 100)
                st.markdown(metric_card(
                    "YoY Growth",
                    f"{yoy:.1f}%",
                    yoy > 0
                ), unsafe_allow_html=True)
        
        if len(overall_trend) >= 2:
            with cols[2]:
                qoq = ((overall_trend.iloc[-1]['Registrations'] - 
                      overall_trend.iloc[-2]['Registrations']) / 
                      overall_trend.iloc[-2]['Registrations'] * 100)
                st.markdown(metric_card(
                    "QoQ Growth",
                    f"{qoq:.1f}%",
                    qoq > 0
                ), unsafe_allow_html=True)
        
        # Main chart
        st.markdown(f"""
        <div class="card">
            <h3 style="margin-top:0">Registration Trends</h3>
        </div>
        """, unsafe_allow_html=True)
        fig = create_themed_chart(
            overall_trend,
            x='Date',
            y='Registrations',
            title='Registration Trends Over Time'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Vehicle type analysis
        st.markdown(f"""
        <div class="card">
            <h3 style="margin-top:0">Vehicle Type Trends</h3>
        </div>
        """, unsafe_allow_html=True)
        
        vehicle_growth = calculate_growth_metrics(
            filtered_data.groupby(['Date', 'Vehicle Type'])['Registrations'].sum().reset_index(),
            ['Vehicle Type']
        )
        
        fig = create_themed_chart(
            vehicle_growth,
            x='Date',
            y='Registrations',
            color='Vehicle Type',
            title='Vehicle Type Registration Trends'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Manufacturer analysis
        st.markdown(f"""
        <div class="card">
            <h3 style="margin-top:0">Top Manufacturers</h3>
        </div>
        """, unsafe_allow_html=True)
        
        top_manufacturers = filtered_data.groupby('Manufacturer')['Registrations'].sum().nlargest(5).index.tolist()
        fig = create_themed_chart(
            filtered_data[filtered_data['Manufacturer'].isin(top_manufacturers)],
            x='Date',
            y='Registrations',
            color='Manufacturer',
            title='Top 5 Manufacturers by Registrations'
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()