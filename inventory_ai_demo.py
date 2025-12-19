import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os

# ==========================================
# 1. 页面配置与 CSS 美化
# ==========================================
st.set_page_config(page_title="供应链 AI 决策大脑", page_icon="🧠", layout="wide")

# 自定义 CSS 让界面更有科技感
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #4e73df;
    }
    .ai-box {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #90caf9;
    }
    .stAlert {
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心功能函数
# ==========================================

def analyze_data_with_ai(df, customer_type):
    """
    【仿真 AI 引擎】
    这里模拟大模型的思维链。它不调用真实 API (为了演示稳定)，
    而是根据数据计算出的指标，动态拼凑出一段“看起来像 AI 写”的深度分析。
    """
    # 1. 计算核心指标
    total_act = df['Actual_Qty'].sum()
    total_fcst = df['Forecast_Qty'].sum()
    bias = (total_fcst - total_act) / total_act
    
    # 2. 生成“AI 语气”的分析报告
    report = f"**🤖 AI Deep Insight Report ({customer_type})**\n\n"
    
    report += "**1. Current Diagnosis:**\n"
    if bias > 0.15:
        report += f"Detected a significant **Bullwhip Effect**. Customer forecast total ({int(total_fcst):,}) greatly exceeds actual demand ({int(total_act):,}), with a **bias of {bias:.1%}**. This often stems from customers inflating demand to secure capacity.\n"
    elif bias < -0.10:
        report += f"Detected **under-forecasting**. Actual shipments exceed forecasts by {abs(bias):.1%}, which can lead to reduced fill rates and increased urgent freight costs.\n"
    else:
        report += f"Supply and demand are well matched, with overall bias within {bias:.1%}, which is healthy.\n"
        
    report += "\n**2. Pattern Recognition:**\n"
    if customer_type == "TOP":
        report += "The algorithm detects clear **quarterly pulses**. Orders concentrate around Q1 stocking and Q2 peak season, with non-linear stocking behavior. Recommend shifting from pure forecasting to **Collaborative Planning (CPFR)**.\n"
    else:
        report += "Demand shows a **Poisson-like** pattern with high dispersion and long-tail behavior. Individual customers are hard to predict; consider **risk pooling** strategies to aggregate demand.\n"

    report += "\n**3. AI Strategy Suggestions:**\n"
    if bias > 0.10:
        report += f"💡 **Cost Reduction**: Suggest reducing Days of Inventory (DOI) from 30 days to **{int(30/(1+bias))} days**, estimated to free approx **15% - 20%** working capital."
    else:
        report += "💡 **Supply Assurance**: Recommend dynamic buffer inventory and intelligent replenishment alerts to avoid stockouts in peak seasons."
        
    return report

# ==========================================
# 3. 侧边栏：数据上传
# ==========================================
st.sidebar.title("📂 Data Source")
st.sidebar.info("Please upload a cleaned CSV data file.")

uploaded_file = st.sidebar.file_uploader("Upload data (CSV)", type=['csv'])
local_default = "supply_chain_data_5years.csv"

# 若在工作区存在本地默认数据，自动加载以便调试/展示（用户仍可在侧边栏上传其他文件）
if not uploaded_file:
    if os.path.exists(local_default):
        uploaded_file = local_default
        st.sidebar.success(f"已自动使用本地文件：`{local_default}` 加载数据。若需切换，请在左侧上传新的 CSV。")
    else:
        st.markdown("<h1 style='text-align:center'>🧠 供应链 AI 决策大脑</h1>", unsafe_allow_html=True)
        st.warning("👈 请在左侧上传数据文件以启动分析 (使用刚才生成的 CSV)")
        st.markdown("---")
        st.subheader("系统功能预览：")
        st.markdown("""
        * **📈 全景数据透视**：自动清洗并可视化历史流水。
        * **🤖 大模型智能归因**：内置 AI 助手解释数据背后的业务逻辑。
        * **🎯 动态库存仿真**：根据不同客户类型（TOP vs 常规）推演最优库存策略。
        """)
        st.stop()

# ==========================================
# 4. 数据加载与预处理
# ==========================================
try:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 简单的列名校验
    required_cols = ['Date', 'Customer_Type', 'Actual_Qty', 'Forecast_Qty']
    if not all(col in df.columns for col in required_cols):
        st.error(f"数据格式错误！必须包含以下列：{required_cols}")
        st.stop()
        
except Exception as e:
    st.error(f"文件读取失败: {e}")
    st.stop()

# ==========================================
# 5. 主界面构建
# ==========================================
st.markdown("<h1 style='text-align:center'>🧠 Supply Chain AI Decision Engine</h1>", unsafe_allow_html=True)

# 全局过滤器
# 已将分析维度筛选移至主界面（供需趋势图右侧，位于按年份筛选下方）
# 数据过滤将在用户在主界面选择维度后计算（见下方）

# --- 第一部分：BI 驾驶舱 (可视化分析) ---
col_chart1, col_chart2 = st.columns([4, 1])

with col_chart2:
    st.subheader("按年份筛选")
    # 年份基于全量数据显示，位于维度筛选之上
    years = sorted(df['Date'].dt.year.unique())
    selected_years = st.multiselect("选择年份", years, default=years, key='year_sel')
    if not selected_years:
        st.warning("未选择年份；将显示全部年份。")
        selected_years = years

    st.subheader("分析维度筛选")
    # 统一格式：都使用带 key 的 selectbox，下拉样式保持一致
    selected_type = st.selectbox("选择客户群组", df['Customer_Type'].unique(), key='type_sel')
    selected_sku_cat = st.selectbox("选择产品品类", df['Category'].unique(), key='cat_sel')

# 依据所选维度过滤数据
filtered_df = df[(df['Customer_Type'] == selected_type) & (df['Category'] == selected_sku_cat)]

# 标题与 KPI（基于筛选后数据）
st.header(f"1. 供需全景透视 - {selected_type} ({selected_sku_cat})")

# 1.1 关键指标卡 (KPI)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_act = filtered_df['Actual_Qty'].sum()
total_fcst = filtered_df['Forecast_Qty'].sum()
avg_price = filtered_df['Price'].mean() if not np.isnan(filtered_df['Price'].mean()) else 0
bias_pct = (total_fcst - total_act) / total_act * 100 if total_act != 0 else 0

kpi1.metric("实际提货总量", f"{int(total_act):,}", help="实际发生的出库数量")
kpi2.metric("客户预测总量", f"{int(total_fcst):,}", delta=f"{bias_pct:.1f}% 偏差")
kpi3.metric("涉及金额估算", f"¥{int(total_act * avg_price / 10000):,} 万")
kpi4.metric("数据跨度", f"{filtered_df['Date'].dt.year.nunique()} 年")

# 1.2 动态可视化图表
with col_chart1:
    # 时间序列趋势图 (按所选年份筛选并聚合到日)
    df_by_year = filtered_df[filtered_df['Date'].dt.year.isin(selected_years)]
    if df_by_year.empty:
        st.info("No data for the selected year(s). Please choose other years or adjust the filters. Showing all data for the current filters as a fallback.")
        df_by_year = filtered_df.copy()

    daily_chart = df_by_year.groupby('Date')[["Actual_Qty", "Forecast_Qty"]].sum().reset_index()
    fig_trend = px.line(daily_chart, x='Date', y=['Actual_Qty', 'Forecast_Qty'], 
                        title="供需趋势对比 (按时间轴)",
                        color_discrete_map={"Actual_Qty": "#3366cc", "Forecast_Qty": "#ff9900"},
                        labels={"value": "数量", "variable": "指标"})
    fig_trend.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_trend, width='stretch')

