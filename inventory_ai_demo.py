import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import json
from typing import List, Dict, Optional

# 尝试导入 Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    # 这里不直接 st.warning，避免影响页面布局，在调用时检查

# ==========================================
# 1. 页面配置与 CSS 美化 (全局生效)
# ==========================================
st.set_page_config(page_title="供应链 AI 决策大脑", page_icon="🧠", layout="wide")

# 企业级 SaaS 风格 CSS
st.markdown("""
<style>
    /* 全局样式 */
    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* 页面标题样式 */
    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .page-subtitle {
        font-size: 1rem;
        color: #6c757d;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* KPI 卡片样式 */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #4e73df;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    .kpi-label {
        font-size: 0.875rem;
        color: #6c757d;
        font-weight: 500;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 4px;
    }
    
    .kpi-unit {
        font-size: 0.875rem;
        color: #6c757d;
        font-weight: 400;
    }
    
    .kpi-delta-positive {
        color: #1cc88a;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .kpi-delta-negative {
        color: #e74a3b;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* Filter Card 样式 */
    .filter-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    
    .filter-card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Profile Card 样式 */
    .profile-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        margin-bottom: 2rem;
    }
    
    .profile-card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 12px;
    }
    
    .profile-card-content {
        color: #6c757d;
        font-size: 0.9375rem;
        line-height: 1.6;
    }
    
    /* 模块入口卡片 */
    .module-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 32px 24px;
        border: 2px solid #e9ecef;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .module-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(78, 115, 223, 0.15);
        border-color: #4e73df;
    }
    
    .module-icon {
        font-size: 3rem;
        margin-bottom: 16px;
    }
    
    .module-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 12px;
    }
    
    .module-desc {
        font-size: 0.9375rem;
        color: #6c757d;
        line-height: 1.6;
    }
    
    /* Step 卡片 */
    .step-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .step-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4e73df 0%, #5a6fd8 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.125rem;
    }
    
    .step-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
    }
    
    /* 图表容器 */
    .chart-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e9ecef;
    }
    
    .chart-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 16px;
    }
    
    .chart-insight {
        font-size: 0.875rem;
        color: #6c757d;
        margin-top: 12px;
        font-style: italic;
        padding-top: 12px;
        border-top: 1px solid #e9ecef;
    }
    
    /* 按钮样式优化 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    /* 分割线优化 */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e9ecef;
    }
    
    /* 返回按钮样式 */
    .back-button {
        margin-bottom: 1.5rem;
    }

    /* =================================================================
       浮动聊天窗口特殊样式 (针对 st.popover)
       ================================================================= */
    
    /* 1. 将 Popover 触发按钮定位到右下角 */
    [data-testid="stPopover"] {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }

    /* 2. 美化触发按钮为圆形、蓝色渐变 */
    [data-testid="stPopover"] > button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4e73df 0%, #5a6fd8 100%);
        border: none;
        box-shadow: 0 4px 16px rgba(78, 115, 223, 0.4);
        color: white;
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s;
    }

    [data-testid="stPopover"] > button:hover {
        transform: scale(1.1);
        color: white;
        border: none;
    }

    /* 3. 隐藏按钮内默认的文字容器边距，确保图标居中 */
    [data-testid="stPopover"] > button > div {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* 4. 调整弹出窗口的尺寸 */
    [data-testid="stPopoverBody"] {
        width: 400px !important;
        max-height: 600px !important;
        border-radius: 12px;
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
        padding: 0 !important;
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
# LLM 相关 Session State
if 'chat_messages' not in st.session_state:
    st.session_state['chat_messages'] = []
if 'gemini_api_key' not in st.session_state:
    # 从环境变量读取 API Key，如果没有则使用空字符串
    st.session_state['gemini_api_key'] = os.getenv('GEMINI_API_KEY', '')
if 'gemini_model' not in st.session_state:
    st.session_state['gemini_model'] = 'gemini-pro'
if 'llm_provider' not in st.session_state:
    st.session_state['llm_provider'] = 'gemini'

# ==========================================
# 3. UI Helper Functions
# ==========================================

def render_kpi_card(label: str, value: str, delta: str = None, delta_color: str = None):
    """渲染 KPI 卡片"""
    delta_class = "kpi-delta-positive" if delta_color == "green" else "kpi-delta-negative" if delta_color == "red" else ""
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ""
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

def render_profile_card(title: str, content: str):
    """渲染客户信息卡片"""
    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-card-title">{title}</div>
        <div class="profile-card-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LLM 功能函数 (Gemini 集成)
# ==========================================

def get_page_context() -> str:
    """获取当前页面上下文信息，用于 LLM 提示"""
    context = f"当前页面: {st.session_state.get('current_page', 'Home')}\n"
    
    df = st.session_state.get('df_data')
    if df is not None:
        context += f"数据概览: 共 {len(df)} 行记录\n"
        context += f"数据列: {', '.join(df.columns.tolist())}\n"
    return context

def call_gemini(messages: List[Dict], api_key: str, model: str = 'gemini-pro') -> Optional[str]:
    """调用 Google Gemini API"""
    if not GEMINI_AVAILABLE:
        return "❌ 未安装 google-generativeai 库，请运行: pip install google-generativeai"
    
    if not api_key:
        return "❌ 请设置环境变量 GEMINI_API_KEY"
    
    try:
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        # 将消息格式转换为 Gemini 格式
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                prompt_parts.append(content)
            elif role == 'user':
                prompt_parts.append(f"用户: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"助手: {content}")
        
        # 生成响应
        response = model_instance.generate_content('\n'.join(prompt_parts))
        return response.text
    except Exception as e:
        return f"❌ Gemini API 调用失败: {str(e)}"

def chat_with_llm(user_message: str, provider: str = 'gemini') -> str:
    """与 LLM 进行对话"""
    # 获取页面上下文
    page_context = get_page_context()
    
    # 构建系统提示
    system_prompt = f"""你是一个专业的供应链数据分析助手。你的任务是帮助用户理解供应链数据和分析结果。

当前上下文信息:
{page_context}

请用中文回答用户的问题，提供专业、清晰的分析和建议。"""
    
    # 初始化消息列表（如果为空）
    if not st.session_state['chat_messages']:
        st.session_state['chat_messages'] = [
            {'role': 'system', 'content': system_prompt}
        ]
    
    # 添加用户消息
    st.session_state['chat_messages'].append({
        'role': 'user',
        'content': user_message
    })
    
    # 调用 LLM
    if provider == 'gemini':
        response = call_gemini(
            st.session_state['chat_messages'],
            st.session_state['gemini_api_key'],
            st.session_state['gemini_model']
        )
    else:
        response = "❌ 不支持的 LLM 提供商"
    
    # 添加助手回复
    if response:
        st.session_state['chat_messages'].append({
            'role': 'assistant',
            'content': response
        })
    
    return response

def render_floating_chat():
    """
    渲染浮动聊天窗口
    修复版：使用 Streamlit 原生 st.popover + st.chat_input，彻底解决发送失败问题。
    """
    
    # 使用原生 Popover 组件
    # 通过 CSS [data-testid="stPopover"] 将其定位到了右下角
    with st.popover("💬", help="AI 智能助手"):
        st.markdown('<div style="padding: 10px 0px; font-weight: bold; border-bottom: 1px solid #eee; margin-bottom: 10px;">✨ 供应链数据助手</div>', unsafe_allow_html=True)
        
        # 创建一个容器用于显示聊天记录，设置固定高度以允许滚动
        chat_container = st.container(height=400)
        
        with chat_container:
            # 如果没有消息，显示欢迎语
            if not st.session_state['chat_messages']:
                st.info("👋 您好！我是您的数据分析助手。您可以问我关于库存、销量或预测的问题。")
            
            # 渲染历史消息
            for msg in st.session_state['chat_messages']:
                if msg.get('role') == 'system':
                    continue
                
                # 使用 Streamlit 原生聊天气泡
                with st.chat_message(msg['role'], avatar="🧑‍💻" if msg['role'] == "user" else "🤖"):
                    st.markdown(msg['content'])

        # 渲染原生聊天输入框 (关键：这解决了发送问题)
        if prompt := st.chat_input("输入您的问题...", key="floating_chat_input"):
            
            # 1. 立即显示用户输入
            with chat_container:
                with st.chat_message("user", avatar="🧑‍💻"):
                    st.markdown(prompt)
            
            # 2. 调用 LLM
            provider = st.session_state.get('llm_provider', 'gemini')
            
            with chat_container:
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("思考中..."):
                        # chat_with_llm 函数内部会自动追加 assistant 回复到 session_state
                        response = chat_with_llm(prompt, provider)
                        st.markdown(response)
            
            # 强制刷新以保存状态并更新界面
            st.rerun()


# ==========================================
# 5. 页面定义
# ==========================================

# --- 5.0 导航辅助函数 ---
def navigate_to(page):
    st.session_state['current_page'] = page

# --- 5.1 首页 (Home) ---
def page_home():
    st.markdown('<h1 class="page-title">供应链 AI 决策大脑</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">基于数据驱动的智能供应链分析与决策平台</p>', unsafe_allow_html=True)
    
    # Step 1: 数据上传
    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">1</div>
            <div class="step-title">导入数据</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("上传 CSV 数据文件", type=['csv'], help="支持标准 CSV 格式，包含 Date, Customer_ID, SKU_ID, Actual_Qty, Forecast_Qty 等字段")
    
    local_default = "supply_chain_data_5years.csv"
    
    # 数据加载逻辑
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            st.session_state['df_data'] = df
            st.success(f"✅ 数据加载成功，共 {len(df):,} 条记录")
        except Exception as e:
            st.error(f"❌ 文件解析失败：{str(e)}")
    elif os.path.exists(local_default) and st.session_state['df_data'] is None:
        # 尝试自动加载本地默认文件
        try:
            df = pd.read_csv(local_default)
            df['Date'] = pd.to_datetime(df['Date'])
            st.session_state['df_data'] = df
            st.info(f"ℹ️ 已自动加载演示数据：{local_default}")
        except:
            pass

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Step 2: 模块选择
    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">2</div>
            <div class="step-title">选择分析模块</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 检查是否有数据
    is_disabled = st.session_state['df_data'] is None
    if is_disabled:
        st.warning("⚠️ 请先上传数据文件以启用分析功能")
        st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="module-card">
            <div class="module-icon">📊</div>
            <div class="module-title">全景数据分析</div>
            <div class="module-desc">供需趋势分析、KPI 看板、数据洞察</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入数据分析", disabled=is_disabled, key="btn_data", use_container_width=True):
            navigate_to('Data Analysis')
            st.rerun()

    with col2:
        st.markdown("""
        <div class="module-card">
            <div class="module-icon">👤</div>
            <div class="module-title">客户专项画像</div>
            <div class="module-desc">客户行为分析、订单画像、预测准确性评估</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入客户分析", disabled=is_disabled, key="btn_customer", use_container_width=True):
            navigate_to('Customer Analysis')
            st.rerun()

    with col3:
        st.markdown("""
        <div class="module-card">
            <div class="module-icon">📦</div>
            <div class="module-title">库存策略仿真</div>
            <div class="module-desc">安全库存推演、补货参数优化、策略模拟</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入库存策略", disabled=is_disabled, key="btn_inventory", use_container_width=True):
            navigate_to('Inventory Strategy')
            st.rerun()

# --- 5.2 页面一：数据分析 ---
def page_data_analysis():
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

# --- 5.3 页面二：客户分析 ---
def page_customer_analysis():
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

# --- 5.4 页面三：库存策略 (Placeholder) ---
def page_inventory_strategy():
    if st.button("← 返回主页", key="back_home_3", use_container_width=True):
        navigate_to('Home')
        st.rerun()

    st.markdown('<h1 class="page-title">📦 库存策略中心</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">库存优化与补货策略仿真</p>', unsafe_allow_html=True)
    
    st.info("🚧 此模块正在开发中，敬请期待")
    
    st.markdown("### 规划功能")
    st.markdown("""
    * **多级库存优化 (MEIO)** - 跨层级库存协同优化
    * **呆滞库存 (SLOB) 预警** - 智能识别滞销风险
    * **补货参数 (Min/Max) 模拟器** - 动态调整补货策略
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.slider("目标服务水平", 0.8, 0.99, 0.95, help="服务水平越高，库存成本越高")
    with col2:
        st.number_input("持有成本 (%)", value=10, min_value=1, max_value=50, help="年度库存持有成本占商品价值的百分比")

# ==========================================
# 6. 主程序入口 (路由控制)
# ==========================================
def main():
    
    # 渲染浮动聊天窗口
    render_floating_chat()

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