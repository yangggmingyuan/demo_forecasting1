"""首页模块"""
import streamlit as st
import pandas as pd
import os
from utils.navigation import navigate_to


def page_home():
    """首页：数据上传和模块选择"""
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

