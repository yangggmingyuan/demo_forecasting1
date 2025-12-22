"""供应链 AI 决策大脑 - 主应用入口"""
# Force Reload Trigger
import streamlit as st

# 导入配置模块
from config.styles import load_styles
from config.state import init_session_state

# 导入页面模块
from pages.home import page_home
from pages.data_analysis import page_data_analysis
from pages.customer_analysis import page_customer_analysis
from pages.inventory_strategy import page_inventory_strategy

# 导入聊天模块
from llm.chat import render_floating_chat

# ==========================================
# 页面配置与样式加载
# ==========================================
st.set_page_config(page_title="供应链 AI 决策大脑", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

# 加载 CSS 样式
st.markdown(load_styles(), unsafe_allow_html=True)

# ==========================================
# Session State 初始化
# ==========================================
init_session_state()

# ==========================================
# 主程序入口 (路由控制)
# ==========================================
def main():
    """主函数：处理路由和页面渲染"""
    # 渲染浮动聊天窗口
    render_floating_chat()

    # 路由逻辑
    current_page = st.session_state.get('current_page', 'Home')
    
    if current_page == 'Home':
        page_home()
    elif current_page == 'Data Analysis':
        page_data_analysis()
    elif current_page == 'Customer Analysis':
        page_customer_analysis()
    elif current_page == 'Inventory Strategy':
        page_inventory_strategy()


if __name__ == "__main__":
    main()

