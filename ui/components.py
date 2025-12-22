"""可复用的 UI 组件函数"""
import streamlit as st


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

