#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像识别程序 - 支持多提供商（阿里云百炼、OpenAI、智谱AI）
"""

import json
import os
import sys
import re
import base64
import argparse
import glob
from datetime import datetime, timedelta
import requests


def get_mime_type(file_path):
    """根据文件扩展名返回对应的 MIME 类型"""
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
    }
    return mime_map.get(ext, 'image/jpeg')


def expand_env_vars(value):
    """展开配置中的 ${VAR} 环境变量引用"""
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    
    if not os.path.exists(config_path):
        print(f"错误: 配置文件 {config_path} 不存在")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    provider = config.get('provider', 'aliyun')
    providers = config.get('providers', {})
    
    if provider not in providers:
        print(f"错误: 未知提供商 '{provider}'，可选: {list(providers.keys())}")
        sys.exit(1)
    
    provider_config = providers[provider]
    
    # 展开环境变量引用
    for key in ('api_key', 'api_base_url', 'model_name'):
        if key in provider_config:
            provider_config[key] = expand_env_vars(provider_config[key])
    
    if not provider_config.get('api_key') or \
       provider_config['api_key'].startswith('sk-你的') or \
       provider_config['api_key'].startswith('你的') or \
       provider_config['api_key'].startswith('${') or \
       '-your-' in provider_config['api_key']:
        print(f"错误: 请先在 config.json 中配置 {provider} 的 API Key，"
              f"填入你自己的真实密钥")
        sys.exit(1)
    
    return config


def get_provider_config(config):
    """获取当前提供商的配置"""
    provider = config.get('provider', 'aliyun')
    return config.get('providers', {}).get(provider, {})


def image_to_base64(image_path):
    """将图片转换为base64编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')


# ==================== 请求构建 ====================

def build_request_aliyun(config, image_base64, mime_type, prompt_text):
    """构建阿里云百炼请求"""
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": config["model_name"],
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:{mime_type};base64,{image_base64}"},
                        {"text": prompt_text}
                    ]
                }
            ]
        }
    }
    return headers, payload


def build_request_openai(config, image_base64, mime_type, prompt_text):
    """构建 OpenAI 请求"""
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": config["model_name"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
                ]
            }
        ]
    }
    return headers, payload


def build_request_zhipuai(config, image_base64, mime_type, prompt_text):
    """构建智谱AI请求"""
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": config["model_name"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
    }
    return headers, payload


# ==================== 响应解析 ====================

def parse_response_aliyun(result):
    """解析阿里云百炼响应"""
    if 'output' in result and 'choices' in result['output']:
        return result['output']['choices'][0]['message']['content'][0]['text']
    return None


def parse_response_openai(result):
    """解析 OpenAI 响应"""
    if 'choices' in result and len(result['choices']) > 0:
        content = result['choices'][0].get('message', {}).get('content', '')
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    return item['text']
            return str(content)
        elif isinstance(content, str):
            return content
    return None


def parse_response_zhipuai(result):
    """解析智谱AI响应"""
    if 'data' in result and 'choices' in result['data'] and len(result['data']['choices']) > 0:
        return result['data']['choices'][0].get('message', {}).get('content', '')
    return None


# ==================== 主识别逻辑 ====================

