import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os

# ==========================================
# 1. 页面配置与 CSS 美化 (全局生效)
# ==========================================
st.set_page_config(page_title="供应链 AI 决策大脑", page_icon="🧠", layout="wide")

# 自定义 CSS：增加了首页卡片的样式
st.markdown("""
<style>
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    /* 指标卡片 */
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 3px solid #4e73df;
    }
    /* AI 分析框 */
    .ai-box {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #90caf9;
        margin-top: 20px;
    }
    /* 首页导航卡片 */
    .nav-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        transition: transform 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .nav-card:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-color: #4e73df;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State 初始化 (状态管理)
# ==========================================
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'
if 'df_data' not in st.session_state:
    st.session_state['df_data'] = None

# ==========================================
# 3. 核心功能函数 (AI 逻辑)
# ==========================================
def analyze_data_with_ai(df, customer_type):
    """【仿真 AI 引擎】模拟大模型思维链"""
    total_act = df['Actual_Qty'].sum()
    total_fcst = df['Forecast_Qty'].sum()
    bias = (total_fcst - total_act) / total_act if total_act != 0 else 0
    
    report = f"**🤖 AI Deep Insight Report ({customer_type})**\n\n"
    report += "**1. Current Diagnosis:**\n"
    if bias > 0.15:
        report += f"Detected a significant **Bullwhip Effect**. Forecast ({int(total_fcst):,}) exceeds demand ({int(total_act):,}) by **{bias:.1%}**.\n"
    elif bias < -0.10:
        report += f"Detected **under-forecasting**. Actual shipments exceed forecasts by {abs(bias):.1%}.\n"
    else:
        report += f"Supply and demand are well matched, bias within {bias:.1%}.\n"
        
    report += "\n**2. Pattern Recognition:**\n"
    if customer_type == "TOP":
        report += "Algorithm detects **quarterly pulses**. Recommend shifting to **Collaborative Planning (CPFR)**.\n"
    else:
        report += "Demand shows **Poisson-like** pattern. Consider **risk pooling** strategies.\n"

    report += "\n**3. AI Strategy Suggestions:**\n"
    if bias > 0.10:
        report += f"💡 **Cost Reduction**: Suggest reducing DOI to **{int(30/(1+bias))} days**, freeing **15%-20%** working capital."
    else:
        report += "💡 **Supply Assurance**: Recommend dynamic buffer inventory for peak seasons."
    return report

# ==========================================
# 4. 页面定义
# ==========================================

# --- 4.0 导航辅助函数 ---
def navigate_to(page):
    st.session_state['current_page'] = page

# --- 4.1 首页 (Home) ---
def page_home():
    st.markdown("<h1 style='text-align:center; margin-bottom: 50px;'>🧠 供应链 AI 决策大脑</h1>", unsafe_allow_html=True)
    
    # 1. 数据上传区
    st.markdown("### 1️⃣ 第一步：导入数据")
    uploaded_file = st.file_uploader("请上传清洗后的 CSV 数据文件", type=['csv'])
    
    local_default = "supply_chain_data_5years.csv"
    
    # 数据加载逻辑
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            st.session_state['df_data'] = df
            st.success(f"✅ 数据加载成功！包含 {len(df)} 行记录。")
        except Exception as e:
            st.error(f"文件解析失败: {e}")
    elif os.path.exists(local_default) and st.session_state['df_data'] is None:
        # 尝试自动加载本地默认文件
        try:
            df = pd.read_csv(local_default)
            df['Date'] = pd.to_datetime(df['Date'])
            st.session_state['df_data'] = df
            st.info(f"ℹ️ 已自动加载本地演示数据: `{local_default}`")
        except:
            pass

    st.markdown("---")
    
    # 2. 导航按钮区
    st.markdown("### 2️⃣ 第二步：选择功能模块")
    
    # 检查是否有数据
    is_disabled = st.session_state['df_data'] is None
    if is_disabled:
        st.warning("⚠️ 请先在上方上传数据，才能启用分析模块。")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📊 **全景数据分析**\n\n供需趋势、KPI 看板、AI 智能归因。")
        st.button("进入 -> 数据分析", disabled=is_disabled, on_click=navigate_to, args=('Data Analysis',), use_container_width=True)

    with col2:
        st.warning("👤 **客户专项画像**\n\n客户行为细分、订单画像、流失预警。")
        st.button("进入 -> 客户分析", disabled=is_disabled, on_click=navigate_to, args=('Customer Analysis',), use_container_width=True)

    with col3:
        st.success("📦 **库存策略仿真**\n\n安全库存推演、补货参数优化。")
        st.button("进入 -> 库存策略", disabled=is_disabled, on_click=navigate_to, args=('Inventory Strategy',), use_container_width=True)

# --- 4.2 页面一：数据分析 (原来的主代码) ---
def page_data_analysis():
    st.sidebar.button("🏠 返回主页", on_click=navigate_to, args=('Home',), use_container_width=True)
    st.markdown("# 📊 全景数据分析")
    
    df = st.session_state['df_data']
    
    # ---------------- 原有逻辑开始 ----------------
    
    # 1. 筛选器
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        years = sorted(df['Date'].dt.year.unique())
        selected_years = st.multiselect("选择年份", years, default=years)
        if not selected_years: selected_years = years
    
    with col_filter2:
        selected_type = st.selectbox("选择客户群组", df['Customer_Type'].unique())
        selected_sku_cat = st.selectbox("选择产品品类", df['Category'].unique())

    # 数据过滤
    filtered_df = df[
        (df['Customer_Type'] == selected_type) & 
        (df['Category'] == selected_sku_cat) &
        (df['Date'].dt.year.isin(selected_years))
    ]

    # 2. KPI 看板
    st.markdown("### 关键绩效指标 (KPI)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_act = filtered_df['Actual_Qty'].sum()
    total_fcst = filtered_df['Forecast_Qty'].sum()
    avg_price = filtered_df['Price'].mean() if 'Price' in filtered_df else 100 
    bias_pct = (total_fcst - total_act) / total_act * 100 if total_act != 0 else 0

    kpi1.metric("实际提货总量", f"{int(total_act):,}")
    kpi2.metric("客户预测总量", f"{int(total_fcst):,}", delta=f"{bias_pct:.1f}% 偏差")
    kpi3.metric("涉及金额估算", f"¥{int(total_act * avg_price / 10000):,} 万")
    kpi4.metric("记录行数", f"{len(filtered_df):,}")

    st.markdown("---")

    # 3. 图表与 AI
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📈 供需趋势对比")
        daily_chart = filtered_df.groupby('Date')[["Actual_Qty", "Forecast_Qty"]].sum().reset_index()
        fig_trend = px.line(daily_chart, x='Date', y=['Actual_Qty', 'Forecast_Qty'], 
                            color_discrete_map={"Actual_Qty": "#3366cc", "Forecast_Qty": "#ff9900"})
        fig_trend.update_layout(legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("🤖 AI 智能解读")
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=60)
        if st.button("✨ 生成分析报告"):
            with st.spinner("AI 正在思考..."):
                time.sleep(1)
                insight = analyze_data_with_ai(filtered_df, selected_type)
                st.markdown(f'<div class="ai-box" style="font-size:0.9em;">{insight}</div>', unsafe_allow_html=True)
        else:
            st.info("点击按钮，让 AI 基于当前筛选数据生成诊断报告。")

# --- 4.3 页面二：客户分析 ---
def page_customer_analysis():
    st.sidebar.button("🏠 返回主页", on_click=navigate_to, args=('Home',), use_container_width=True)
    st.markdown("# 👤 客户专项分析")
    
    df = st.session_state['df_data']
    
    # 1. 检测客户标识字段
    customer_field = None
    possible_fields = ['Customer_ID', 'Customer_Name', 'CustomerCode', 'Customer']
    for field in possible_fields:
        if field in df.columns:
            customer_field = field
            break
    
    # 如果没有找到单独的客户ID字段，使用 Customer_Type
    if customer_field is None:
        if 'Customer_Type' in df.columns:
            customer_field = 'Customer_Type'
        else:
            st.error("❌ 数据中未找到客户标识字段，无法进行客户分析。")
            return
    
    # 2. 客户选择界面
    st.markdown("### 📋 选择客户")
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # 获取所有唯一客户
        unique_customers = sorted(df[customer_field].unique())
        if len(unique_customers) == 0:
            st.warning("⚠️ 数据中没有客户记录。")
            return
        
        selected_customer = st.selectbox(
            f"选择客户 ({customer_field})",
            unique_customers,
            help=f"共 {len(unique_customers)} 个客户可选"
        )
    
    with col_filter2:
        # 年份筛选
        if 'Date' in df.columns:
            # 确保Date是datetime类型
            if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df_temp = df.copy()
                df_temp['Date'] = pd.to_datetime(df_temp['Date'], errors='coerce')
                years = sorted(df_temp['Date'].dt.year.dropna().unique())
            else:
                years = sorted(df['Date'].dt.year.dropna().unique())
        else:
            years = []
        selected_years = st.multiselect("选择年份", years, default=years if years else [])
        if not selected_years:
            selected_years = years
    
    # 3. 数据过滤
    filtered_df = df[df[customer_field] == selected_customer].copy()
    
    if 'Date' in filtered_df.columns:
        # 确保Date是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(filtered_df['Date']):
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
        # 过滤年份
        if selected_years and len(selected_years) > 0:
            filtered_df = filtered_df[filtered_df['Date'].dt.year.isin(selected_years)]
    
    # 检查是否有数据
    if len(filtered_df) == 0:
        st.warning(f"⚠️ 客户 {selected_customer} 在所选时间段内没有数据记录。")
        return
    
    # 显示客户基本信息
    customer_type = filtered_df['Customer_Type'].iloc[0] if 'Customer_Type' in filtered_df.columns else "未知"
    st.info(f"**客户信息**: {selected_customer} | **客户类型**: {customer_type} | **记录数**: {len(filtered_df):,} 条")
    
    st.markdown("---")
    
    # 4. KPI 指标卡片
    st.markdown("### 📊 关键绩效指标 (KPI)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_act = filtered_df['Actual_Qty'].sum()
    total_fcst = filtered_df['Forecast_Qty'].sum()
    avg_price = filtered_df['Price'].mean() if 'Price' in filtered_df.columns else 0
    bias_pct = (total_fcst - total_act) / total_act * 100 if total_act != 0 else 0
    avg_order = total_act / len(filtered_df) if len(filtered_df) > 0 else 0
    
    kpi1.metric("总实际提货量", f"{int(total_act):,}")
    kpi2.metric("总预测提货量", f"{int(total_fcst):,}", delta=f"{bias_pct:.1f}%")
    kpi3.metric("平均订单量", f"{avg_order:.1f}")
    kpi4.metric("涉及金额", f"¥{int(total_act * avg_price / 10000):,} 万")
    
    st.markdown("---")
    
    # 5. 历史数据可视化
    st.markdown("### 📈 历史数据可视化")
    
    # 5.1 时间序列趋势图
    if 'Date' in filtered_df.columns and len(filtered_df) > 0:
        st.subheader("📅 时间序列趋势")
        time_chart = filtered_df.groupby('Date')[["Actual_Qty", "Forecast_Qty"]].sum().reset_index()
        fig_time = px.line(
            time_chart, 
            x='Date', 
            y=['Actual_Qty', 'Forecast_Qty'],
            labels={'value': '数量', 'Date': '日期'},
            title=f"{selected_customer} - 实际提货量 vs 预测量趋势",
            color_discrete_map={"Actual_Qty": "#3366cc", "Forecast_Qty": "#ff9900"}
        )
        fig_time.update_layout(
            legend=dict(orientation="h", y=1.1),
            hovermode='x unified'
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        # 5.2 月度汇总图
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📆 月度汇总")
            filtered_df['YearMonth'] = filtered_df['Date'].dt.to_period('M').astype(str)
            monthly_data = filtered_df.groupby('YearMonth')['Actual_Qty'].sum().reset_index()
            fig_monthly = px.bar(
                monthly_data,
                x='YearMonth',
                y='Actual_Qty',
                labels={'Actual_Qty': '实际提货量', 'YearMonth': '年月'},
                title="月度实际提货量",
                color='Actual_Qty',
                color_continuous_scale='Blues'
            )
            fig_monthly.update_layout(showlegend=False)
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col_chart2:
            st.subheader("📅 年度汇总")
            filtered_df['Year'] = filtered_df['Date'].dt.year
            yearly_data = filtered_df.groupby('Year')['Actual_Qty'].sum().reset_index()
            fig_yearly = px.bar(
                yearly_data,
                x='Year',
                y='Actual_Qty',
                labels={'Actual_Qty': '实际提货量', 'Year': '年份'},
                title="年度实际提货量",
                color='Actual_Qty',
                color_continuous_scale='Greens'
            )
            fig_yearly.update_layout(showlegend=False)
            st.plotly_chart(fig_yearly, use_container_width=True)
    
    # 5.3 产品品类分布
    if 'Category' in filtered_df.columns:
        st.subheader("📦 产品品类分布")
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            category_data = filtered_df.groupby('Category')['Actual_Qty'].sum().reset_index()
            fig_pie = px.pie(
                category_data,
                values='Actual_Qty',
                names='Category',
                title="产品品类占比（饼图）"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_bar:
            category_data = filtered_df.groupby('Category')['Actual_Qty'].sum().reset_index()
            fig_bar = px.bar(
                category_data,
                x='Category',
                y='Actual_Qty',
                labels={'Actual_Qty': '实际提货量', 'Category': '产品品类'},
                title="产品品类分布（柱状图）",
                color='Actual_Qty',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # 5.4 预测准确度分析
    st.subheader("🎯 预测准确度分析")
    if len(filtered_df) > 0:
        filtered_df['Forecast_Error'] = filtered_df['Forecast_Qty'] - filtered_df['Actual_Qty']
        # 计算百分比误差，避免除零错误
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
                        title="预测误差趋势",
                        color_discrete_sequence=['#e74c3c']
                    )
                    fig_error.add_hline(y=0, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig_error, use_container_width=True)
                else:
                    st.info("暂无预测误差数据")
        
        with col_acc2:
            # 预测准确度统计
            mae = filtered_df['Forecast_Error'].abs().mean()
            mape = filtered_df['Forecast_Error_Pct'].abs().mean()
            st.metric("平均绝对误差 (MAE)", f"{mae:.2f}" if not pd.isna(mae) else "N/A")
            st.metric("平均绝对百分比误差 (MAPE)", f"{mape:.2f}%" if not pd.isna(mape) else "N/A")
            st.metric("预测偏差率", f"{bias_pct:.2f}%")

# --- 4.4 页面三：库存策略 (Placeholder) ---
def page_inventory_strategy():
    st.sidebar.button("🏠 返回主页", on_click=navigate_to, args=('Home',), use_container_width=True)
    st.title("📦 库存策略中心")
    
    st.info("🚧 此模块正在开发中...")
    
    st.markdown("### 规划功能：")
    st.markdown("""
    * **多级库存优化 (MEIO)**
    * **呆滞库存 (SLOB) 预警**
    * **补货参数 (Min/Max) 模拟器**
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.slider("目标服务水平", 0.8, 0.99, 0.95)
    with col2:
        st.number_input("持有成本 (%)", 10)

# ==========================================
# 5. 主程序入口 (路由控制)
# ==========================================
def main():
    # 侧边栏显示当前状态
    if st.session_state['current_page'] != 'Home':
        st.sidebar.markdown(f"**当前页面:** {st.session_state['current_page']}")
        st.sidebar.markdown("---")

    # 路由逻辑
    if st.session_state['current_page'] == 'Home':
        page_home()
    elif st.session_state['current_page'] == 'Data Analysis':
        page_data_analysis()
    elif st.session_state['current_page'] == 'Customer Analysis':
        page_customer_analysis()
    elif st.session_state['current_page'] == 'Inventory Strategy':
        page_inventory_strategy()

if __name__ == "__main__":
    main()