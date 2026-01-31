import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import wbgapi as wb

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Indian Economic Monitor", page_icon="🇮🇳", layout="wide")

st.title("🇮🇳 Indian Economic Policy Monitor")
st.markdown("""
**Built by: [Your Name]** | CSE Graduate & Policy Aspirant  
*This dashboard aggregates real-time development data from the World Bank and trade data from the RBI to assist in macroeconomic monitoring.*
""")
st.divider()

# --- SIDEBAR NAVIGATION ---
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Module:", ["Real-Time Phillips Curve", "EXIM Trade Pulse"])

# --- FUNCTION 1: PHILLIPS CURVE (World Bank) ---
def real_phillips_curve():
    st.header("📈 Macro-Stability: The Phillips Curve Analysis")
    
    # Introduction and Explanation
    st.markdown("""
    ### What is the Phillips Curve?
    The **Phillips Curve** is a fundamental concept in macroeconomics that illustrates the inverse relationship 
    between inflation and unemployment. Named after economist A.W. Phillips, it suggests that:
    
    - **Lower unemployment** → **Higher inflation** (economy is "hot")
    - **Higher unemployment** → **Lower inflation** (economy is "cool")
    
    This relationship helps policymakers balance economic growth with price stability.
    """)
    
    st.info("""
    **💡 How to Read This Chart:**
    - Each **point** represents a specific year (2000-2023)
    - **X-axis:** Unemployment rate (% of labor force)
    - **Y-axis:** Inflation rate (% change in Consumer Price Index)
    - **Red dashed line:** Statistical trend showing the overall relationship
    - **Hover** over points to see the exact year and values
    """)
    
    # 1. Fetch Data
    with st.spinner('Querying World Bank API (Live Data)...'):
        # Indicators: Inflation (FP.CPI.TOTL.ZG), Unemployment (SL.UEM.TOTL.ZS)
        indicators = {'FP.CPI.TOTL.ZG': 'Inflation', 'SL.UEM.TOTL.ZS': 'Unemployment'}
        df_list = []
        
        # We fetch data starting from 2000 to ensure better data quality
        for ind, name in indicators.items():
            try:
                d = wb.data.DataFrame(ind, 'IND', time=range(2000, 2024)).T
                d.columns = [name]
                df_list.append(d)
            except:
                st.error(f"Could not retrieve data for {name}")
                return
        
        # Data Cleaning
        if not df_list:
            st.error("API returned no data. Please check internet connection.")
            return

        final_df = pd.concat(df_list, axis=1)
        # Cleaning the index (removing 'YR' prefix returned by API)
        final_df.index = final_df.index.astype(str).str.replace('YR', '', regex=False).astype(int)
        final_df.reset_index(inplace=True)
        final_df.rename(columns={'index': 'Year'}, inplace=True)

    # 2. Visualization
    fig = px.scatter(
        final_df, 
        x="Unemployment", 
        y="Inflation", 
        hover_data=['Year'],
        color="Year",
        size_max=15,
        title="Phillips Curve: India (2000-2023)",
        labels={"Unemployment": "Unemployment Rate (%)", "Inflation": "Inflation (CPI %)"}
    )
    
    # Add manual trendline using numpy polyfit
    import numpy as np
    # Remove NaN values for trendline calculation
    clean_df = final_df.dropna(subset=['Unemployment', 'Inflation'])
    if len(clean_df) > 1:
        z = np.polyfit(clean_df['Unemployment'], clean_df['Inflation'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(clean_df['Unemployment'].min(), clean_df['Unemployment'].max(), 100)
        y_trend = p(x_trend)
        
        fig.add_scatter(
            x=x_trend, 
            y=y_trend, 
            mode='lines',
            name='Trend Line',
            line=dict(color='red', width=2, dash='dash')
        )
    
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    fig.update_layout(
        height=600,
        font=dict(size=14),
        hovermode='closest',
        plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. Key Insights
    st.markdown("### 🔍 Key Insights from India's Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 What the Data Shows:**
        - India's Phillips Curve shows a **weaker negative correlation** than classical theory predicts
        - Post-2015 data reveals a **flattening trend**, indicating structural changes in the economy
        - Inflation spikes (2008-2010) occurred despite varying unemployment levels
        """)
    
    with col2:
        st.markdown("""
        **🎯 Economic Interpretation:**
        - **Supply-side factors** (food, fuel prices) dominate inflation in India
        - **Structural unemployment** persists regardless of inflation levels
        - Traditional demand-management policies have limited effectiveness
        """)
    
    # 3.5 Policy Implications
    st.warning("""
    **🏛️ Policy Implications for India:**
    
    1. **Monetary Policy Limitations:** The Reserve Bank of India's interest rate adjustments alone may not 
       effectively control inflation when it's driven by supply shocks (oil prices, agricultural output).
    
    2. **Supply-Side Interventions Needed:** Focus on:
       - Agricultural productivity improvements
       - Energy security and renewable sources
       - Infrastructure development to reduce logistics costs
    
    3. **Structural Reforms:** Address skill mismatches and labor market rigidities to reduce structural unemployment.
    """)
    
    # 3.7 Show the data table
    with st.expander("📋 View Raw Data Table"):
        st.dataframe(final_df.sort_values('Year', ascending=False), use_container_width=True)

    # 4. DATA SOURCES
    with st.expander("📊 View Data Sources (Click to Open)"):
        st.markdown("""
        **Data fetched via World Bank API (wbgapi):**
        1.  **Inflation (Consumer Prices):** [World Bank Indicator FP.CPI.TOTL.ZG](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=IN)
        2.  **Unemployment (Total %):** [World Bank Indicator SL.UEM.TOTL.ZS](https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS?locations=IN)
        """)

# --- FUNCTION 2: EXIM PULSE (RBI) ---
def real_exim_pulse():
    st.header("🚢 Trade Balance: Import/Export Composition")
    
    # Introduction and Explanation
    st.markdown("""
    ### Understanding India's Trade Flows
    
    This **Sankey diagram** visualizes India's major import and export categories, showing the flow of goods 
    in and out of the country. Trade balance is a critical indicator of economic health and competitiveness.
    
    **Key Concepts:**
    - **Imports** (🔴 Red): Goods India purchases from other countries
    - **Exports** (🟢 Green): Goods India sells to other countries
    - **Trade Deficit**: When imports exceed exports (money flowing out)
    - **Trade Surplus**: When exports exceed imports (money flowing in)
    """)
    
    st.info("""
    **💡 How to Read This Sankey Diagram:**
    - **Left side (Red):** Import categories flowing INTO India
    - **Center (Blue):** India 🇮🇳
    - **Right side (Green):** Export categories flowing FROM India
    - **Width of flows:** Proportional to trade value (in USD Billions)
    - **Hover** over flows to see exact values
    """)

    # 1. Load Data
    try:
        df = pd.read_csv('rbi_data.csv')
    except FileNotFoundError:
        st.error("⚠️ Data file not found. Please ensure 'rbi_data.csv' is in the folder.")
        return

    # 2. Process Data for Sankey with improved visuals
    # Separate imports and exports
    imports = df[df['Type'] == 'Import'].copy()
    exports = df[df['Type'] == 'Export'].copy()
    
    # Create labels with values for clarity
    import_labels = [f"{row['Category']}" for _, row in imports.iterrows()]
    export_labels = [f"{row['Category']}" for _, row in exports.iterrows()]
    
    all_labels = import_labels + ["🇮🇳 INDIA"] + export_labels
    
    sources = []
    targets = []
    values = []
    link_colors = []
    
    india_index = len(import_labels)
    
    # Import flows (to India)
    for i, (_, row) in enumerate(imports.iterrows()):
        sources.append(i)
        targets.append(india_index)
        values.append(row['Value'])
        link_colors.append("rgba(239, 68, 68, 0.4)")  # Red for imports
    
    # Export flows (from India)
    for i, (_, row) in enumerate(exports.iterrows()):
        sources.append(india_index)
        targets.append(india_index + 1 + i)
        values.append(row['Value'])
        link_colors.append("rgba(34, 197, 94, 0.4)")  # Green for exports
    
    # Create node colors
    node_colors = [
        "#dc2626" for _ in import_labels  # Red for import nodes
    ] + [
        "#1e40af"  # Blue for India
    ] + [
        "#16a34a" for _ in export_labels  # Green for export nodes
    ]

    # 3. Plot Enhanced Sankey
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 20,
          thickness = 25,
          line = dict(color = "white", width = 2),
          label = all_labels,
          color = node_colors,
          customdata = all_labels,
          hovertemplate='%{customdata}<br />Total: $%{value:.1f}B<extra></extra>'
        ),
        link = dict(
          source = sources,
          target = targets,
          value = values,
          color = link_colors,
          hovertemplate='%{value:.1f} USD Billion<extra></extra>'
      ))])
    
    fig.update_layout(
        title=dict(
            text="India's Trade Composition (USD Billion)<br><sub>🔴 Red = Imports | 🟢 Green = Exports</sub>",
            font=dict(size=20)
        ),
        font=dict(size=14, family="Arial"),
        height=700,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 3.5 Add summary statistics
    col1, col2, col3 = st.columns(3)
    total_imports = imports['Value'].sum()
    total_exports = exports['Value'].sum()
    trade_deficit = total_imports - total_exports
    
    with col1:
        st.metric("Total Imports", f"${total_imports:.1f}B", delta=None)
    with col2:
        st.metric("Total Exports", f"${total_exports:.1f}B", delta=None)
    with col3:
        st.metric("Trade Deficit", f"${trade_deficit:.1f}B", delta=f"-${trade_deficit:.1f}B", delta_color="inverse")
    
    # 4. Detailed Analysis
    st.markdown("### 🔍 Trade Composition Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔴 Top Import Categories:**")
        top_imports = imports.nlargest(3, 'Value')
        for idx, row in top_imports.iterrows():
            st.markdown(f"- **{row['Category']}**: ${row['Value']:.1f}B")
        st.caption("These represent India's key dependencies")
    
    with col2:
        st.markdown("**🟢 Top Export Categories:**")
        top_exports = exports.nlargest(3, 'Value')
        for idx, row in top_exports.iterrows():
            st.markdown(f"- **{row['Category']}**: ${row['Value']:.1f}B")
        st.caption("These represent India's competitive strengths")
    
    # 4.5 Key Observations
    st.markdown("### 📊 Key Observations")
    
    st.success("""
    **✅ Strengths:**
    - **Engineering Goods** ($107B) showcase India's manufacturing capabilities
    - **Petroleum Products** ($94.5B) exports demonstrate refining capacity
    - **Gems & Jewellery** ($38B) maintains traditional export strength
    """)
    
    st.error("""
    **⚠️ Vulnerabilities:**
    - **Crude Oil** ($162.2B) imports create massive trade deficit and currency pressure
    - **Electronic Goods** show dual nature: $73.5B imports vs $23.5B exports (net importer)
    - **Gold** ($35B) imports for cultural/investment demand strain foreign reserves
    """)
    
    # 4.7 Policy Implications
    st.warning("""
    **🏛️ Policy Implications & Strategic Priorities:**
    
    1. **Energy Security Crisis:**
       - Crude oil imports ($162.2B) are the single largest trade burden
       - **Action needed:** Accelerate renewable energy adoption, electric vehicle transition
       - Target: Reduce oil import dependency by 30% by 2030
    
    2. **Electronics Manufacturing Opportunity:**
       - Current net import of $50B in electronic goods
       - **PLI Scheme Impact:** Growing domestic assembly (phones, semiconductors)
       - **Goal:** Achieve electronics trade balance by 2027
    
    3. **Value Addition Strategy:**
       - Export petroleum products ($94.5B) while importing crude ($162.2B)
       - **Opportunity:** Expand refining capacity, petrochemical exports
       - Leverage engineering goods strength for high-value manufacturing
    
    4. **Current Account Management:**
       - Trade deficit of $32B requires careful monitoring
       - **Balance through:** Services exports (IT, consulting), remittances
       - Maintain adequate foreign exchange reserves
    """)
    
    # 4.8 Show detailed data
    with st.expander("📋 View Detailed Trade Data"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Import Details:**")
            st.dataframe(imports[['Category', 'Value']].sort_values('Value', ascending=False), use_container_width=True)
        with col2:
            st.markdown("**Export Details:**")
            st.dataframe(exports[['Category', 'Value']].sort_values('Value', ascending=False), use_container_width=True)

    # 5. DATA SOURCES (UPDATED TABLE NUMBERS)
    with st.expander("📊 View Data Sources (Click to Open)"):
        st.markdown("""
        **Data sourced from Reserve Bank of India (RBI):**
        *   **Source Portal:** [RBI Database on Indian Economy (DBIE)](https://cims.rbi.org.in/)
        *   **Specific Report:** Handbook of Statistics on the Indian Economy.
        *   **Tables Used:** 
            *   **Table 116:** Exports of Major Commodities.
            *   **Table 118:** Imports of Major Commodities.
        """)

# --- MAIN EXECUTION ---
if page == "Real-Time Phillips Curve":
    real_phillips_curve()
elif page == "EXIM Trade Pulse":
    real_exim_pulse()
