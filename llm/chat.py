"""聊天功能模块"""
import streamlit as st
from typing import List, Dict
from llm.gemini import call_gemini
from llm.qwen_local import call_qwen_local


def get_page_context() -> str:
    """获取当前页面上下文信息，用于 LLM 提示"""
    context = f"当前页面: {st.session_state.get('current_page', 'Home')}\n"
    
    df = st.session_state.get('df_data')
    if df is not None:
        context += f"数据概览: 共 {len(df)} 行记录\n"
        context += f"数据列: {', '.join(df.columns.tolist())}\n"
    return context


def chat_with_llm(user_message: str, provider: str = 'qwen_local') -> str:
    """与 LLM 进行对话"""
    # 获取页面上下文
    page_context = get_page_context()
    
    # 构建系统提示
    system_prompt = f"""你是一个专业的供应链数据分析助手。你的任务是帮助用户理解供应链数据和分析结果。

当前上下文信息:
{page_context}

请用中文回答用户的问题，提供专业、清晰的分析和建议。"""
    
    # 初始化消息列表（如果为空）
    if 'chat_messages' not in st.session_state:
        st.session_state['chat_messages'] = []

    # 确保第一条是 System Prompt
    if not st.session_state['chat_messages'] or st.session_state['chat_messages'][0].get('role') != 'system':
         st.session_state['chat_messages'].insert(0, {'role': 'system', 'content': system_prompt})
    else:
         st.session_state['chat_messages'][0]['content'] = system_prompt

    
    # 添加用户消息
    st.session_state['chat_messages'].append({
        'role': 'user',
        'content': user_message
    })
    
    # 调用 LLM
    response = None
    
    # 强制使用 Qwen Local
    # Local Qwen Logic
    api_base = st.session_state.get('qwen_api_base', 'http://localhost:11434/v1')
    model_name = st.session_state.get('qwen_model_name', 'qwen2.5:14b')
    
    # Auto-detect model if we are using a likely incorrect default or if previous call failed
    # We do this check once if the model name seems like a default guess
    from llm.qwen_local import get_ollama_models
    
    # Check if we should try to auto-detect (e.g., first run or default value)
    if 'qwen_model_autodetected' not in st.session_state:
        available_models = get_ollama_models(api_base)
        if available_models:
            # Try to find a qwen model
            best_match = next((m for m in available_models if 'qwen' in m.lower()), None)
            if best_match:
                model_name = best_match
            else:
                model_name = available_models[0] # Fallback to whatever is installed
            
            # Update session state so we use this valid model
            st.session_state['qwen_model_name'] = model_name
            st.session_state['qwen_model_autodetected'] = True
    
    response = call_qwen_local(
        messages=st.session_state['chat_messages'],
        api_base=api_base,
        model_name=model_name
    )
    
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
    修复版：使用 st.popover + st.text_input + st.button，解决 st.chat_input 在 popover 内不工作的问题。
    """
    
    # --- 核心修改：加入这段 CSS 来放大按钮 ---
    st.markdown("""
    <style>
        /* 找到所有的 Popover 按钮并放大 */
        div[data-testid="stPopover"] > button {
            font-size: 3rem !important;  /* 图标/字体大小：这里改成了 3倍大小 */
            width: 80px !important;      /* 按钮宽度 */
            height: 80px !important;     /* 按钮高度 */
            border-radius: 50% !important; /* 可选：设为 50% 会变成圆形按钮，不写这行就是圆角矩形 */
            border: 2px solid #4e73df !important; /* 可选：加个边框颜色 */
            background-color: white !important; /* Ensure background is visible if gradient fails */
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        }
        
        /* Position Fix (Optional, ensuring it stays in bottom right) */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 40px !important;
            right: 40px !important;
            z-index: 99999 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    # -------------------------------------
    
    # 强制 Provider 为 qwen_local
    st.session_state['llm_provider'] = 'qwen_local'

    with st.popover("🤖", help="AI 智能助手"):
        st.markdown(
            """
            <div style="
                padding: 15px 0px; 
                font-weight: 800; 
                font-size: 1.4rem; 
                border-bottom: 2px solid #f0f0f0; 
                margin-bottom: 15px;
                background: linear-gradient(to right, #4e73df, #36b9cc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                ✨ 供应链数据助手 <span style="-webkit-text-fill-color: #888; font-size: 0.8rem; font-weight: normal; margin-left: auto;">(Local AI)</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        


        # Chat Container
        chat_container = st.container(height=350)
        
        with chat_container:
            messages_to_show = [msg for msg in st.session_state.get('chat_messages', []) if msg.get('role') != 'system']
            if not messages_to_show:
                st.info("👋 您好！我是您的本地数据分析助手。")
            
            for msg in messages_to_show:
                with st.chat_message(msg['role'], avatar="🧑‍💻" if msg['role'] == "user" else "🤖"):
                    st.markdown(msg['content'])

        # Input Area
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                user_input = st.text_input(
                    "输入您的问题...",
                    key="chat_input_text",
                    label_visibility="collapsed",
                    placeholder="输入您的问题..."
                )
            with col2:
                submitted = st.form_submit_button("发送", use_container_width=True)
            
            if submitted and user_input and user_input.strip():
                prompt = user_input.strip()
                
                # Show spinner while thinking
                with st.spinner("思考中..."):
                    chat_with_llm(prompt, provider='qwen_local')
                st.rerun()