def recognize_image(image_path, config, prompt_text=None):
    """根据提供商识别图像"""
    provider_config = get_provider_config(config)
    provider = config.get('provider', 'aliyun')
    
    # 获取默认提示词
    if not prompt_text:
        prompt_text = provider_config.get('default_prompt', '请详细描述这张图片中的内容。')
    
    # 检查图片文件
    if not os.path.exists(image_path):
        print(f"错误: 图片文件 {image_path} 不存在")
        return None, None
    
    # 获取 base64 和 MIME
    image_base64 = image_to_base64(image_path)
    mime_type = get_mime_type(image_path)
    
    # 根据提供商构建请求
    if provider == 'aliyun':
        build_func = build_request_aliyun
        parse_func = parse_response_aliyun
        provider_name = '阿里云百炼'
    elif provider == 'openai':
        build_func = build_request_openai
        parse_func = parse_response_openai
        provider_name = 'OpenAI'
    elif provider == 'zhipuai':
        build_func = build_request_zhipuai
        parse_func = parse_response_zhipuai
        provider_name = '智谱AI'
    elif provider in ('agnes', 'AGNES'):
        build_func = build_request_openai
        parse_func = parse_response_openai
        provider_name = 'Agnes'
    else:
        # 默认使用 OpenAI 兼容格式（大多数现代 API 都支持）
        build_func = build_request_openai
        parse_func = parse_response_openai
        provider_name = provider
    
    headers, payload = build_func(provider_config, image_base64, mime_type, prompt_text)
    
    try:
        print(f"正在识别图片: {image_path}")
        print(f"使用提供商: {provider_name}")
        print(f"使用模型: {provider_config['model_name']}")
        
        response = requests.post(
            provider_config['api_base_url'],
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = parse_func(result)
            if content:
                return content, prompt_text
            else:
                print(f"API返回格式异常: {result}")
                return None, None
        else:
            print(f"API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None, None
            
    except requests.exceptions.Timeout:
        print("错误: 请求超时，请检查网络连接")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"错误: 网络请求失败 - {e}")
        return None, None
    except Exception as e:
        print(f"错误: {e}")
        return None, None


def save_result(image_path, result, prompt_text=None):
    """保存识别结果到txt文件"""
    
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{image_name}_result_{timestamp}.txt"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"图像识别结果\n")
        f.write(f"{'='*50}\n\n")
        f.write(f"图片路径: {image_path}\n")
        if prompt_text:
            f.write(f"使用提示词: {prompt_text}\n")
        f.write(f"识别时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"识别结果:\n")
        f.write(f"{'-'*50}\n")
        f.write(result)
        f.write(f"\n{'-'*50}\n")
    
    print(f"\n结果已保存到: {output_path}")
    return output_path


def cleanup_output(text):
    """轻量清理：去除 Markdown 标记和 emoji，保留可读文字"""
    if not text:
        return text
    # 去除加粗/斜体标记
    text = text.replace('**', '').replace('__', '')
    # 去除 Markdown 链接标记
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 去除 Markdown 引用
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # 去除 emoji 和特殊符号（逐步添加）
    for ch in ['✅', '📌', '🔹', '🔸', '➡', '➤', '▸', '◆', '◇', '●', '○',
               '🎯', '🎉', '😊', '👍', '👏', '🌟', '⭐', '💡', '📝', '📊',
               '🔍', '🔗', '🛠', '⚙', '📁', '📂', '📄', '📑', '📈', '📉',
               '🔴', '🟢', '🟡', '🟠', '🔵', '🟣', '🟤', '⬛', '⬜', '🔲',
               '🔳', '▪', '▫', '☑', '✔', '✖', '❌', '❓', '❗']:
        text = text.replace(ch, '')
    # 去除剩余常见带圈数字/字母等 Unicode 装饰
    text = re.sub(r'[\u2000-\u206F\u2100-\u214F\u2190-\u21FF\u2300-\u23FF'
                  r'\u2460-\u24FF\u2500-\u257F\u2580-\u259F\u25A0-\u25FF'
                  r'\u2600-\u26FF\u2700-\u27BF\u27C0-\u27EF\u27F0-\u27FF'
                  r'\u2900-\u297F\u2980-\u29FF\u2A00-\u2AFF'
                  r'\U0001D000-\U0001D0FF\U0001D100-\U0001D1FF'
                  r'\U0001D200-\U0001D2FF\U0001D300-\U0001D3FF'
                  r'\U0001D400-\U0001D7FF\U0001F000-\U0001F9FF'
                  r'\U0001FA00-\U0001FAFF\U0001FB00-\U0001FBFF]', '', text)
    # 合并多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 去除行首尾空白
    lines = [l.strip() for l in text.split('\n')]
    text = '\n'.join(lines)
    return text.strip()


def cleanup_old_results(days=7):
    """删除项目目录下超过指定天数的 *_result_*.txt 文件"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    cutoff = datetime.now() - timedelta(days=days)
    pattern = os.path.join(project_dir, '*_result_*.txt')
    for f in glob.glob(pattern):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(f))
            if mtime < cutoff:
                os.remove(f)
                print(f"清理旧结果文件: {f}")
        except (OSError, ValueError):
            pass


def main():
    """主函数"""
    
    # 设置 stdout 编码为 UTF-8 避免 GBK 打印 emoji/中文出错
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    
    # 启动时清理超过7天的旧结果文件
    cleanup_old_results(days=7)
    
    parser = argparse.ArgumentParser(description="多提供商图像识别工具（支持阿里云/OpenAI/智谱AI）")
    parser.add_argument("image_path", help="图片路径")
    parser.add_argument("-p", "--prompt", help="自定义识别提示词（覆盖默认的提供商提示词）")
    args = parser.parse_args()
    
    image_path = args.image_path
    
    # 加载配置
    config = load_config()
    provider = config.get('provider', 'aliyun')
    
    # 识别图像
    result, used_prompt = recognize_image(image_path, config, prompt_text=args.prompt)
    
    if result:
        # 清理花哨格式，保留可读纯文字
        clean = cleanup_output(result)
        print("\n识别结果:")
        print("-" * 50)
        print(clean)
        print("-" * 50)
        
        # 保存结果（原始内容，未处理）
        
        # 保存结果
        save_result(image_path, result, prompt_text=used_prompt)
    else:
        print("\n识别失败，请检查图片路径和API配置")
        sys.exit(1)


if __name__ == "__main__":
    main()
