"""Local Qwen2.5 Integration Module"""
import requests
import json
import streamlit as st
from typing import List, Dict, Optional

def call_qwen_local(
    messages: List[Dict], 
    api_base: str = "http://localhost:11434/v1", 
    model_name: str = "qwen2.5", 
    api_key: str = "sk-no-key-required"
) -> Optional[str]:
    """
    Call a local LLM via OpenAI-compatible API (e.g., Ollama, LM Studio).
    
    Args:
        messages: List of message dicts {'role': '...', 'content': '...'}
        api_base: Base URL for the API (e.g., http://localhost:11434/v1)
        model_name: Name of the model to use
        api_key: API Key (usually ignored by local servers like Ollama)
        
    Returns:
        The content of the assistant's response, or an error message string.
    """
    
    # Ensure api_base doesn't end with slash to avoid double slashes
    if api_base.endswith('/'):
        api_base = api_base[:-1]
        
    url = f"{api_base}/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        # Explicitly disable proxies for localhost requests to avoid 502/Proxy errors
        proxies = {"http": None, "https": None}
        response = requests.post(url, headers=headers, json=payload, timeout=60, proxies=proxies)
        
        if response.status_code == 200:
            data = response.json()
            # Handle standard OpenAI format
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                return content
            else:
                return f"❌ 响应格式未知: {str(data)}"
        else:
            return f"❌ API 请求失败: Status {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return f"❌ 无法连接到本地服务 ({api_base})。\n请确保:\n1. 本地 LLM 服务 (如 Ollama) 已启动\n2. 地址配置正确 (默认: http://localhost:11434/v1)"
    except requests.exceptions.Timeout:
        return "❌ 请求超时。本地模型响应时间过长。"
    except Exception as e:
        return f"❌ 发生意外错误: {str(e)}"

def get_ollama_models(api_base: str = "http://localhost:11434") -> List[str]:
    """Get list of available models from Ollama"""
    try:
        # Note: Ollama API is usually at /api/tags, distinct from OpenAI /v1
        # If api_base is .../v1, strip it
        base_url = api_base.replace("/v1", "")
        response = requests.get(f"{base_url}/api/tags", timeout=1, proxies={"http": None, "https": None})
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
    except Exception:
        pass
    return []
