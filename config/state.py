"""Session State 初始化和管理模块"""
import streamlit as st
import os


def init_session_state():
    """初始化所有 Session State 变量"""
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Home'
    if 'df_data' not in st.session_state:
        st.session_state['df_data'] = None
    # LLM 相关 Session State
    if 'chat_messages' not in st.session_state:
        st.session_state['chat_messages'] = []
    # 初始化或更新 API Key（如果不存在或为空，使用默认值）
    # 优先使用环境变量，如果没有则使用代码中的默认值
    default_key = 'AIzaSyBxt-RJNa2WWsMyGcLH1aIsxATGlHZx2Fo'
    env_key = os.getenv('GEMINI_API_KEY', '')
    
    # 确保 API Key 始终有值
    # 每次调用时都检查，确保即使 session_state 中的值为空也会重新设置
    current_key = st.session_state.get('gemini_api_key', '')
    
    # 如果不存在、为空或格式不正确，重新设置
    if (not current_key or 
        current_key.strip() == '' or 
        not current_key.startswith('AIza')):
        # 优先使用环境变量，如果没有则使用默认值
        if env_key and env_key.strip() != '':
            st.session_state['gemini_api_key'] = env_key
        elif default_key and default_key.strip() != '':
            st.session_state['gemini_api_key'] = default_key
        else:
            # 如果默认值也为空（理论上不应该发生），设置为空字符串
            st.session_state['gemini_api_key'] = ''
    if 'gemini_model' not in st.session_state:
        st.session_state['gemini_model'] = 'gemini-1.5-flash'
    if 'llm_provider' not in st.session_state:
        st.session_state['llm_provider'] = 'gemini'
