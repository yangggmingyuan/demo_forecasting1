"""CSS 样式定义模块"""

def load_styles():
    """加载并注入企业级 SaaS 风格 CSS"""
    return """
<style>
    /* 全局样式 */
    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    [data-testid="collapsedControl"] {
        display: none;
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
    
    /* 1. 将 Popover 容器定位到右下角 */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 40px !important;
        right: 40px !important;
        z-index: 99999 !important;
        width: 80px !important;
        height: 80px !important;
    }

    /* 2. 美化触发按钮为圆形、蓝色渐变 + 呼吸动画 */
    @keyframes pulse-animation {
        0% { box-shadow: 0 0 0 0 rgba(78, 115, 223, 0.7); transform: scale(1); }
        70% { box-shadow: 0 0 0 15px rgba(78, 115, 223, 0); transform: scale(1.05); }
        100% { box-shadow: 0 0 0 0 rgba(78, 115, 223, 0); transform: scale(1); }
    }

    [data-testid="stPopover"] > button {
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #4e73df 0%, #224abe 100%) !important;
        border: 2px solid #ffffff !important;
        color: white !important;
        font-size: 40px !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        animation: pulse-animation 3s infinite !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease !important;
    }

    /* 3. 尝试隐藏按钮内的默认箭头/Chevron (通常是 SVG 或 span) */
    [data-testid="stPopover"] > button > div > span {
        display: none !important; 
    }
    /* SVG usually handles the arrow in some versions */
    [data-testid="stPopover"] > button svg {
        display: none !important;
    }
    /* Ensure the text/emoji is visible and centered */
    [data-testid="stPopover"] > button > div {
       display: flex !important;
       width: 100% !important;
       height: 100% !important;
       justify-content: center !important;
       align-items: center !important;
    }

    [data-testid="stPopover"] > button:hover {
        transform: scale(1.1) !important;
        background: linear-gradient(135deg, #375a7f 0%, #1a3a9f 100%) !important;
        border-color: #f8f9fa !important;
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
"""

