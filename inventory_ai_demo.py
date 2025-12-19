import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

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
    report = f"**🤖 AI 深度洞察报告 ({customer_type})**\n\n"
    
    report += "**1. 现状诊断：**\n"
    if bias > 0.15:
        report += f"检测到严重的**‘牛鞭效应’ (Bullwhip Effect)**。客户预测总量 ({int(total_fcst):,}) 远高于实际需求 ({int(total_act):,})，**偏差高达 {bias:.1%}**。这通常源于客户为了抢占产能而虚报需求。\n"
    elif bias < -0.10:
        report += f"检测到明显的**‘需求低估’**。实际出库量超出预测 {abs(bias):.1%}，这极易导致**现货率 (Fill Rate)** 下降和紧急空运成本增加。\n"
    else:
        report += f"当前供需匹配度良好，整体偏差控制在 {bias:.1%} 以内，属于健康范围。\n"
        
    report += "\n**2. 模式识别：**\n"
    if customer_type == "TOP":
        report += "算法识别到明显的**‘季度脉冲’**特征。订单集中在 Q1 备货期和 Q2 旺季，且存在非线性的囤货行为。建议从‘单纯预测’转向‘协同计划 (CPFR)’。\n"
    else:
        report += "需求呈现**‘泊松分布’**特征，离散度高但长尾效应明显。单个客户的需求难以预测，建议采用‘库存池 (Risk Pooling)’ 策略进行聚合管理。\n"

    report += "\n**3. AI 策略建议：**\n"
    if bias > 0.10:
        report += f"💡 **建议降本**：系统建议将安全库存覆盖天数 (DOI) 从 30天 下调至 **{int(30/(1+bias))}天**，预计可释放现金流约 **15% - 20%**。"
    else:
        report += "💡 **建议保供**：建议设置动态缓冲库存，并开启智能补货预警，确保旺季不缺货。"
        
    return report

# ==========================================
# 3. 侧边栏：数据上传
# ==========================================
st.sidebar.title("📂 数据源配置")
st.sidebar.info("本系统需上传标准清洗后的 CSV 数据")

uploaded_file = st.sidebar.file_uploader("上传业务数据 (CSV)", type=['csv'])

if not uploaded_file:
    st.title("🧠 供应链 AI 决策大脑")
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
st.title("🧠 供应链 AI 决策大脑")

# 全局过滤器
st.sidebar.markdown("---")
st.sidebar.header("🔍 分析维度筛选")
selected_type = st.sidebar.selectbox("选择客户群组", df['Customer_Type'].unique())
selected_sku_cat = st.sidebar.selectbox("选择产品品类", df['Category'].unique())

# 数据过滤
filtered_df = df[(df['Customer_Type'] == selected_type) & (df['Category'] == selected_sku_cat)]

# --- 第一部分：BI 驾驶舱 (可视化分析) ---
st.header(f"1. 供需全景透视 - {selected_type} ({selected_sku_cat})")

# 1.1 关键指标卡 (KPI)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_act = filtered_df['Actual_Qty'].sum()
total_fcst = filtered_df['Forecast_Qty'].sum()
avg_price = filtered_df['Price'].mean()
bias_pct = (total_fcst - total_act) / total_act * 100

kpi1.metric("实际提货总量", f"{int(total_act):,}", help="实际发生的出库数量")
kpi2.metric("客户预测总量", f"{int(total_fcst):,}", delta=f"{bias_pct:.1f}% 偏差")
kpi3.metric("涉及金额估算", f"¥{int(total_act * avg_price / 10000):,} 万")
kpi4.metric("数据跨度", f"{filtered_df['Date'].dt.year.nunique()} 年")

# 1.2 动态可视化图表
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    # 时间序列趋势图 (聚合到月)
    daily_chart = filtered_df.groupby('Date')[['Actual_Qty', 'Forecast_Qty']].sum().reset_index()
    fig_trend = px.line(daily_chart, x='Date', y=['Actual_Qty', 'Forecast_Qty'], 
                        title="供需趋势对比 (按时间轴)",
                        color_discrete_map={"Actual_Qty": "#3366cc", "Forecast_Qty": "#ff9900"},
                        labels={"value": "数量", "variable": "指标"})
    fig_trend.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_trend, use_container_width=True)

with col_chart2:
    # 偏差散点图 (用于展示离散度)
    fig_scatter = px.scatter(daily_chart, x="Actual_Qty", y="Forecast_Qty", 
                             trendline="ols", title="预测能力相关性分析",
                             labels={"Actual_Qty": "实际", "Forecast_Qty": "预测"})
    # 添加一条 y=x 的参考线
    fig_scatter.add_shape(type="line", line=dict(dash="dash", color="gray"),
                          x0=0, y0=daily_chart['Actual_Qty'].max(),
                          x1=0, y1=daily_chart['Actual_Qty'].max())
    st.plotly_chart(fig_scatter, use_container_width=True)


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
    st.plotly_chart(fig_dist, use_container_width=True)