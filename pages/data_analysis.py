"""数据分析页面模块"""
import streamlit as st
import plotly.express as px
from ui.components import render_kpi_card
from utils.navigation import navigate_to


def page_data_analysis():
    """数据分析页面：多维度数据筛选与趋势分析"""
    if st.button("← 返回主页", key="back_home_1", use_container_width=True):
        navigate_to('Home')
        st.rerun()
        
    st.markdown('<h1 class="page-title">📊 全景数据分析</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">多维度数据筛选与趋势分析</p>', unsafe_allow_html=True)
    
    df = st.session_state['df_data']
    
    # 筛选器区域
    with st.container():
        st.markdown('<div class="filter-card-title">🔍 数据筛选</div>', unsafe_allow_html=True)
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            years = sorted(df['Date'].dt.year.unique())
            selected_years = st.multiselect("选择年份", years, default=years, help="可多选，默认选择全部年份")
            if not selected_years: selected_years = years
        
        with col_filter2:
            selected_type = st.selectbox("客户群组", df['Customer_Type'].unique(), help="选择要分析的客户类型")
            selected_sku_cat = st.selectbox("产品品类", df['Category'].unique(), help="选择要分析的产品类别")

    # 数据过滤
    filtered_df = df[
        (df['Customer_Type'] == selected_type) & 
        (df['Category'] == selected_sku_cat) &
        (df['Date'].dt.year.isin(selected_years))
    ]

    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI 看板
    st.markdown("### 关键绩效指标")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_act = filtered_df['Actual_Qty'].sum()
    total_fcst = filtered_df['Forecast_Qty'].sum()
    avg_price = filtered_df['Price'].mean() if 'Price' in filtered_df else 100 
    bias_pct = (total_fcst - total_act) / total_act * 100 if total_act != 0 else 0
    bias_color = "green" if abs(bias_pct) < 10 else "red"

    with kpi1:
        st.markdown(render_kpi_card("实际提货总量", f"{int(total_act):,}", ""), unsafe_allow_html=True)
    with kpi2:
        delta_text = f"{bias_pct:+.1f}%" if bias_pct != 0 else "0%"
        st.markdown(render_kpi_card("客户预测总量", f"{int(total_fcst):,}", delta_text, bias_color), unsafe_allow_html=True)
    with kpi3:
        st.markdown(render_kpi_card("涉及金额估算", f"¥{int(total_act * avg_price / 10000):,}", "万"), unsafe_allow_html=True)
    with kpi4:
        st.markdown(render_kpi_card("记录行数", f"{len(filtered_df):,}", ""), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 图表区域
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📈 供需趋势对比</div>', unsafe_allow_html=True)
    daily_chart = filtered_df.groupby('Date')[["Actual_Qty", "Forecast_Qty"]].sum().reset_index()
    fig_trend = px.line(
        daily_chart, 
        x='Date', 
        y=['Actual_Qty', 'Forecast_Qty'], 
        color_discrete_map={"Actual_Qty": "#4e73df", "Forecast_Qty": "#f6c23e"},
        labels={'value': '数量', 'Date': '日期', 'Actual_Qty': '实际提货量', 'Forecast_Qty': '预测提货量'}
    )
    fig_trend.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=40, b=40, l=40, r=40)
    )
    fig_trend.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    fig_trend.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('<div class="chart-insight">💡 趋势解读：蓝色线表示实际提货量，黄色线表示预测提货量。两条线的差异反映了预测准确性。</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

