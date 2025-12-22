"""Gemini API 集成模块"""
from typing import List, Dict, Optional

# 尝试导入 Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def call_gemini(messages: List[Dict], api_key: str, model: str = 'gemini-1.5-flash') -> Optional[str]:
    """调用 Google Gemini API，支持模型回退机制"""
    if not GEMINI_AVAILABLE:
        return "❌ 未安装 google-generativeai 库，请运行: pip install google-generativeai"
    
    # 确保 API Key 有值：优先使用传入的参数，然后尝试从环境变量获取，最后使用默认值
    import os
    default_key = 'AIzaSyBxt-RJNa2WWsMyGcLH1aIsxATGlHZx2Fo'
    
    # 如果传入的 API Key 为空，尝试从环境变量获取
    if not api_key or api_key.strip() == '':
        api_key = os.getenv('GEMINI_API_KEY', '')
    
    # 如果仍然为空，使用默认值
    if not api_key or api_key.strip() == '':
        api_key = default_key
    
    # 最终验证：如果 API Key 仍然为空（理论上不应该发生），返回友好提示
    if not api_key or api_key.strip() == '':
        return "❌ 无法获取 API Key。请设置环境变量 GEMINI_API_KEY，或联系管理员配置默认 API Key"
    
    # 验证 API Key 格式（Google Gemini API Key 通常以 'AIza' 开头）
    if not api_key.startswith('AIza'):
        return "❌ API Key 格式无效。Google Gemini API Key 应以 'AIza' 开头。请检查您的 API Key 是否正确"
    
    # 定义模型回退列表（按优先级排序）
    model_fallback_list = [model]
    if model == 'gemini-1.5-flash':
        model_fallback_list.extend(['gemini-1.5-pro', 'gemini-pro'])
    elif model == 'gemini-1.5-pro':
        model_fallback_list.extend(['gemini-1.5-flash', 'gemini-pro'])
    else:
        model_fallback_list.extend(['gemini-1.5-flash', 'gemini-1.5-pro'])
    
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
    
    full_prompt = '\n'.join(prompt_parts)
    
    # 尝试使用模型列表中的模型，如果失败则回退到下一个
    last_error = None
    for current_model in model_fallback_list:
        try:
            genai.configure(api_key=api_key)
            model_instance = genai.GenerativeModel(current_model)
            
            # 生成响应
            response = model_instance.generate_content(full_prompt)
            
            # 检查响应是否有效
            if response and hasattr(response, 'text') and response.text:
                return response.text
            else:
                # 如果响应为空，尝试下一个模型
                if current_model != model_fallback_list[-1]:
                    continue
                return "❌ Gemini API 返回了空响应"
                
        except Exception as e:
            error_msg = str(e)
            last_error = error_msg
            
            # 如果是模型不存在错误，尝试下一个模型
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                if current_model != model_fallback_list[-1]:
                    continue  # 尝试下一个模型
            
            # 如果是 API Key 错误，直接返回，不尝试其他模型
            if "API_KEY" in error_msg or "api key" in error_msg.lower() or "invalid" in error_msg.lower():
                if "invalid api key" in error_msg.lower() or "api key not valid" in error_msg.lower():
                    return "❌ API Key 无效。当前使用的 API Key 可能已过期或被撤销。\n\n解决方案：\n1. 设置环境变量 GEMINI_API_KEY 为您的有效 API Key\n2. 或联系管理员更新默认 API Key\n\n获取 API Key：https://makersuite.google.com/app/apikey"
                elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
                    return "❌ API Key 权限不足。当前 API Key 可能没有访问此模型的权限。\n\n解决方案：\n1. 检查 API Key 的权限设置\n2. 使用具有相应权限的 API Key"
                return "❌ API Key 验证失败。请检查您的 API Key 配置是否正确"
            
            # 如果是配额错误，直接返回
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "❌ API 调用次数已达上限，请稍后再试"
            
            # 如果是最后一个模型也失败了，返回错误
            if current_model == model_fallback_list[-1]:
                # 提供更友好的错误信息
                if "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
                    return "❌ 没有权限访问此模型，请检查 API Key 权限"
                elif "rate limit" in error_msg.lower():
                    return "❌ 请求过于频繁，请稍后再试"
                else:
                    return f"❌ Gemini API 调用失败: {error_msg}"
    
    # 如果所有模型都失败了，返回最后一个错误
    return f"❌ 所有模型尝试均失败，最后错误: {last_error}"