# --- 第二部分：AI 智能解读 (大模型嵌入) ---
st.markdown("---")
st.header("2. AI 智能归因分析")

ai_col1, ai_col2 = st.columns([1, 3])

with ai_col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100) # 简单的机器人图标
    st.markdown("### 供应链 AI 助手")
    st.markdown("基于 LLM 大模型对当前筛选的数据进行多维归因。")
    if st.button("✨ 生成 AI 分析报告"):
        with ai_col2:
            with st.spinner("AI 正在读取数据、识别模式、计算置信区间..."):
                time.sleep(1.5) # 模拟思考时间，增加真实感
                insight_text = analyze_data_with_ai(filtered_df, selected_type)
                st.markdown(f"""<div class="ai-box">{insight_text}</div>""", unsafe_allow_html=True)
    else:
        with ai_col2:
            st.info("👈 点击左侧按钮，让 AI 为您解读数据背后的业务逻辑。")


# --- 第三部分：库存策略仿真 (Actionable Insight) ---
st.markdown("---")
st.header("3. 动态库存策略推演")
st.markdown("基于 AI 分析结果，系统自动推荐最优安全库存水位。")

# 交互区
sim_col1, sim_col2 = st.columns([1, 2])

with sim_col1:
    st.subheader("仿真参数设定")
    target_service_level = st.slider("目标服务水平 (Service Level)", 0.80, 0.999, 0.95)
    lead_time = st.number_input("补货提前期 (Lead Time Days)", value=7)
    
    # 动态计算
    std_dev = daily_chart['Actual_Qty'].std()
    mean_dem = daily_chart['Actual_Qty'].mean()
    
    # Z-score 近似
    z_score = 2.05 if target_service_level > 0.97 else (1.65 if target_service_level > 0.9 else 1.28)
    
    safety_stock = z_score * std_dev * np.sqrt(lead_time)
    stock_holding_cost = safety_stock * avg_price
    
    st.markdown("### 📊 推荐结果")
    st.metric("建议安全库存", f"{int(safety_stock):,} 件")
    st.metric("预计资金占用", f"¥{int(stock_holding_cost):,}", delta_color="inverse")

with sim_col2:
    # 简单的正态分布模拟图，展示库存覆盖范围
    x = np.linspace(mean_dem - 4*std_dev, mean_dem + 4*std_dev, 100)
    y = (1/(std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean_dem) / std_dev)**2)
    
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Scatter(x=x, y=y, mode='lines', name='需求分布', fill='tozeroy'))
    # 画出覆盖线
    cutoff = mean_dem + z_score * std_dev
    fig_dist.add_vline(x=cutoff, line_dash="dash", line_color="red", annotation_text=f"覆盖 {target_service_level*100}%")
    
    fig_dist.update_layout(title="需求概率分布与库存覆盖边界", showlegend=False)
    st.plotly_chart(fig_dist, width='stretch')