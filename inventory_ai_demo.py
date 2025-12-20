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
    st.warning("⚠️ 未安装 google-generativeai 库，请运行: pip install google-generativeai")

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
    /* 浮动聊天窗口样式 */
    .chat-widget-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .chat-launcher {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff6b9d, #ff8fab);
        box-shadow: 0 4px 12px rgba(255, 107, 157, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        border: none;
        color: white;
        font-size: 24px;
    }
    .chat-launcher:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(255, 107, 157, 0.6);
    }
    .chat-window {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 380px;
        height: 600px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        z-index: 1001;
        animation: slideUp 0.3s ease-out;
    }
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .chat-header {
        background: white;
        padding: 16px 20px;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .chat-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .chat-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: linear-gradient(135deg, #ff6b9d, #ff8fab);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
    }
    .chat-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
    }
    .chat-close {
        background: none;
        border: none;
        font-size: 20px;
        color: #666;
        cursor: pointer;
        padding: 4px;
        line-height: 1;
    }
    .chat-close:hover {
        color: #333;
    }
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: #f8f9fa;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .message-assistant {
        align-self: flex-start;
        max-width: 75%;
        background: #e9ecef;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        color: #333;
        line-height: 1.5;
    }
    .message-user {
        align-self: flex-end;
        max-width: 75%;
        background: linear-gradient(135deg, #ff6b9d, #ff8fab);
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        color: white;
        line-height: 1.5;
    }
    .message-time {
        font-size: 11px;
        color: #999;
        margin-top: 4px;
        text-align: right;
    }
    .chat-input-area {
        padding: 16px;
        background: white;
        border-top: 1px solid #e5e5e5;
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .chat-input {
        flex: 1;
        padding: 10px 16px;
        border: 1px solid #e5e5e5;
        border-radius: 24px;
        font-size: 14px;
        outline: none;
    }
    .chat-input:focus {
        border-color: #ff6b9d;
    }
    .chat-send {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff6b9d, #ff8fab);
        border: none;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        transition: transform 0.2s;
    }
    .chat-send:hover {
        transform: scale(1.1);
    }
    .chat-send:active {
        transform: scale(0.95);
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
if 'chat_window_open' not in st.session_state:
    st.session_state['chat_window_open'] = False
if 'llm_provider' not in st.session_state:
    st.session_state['llm_provider'] = 'gemini'

# ==========================================
# 3. LLM 功能函数 (Gemini 集成)
# ==========================================

def get_page_context() -> str:
    """获取当前页面上下文信息，用于 LLM 提示"""
    context = f"当前页面: {st.session_state.get('current_page', 'Home')}\n"
    
    df = st.session_state.get('df_data')
    if df is not None:
        context += f"数据概览: 共 {len(df)} 行记录\n"
        context += f"数据列: {', '.join(df.columns.tolist())}\n"
        
        # 根据当前页面添加特定信息
        current_page = st.session_state.get('current_page', 'Home')
        if current_page == 'Customer Analysis':
            # 可以添加当前选中的客户信息等
            pass
        elif current_page == 'Data Analysis':
            # 可以添加当前筛选条件等
            pass
    
    return context

def call_gemini(messages: List[Dict], api_key: str, model: str = 'gemini-pro') -> Optional[str]:
    """调用 Google Gemini API"""
    if not GEMINI_AVAILABLE:
        return "❌ 未安装 google-generativeai 库，请运行: pip install google-generativeai"
    
    if not api_key:
        return "❌ 请设置环境变量 GEMINI_API_KEY。获取 API Key: https://makersuite.google.com/app/apikey"
    
    try:
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        # 将消息格式转换为 Gemini 格式
        # Gemini 使用简单的 prompt 格式，我们需要将对话历史转换为单一 prompt
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

def render_chat_sidebar():
    """侧边栏占位函数（已移除配置选项，API Key 从环境变量读取）"""
    # 配置选项已移除，API Key 从环境变量 GEMINI_API_KEY 读取
    pass

def toggle_chat_window():
    """切换聊天窗口显示状态"""
    st.session_state['chat_window_open'] = not st.session_state['chat_window_open']

def close_chat_window():
    """关闭聊天窗口"""
    st.session_state['chat_window_open'] = False

def render_floating_chat():
    """渲染浮动聊天窗口"""
    # 聊天启动按钮
    if not st.session_state['chat_window_open']:
        # 添加浮动按钮
        st.markdown("""
        <style>
            .floating-chat-launcher {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
            }
            .floating-chat-launcher-btn {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #ff6b9d, #ff8fab);
                box-shadow: 0 4px 12px rgba(255, 107, 157, 0.4);
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .floating-chat-launcher-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(255, 107, 157, 0.6);
            }
        </style>
        <div class="floating-chat-launcher">
            <button class="floating-chat-launcher-btn" id="chatLauncherBtn">💬</button>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const btn = document.getElementById('chatLauncherBtn');
                if (btn) {
                    btn.onclick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        // 使用 URL 参数触发 Streamlit 重新运行
                        const baseUrl = window.location.href.split('?')[0];
                        const newUrl = baseUrl + '?openChat=true&_t=' + Date.now();
                        window.location.href = newUrl;
                        return false;
                    };
                }
            });
        </script>
        """, unsafe_allow_html=True)
    
    # 聊天窗口
    if st.session_state['chat_window_open']:
        # 构建消息HTML
        messages_html = ""
        chat_display = [m for m in st.session_state['chat_messages'] if m.get('role') != 'system'][-20:]  # 显示最后20条消息
        
        for msg in chat_display:
            role = msg.get('role', 'user')
            content = msg.get('content', '').replace('\n', '<br>').replace('"', '&quot;')
            if role == 'user':
                messages_html += f'<div class="message-user">{content}</div>'
            elif role == 'assistant':
                messages_html += f'<div class="message-assistant">{content}</div>'
        
        # 如果没有消息，显示欢迎消息
        if not messages_html:
            messages_html = '<div class="message-assistant">你好！👋 我是供应链 AI 助手，有什么可以帮助你的吗？</div>'
        
        st.markdown(f"""
        <div class="chat-widget-container">
            <div class="chat-window">
                <div class="chat-header">
                    <div class="chat-header-left">
                        <div class="chat-icon">✨</div>
                        <div class="chat-title">AI 智能助手</div>
                    </div>
                    <button class="chat-close" id="closeChatBtn">×</button>
                </div>
                <div class="chat-messages" id="chatMessages">
                    {messages_html}
                </div>
                <div class="chat-input-area">
                    <input type="text" class="chat-input" id="chatInput" placeholder="输入您的问题...">
                    <button class="chat-send" id="sendBtn">➤</button>
                </div>
            </div>
        </div>
        <script>
            // 自动滚动到底部
            setTimeout(function() {{
                const messagesDiv = document.getElementById('chatMessages');
                if (messagesDiv) {{
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }}
            }}, 100);
            
            // 关闭按钮 - 使用 Streamlit 通信
            document.getElementById('closeChatBtn').addEventListener('click', function() {{
                // 通过隐藏的 Streamlit 组件触发关闭
                const event = new CustomEvent('streamlit:closeChat');
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'close'}}, '*');
                // 备用方案：使用 URL 参数
                const baseUrl = window.location.href.split('?')[0];
                window.location.href = baseUrl + '?closeChat=true&t=' + Date.now();
            }});
            
            // 发送按钮
            document.getElementById('sendBtn').addEventListener('click', function() {{
                sendMessage();
            }});
            
            // Enter 键发送
            document.getElementById('chatInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    e.preventDefault();
                    sendMessage();
                }}
            }});
            
            function sendMessage() {{
                const input = document.getElementById('chatInput');
                const message = input.value.trim();
                if (message) {{
                    const baseUrl = window.location.href.split('?')[0];
                    window.location.href = baseUrl + '?sendMessage=' + encodeURIComponent(message) + '&t=' + Date.now();
                }}
            }}
        </script>
        """, unsafe_allow_html=True)

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
    st.button("🏠 返回主页", on_click=navigate_to, args=('Home',), use_container_width=True)
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

    # 3. 图表
    st.subheader("📈 供需趋势对比")
    daily_chart = filtered_df.groupby('Date')[["Actual_Qty", "Forecast_Qty"]].sum().reset_index()
    fig_trend = px.line(daily_chart, x='Date', y=['Actual_Qty', 'Forecast_Qty'], 
                        color_discrete_map={"Actual_Qty": "#3366cc", "Forecast_Qty": "#ff9900"})
    fig_trend.update_layout(legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_trend, use_container_width=True)

# --- 4.3 页面二：客户分析 ---
def page_customer_analysis():
    st.button("🏠 返回主页", on_click=navigate_to, args=('Home',), use_container_width=True)
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
    st.button("🏠 返回主页", on_click=navigate_to, args=('Home',), use_container_width=True)
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
# 6. 主程序入口 (路由控制)
# ==========================================
def main():
    # 渲染侧边栏配置
    render_chat_sidebar()
    
    # 处理聊天窗口控制（使用 query_params）
    # 检查是否有 openChat 参数
    if hasattr(st, 'query_params'):
        if 'openChat' in st.query_params:
            if not st.session_state.get('_chat_opened', False):
                st.session_state['chat_window_open'] = True
                st.session_state['_chat_opened'] = True
                st.rerun()
        
        # 检查是否有 closeChat 参数
        if 'closeChat' in st.query_params:
            if st.session_state.get('_chat_opened', False):
                st.session_state['chat_window_open'] = False
                st.session_state['_chat_opened'] = False
                st.rerun()
        
        # 处理发送消息
        if 'sendMessage' in st.query_params:
            user_message = st.query_params['sendMessage']
            if user_message:
                provider = st.session_state.get('llm_provider', 'gemini')
                response = chat_with_llm(user_message, provider)
                st.rerun()
    else:
        # 如果 query_params 不可用，初始化标记
        if '_chat_opened' not in st.session_state:
            st.session_state['_chat_opened'] = False
    
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