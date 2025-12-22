"""导航辅助函数"""
import streamlit as st


def navigate_to(page):
    """导航到指定页面"""
    st.session_state['current_page'] = page

