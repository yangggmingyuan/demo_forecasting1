"""客户分析页面模块"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from ui.components import render_kpi_card, render_profile_card
from utils.navigation import navigate_to


def page_customer_analysis():
    """客户分析页面：深度洞察客户行为与订单特征"""
    if st.button("← 返回主页", key="back_home_2", use_container_width=True):
        navigate_to('Home')
        st.rerun()

    st.markdown('<h1 class="page-title">👤 客户专项分析</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">深度洞察客户行为与订单特征</p>', unsafe_allow_html=True)
    
    df = st.session_state['df_data']
    
    # 1. 检测客户标识字段
    customer_field = None
    possible_fields = ['Customer_ID', 'Customer_Name', 'CustomerCode', 'Customer']
    for field in possible_fields:
        if field in df.columns:
            customer_field = field
            break
    
    if customer_field is None:
        if 'Customer_Type' in df.columns:
            customer_field = 'Customer_Type'
        else:
            st.error("❌ 数据中未找到客户标识字段，无法进行客户分析")
            return
    
    # 2. 筛选器区域
    with st.container():
        st.markdown('<div class="filter-card-title">🔍 数据筛选</div>', unsafe_allow_html=True)
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            unique_customers = sorted(df[customer_field].unique())
            if len(unique_customers) == 0:
                st.warning("⚠️ 数据中没有客户记录")
                return
            
            selected_customer = st.selectbox(
                f"选择客户",
                unique_customers,
                help=f"共 {len(unique_customers)} 个客户可选"
            )
        
        with col_filter2:
            if 'Date' in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                    df_temp = df.copy()
                    df_temp['Date'] = pd.to_datetime(df_temp['Date'], errors='coerce')
                    years = sorted(df_temp['Date'].dt.year.dropna().unique())
                else:
                    years = sorted(df['Date'].dt.year.dropna().unique())
            else:
                years = []
            selected_years = st.multiselect("选择年份", years, default=years if years else [], help="可多选，默认选择全部年份")
            if not selected_years:
                selected_years = years
    
    # 3. 数据过滤
    filtered_df = df[df[customer_field] == selected_customer].copy()
    
    if 'Date' in filtered_df.columns:
        if not pd.api.types.is_datetime64_any_dtype(filtered_df['Date']):
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
        if selected_years and len(selected_years) > 0:
            filtered_df = filtered_df[filtered_df['Date'].dt.year.isin(selected_years)]
    
    # 检查是否有数据
    if len(filtered_df) == 0:
        st.warning(f"⚠️ 客户 {selected_customer} 在所选时间段内没有数据记录")
        return
    
    # 4. 客户基本信息卡片
    customer_type = filtered_df['Customer_Type'].iloc[0] if 'Customer_Type' in filtered_df.columns else "未知"
    render_profile_card(
        f"客户信息：{selected_customer}",
        f"<strong>客户类型：</strong>{customer_type} | <strong>记录数：</strong>{len(filtered_df):,} 条"
    )
    
    # 5. KPI 指标卡片
    st.markdown("### 关键绩效指标")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_act = filtered_df['Actual_Qty'].sum()
    total_fcst = filtered_df['Forecast_Qty'].sum()
    avg_price = filtered_df['Price'].mean() if 'Price' in filtered_df.columns else 0
    bias_pct = (total_fcst - total_act) / total_act * 100 if total_act != 0 else 0
    avg_order = total_act / len(filtered_df) if len(filtered_df) > 0 else 0
    bias_color = "green" if abs(bias_pct) < 10 else "red"
    
    with kpi1:
        st.markdown(render_kpi_card("总实际提货量", f"{int(total_act):,}", ""), unsafe_allow_html=True)
    with kpi2:
        delta_text = f"{bias_pct:+.1f}%" if bias_pct != 0 else "0%"
        st.markdown(render_kpi_card("总预测提货量", f"{int(total_fcst):,}", delta_text, bias_color), unsafe_allow_html=True)
    with kpi3:
        st.markdown(render_kpi_card("平均订单量", f"{avg_order:.1f}", ""), unsafe_allow_html=True)
    with kpi4:
        st.markdown(render_kpi_card("涉及金额", f"¥{int(total_act * avg_price / 10000):,}", "万"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 6. 时间序列趋势图
    if 'Date' in filtered_df.columns and len(filtered_df) > 0:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📅 时间序列趋势</div>', unsafe_allow_html=True)
        time_chart = filtered_df.groupby('Date')[["Actual_Qty", "Forecast_Qty"]].sum().reset_index()
        fig_time = px.line(
            time_chart, 
            x='Date', 
            y=['Actual_Qty', 'Forecast_Qty'],
            labels={'value': '数量', 'Date': '日期', 'Actual_Qty': '实际提货量', 'Forecast_Qty': '预测提货量'},
            color_discrete_map={"Actual_Qty": "#4e73df", "Forecast_Qty": "#f6c23e"}
        )
        fig_time.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=40, b=40, l=40, r=40)
        )
        fig_time.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
        fig_time.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
        st.plotly_chart(fig_time, use_container_width=True)
        st.markdown('<div class="chart-insight">💡 趋势解读：展示客户的实际提货量与预测提货量随时间的变化趋势，帮助识别需求波动模式。</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 7. 月度/年度汇总图
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📆 月度汇总</div>', unsafe_allow_html=True)
            filtered_df['YearMonth'] = filtered_df['Date'].dt.to_period('M').astype(str)
            monthly_data = filtered_df.groupby('YearMonth')['Actual_Qty'].sum().reset_index()
            fig_monthly = px.bar(
                monthly_data,
                x='YearMonth',
                y='Actual_Qty',
                labels={'Actual_Qty': '实际提货量', 'YearMonth': '年月'},
                color='Actual_Qty',
                color_continuous_scale='Blues'
            )
            fig_monthly.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=40, b=40, l=40, r=40)
            )
            fig_monthly.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
            fig_monthly.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
            st.plotly_chart(fig_monthly, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📅 年度汇总</div>', unsafe_allow_html=True)
            filtered_df['Year'] = filtered_df['Date'].dt.year
            yearly_data = filtered_df.groupby('Year')['Actual_Qty'].sum().reset_index()
            fig_yearly = px.bar(
                yearly_data,
                x='Year',
                y='Actual_Qty',
                labels={'Actual_Qty': '实际提货量', 'Year': '年份'},
                color='Actual_Qty',
                color_continuous_scale='Greens'
            )
            fig_yearly.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=40, b=40, l=40, r=40)
            )
            fig_yearly.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
            fig_yearly.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
            st.plotly_chart(fig_yearly, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 8. 产品品类分布
    if 'Category' in filtered_df.columns:
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📦 产品品类占比</div>', unsafe_allow_html=True)
            category_data = filtered_df.groupby('Category')['Actual_Qty'].sum().reset_index()
            fig_pie = px.pie(
                category_data,
                values='Actual_Qty',
                names='Category',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=40, b=40, l=40, r=40)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_bar:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📦 产品品类分布</div>', unsafe_allow_html=True)
            category_data = filtered_df.groupby('Category')['Actual_Qty'].sum().reset_index()
            fig_bar = px.bar(
                category_data,
                x='Category',
                y='Actual_Qty',
                labels={'Actual_Qty': '实际提货量', 'Category': '产品品类'},
                color='Actual_Qty',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=40, b=40, l=40, r=40)
            )
            fig_bar.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
            fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 9. 预测准确度分析
    if len(filtered_df) > 0:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🎯 预测准确度分析</div>', unsafe_allow_html=True)
        filtered_df['Forecast_Error'] = filtered_df['Forecast_Qty'] - filtered_df['Actual_Qty']
        filtered_df['Forecast_Error_Pct'] = np.where(
            filtered_df['Actual_Qty'] != 0,
            (filtered_df['Forecast_Error'] / filtered_df['Actual_Qty'] * 100),
            np.nan
        )
        
        col_acc1, col_acc2 = st.columns(2)
        
        with col_acc1:
            if 'Date' in filtered_df.columns and len(filtered_df) > 0:
                error_chart = filtered_df.groupby('Date')['Forecast_Error'].sum().reset_index()
                if len(error_chart) > 0:
                    fig_error = px.line(
                        error_chart,
                        x='Date',
                        y='Forecast_Error',
                        labels={'Forecast_Error': '预测误差', 'Date': '日期'},
                        color_discrete_sequence=['#e74a3b']
                    )
                    fig_error.add_hline(y=0, line_dash="dash", line_color="#6c757d", line_width=1)
                    fig_error.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(t=40, b=40, l=40, r=40)
                    )
                    fig_error.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
                    fig_error.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
                    st.plotly_chart(fig_error, use_container_width=True)
                else:
                    st.info("暂无预测误差数据")
        
        with col_acc2:
            mae = filtered_df['Forecast_Error'].abs().mean()
            mape = filtered_df['Forecast_Error_Pct'].abs().mean()
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("平均绝对误差 (MAE)", f"{mae:.2f}" if not pd.isna(mae) else "N/A")
            st.metric("平均绝对百分比误差 (MAPE)", f"{mape:.2f}%" if not pd.isna(mape) else "N/A")
            st.metric("预测偏差率", f"{bias_pct:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)

