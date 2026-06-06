# 图像识别程序

基于阿里云百炼 / OpenAI / Agnes / 智谱AI 等多提供商图像识别命令行工具，集成 Reasonix Desktop 全局 Skill，可直接在对话中识图并回答。

---

## 功能特性

- 支持多提供商：阿里云百炼、OpenAI、Agnes、智谱AI
- 支持未知提供商自动回退为 OpenAI 兼容格式
- 支持详细描述 / 自定义提问（`-p` 参数）
- API Key 支持环境变量引用（如 `${AGNES_API_KEY}`），跨设备安全分发
- 自动保存识别结果到 txt 文件（附带使用的提示词）
- 配置文件管理 API 密钥和模型参数
- 启动时自动清理超过 7 天的旧结果文件
- 自动检测图片格式（jpg/png/gif/bmp/webp）
- 失败时返回非零退出码
- 集成 Reasonix Desktop 全局 Skill：`/view_image @图片`
- **全局目录（任何项目下可用）**，无绝对路径依赖

---

## 文件结构

```
项目目录/
├── README.md                  # 本文档
├── image_recognizer.py        # 识别程序（主脚本）
├── config.json                # API 配置（多提供商）
├── requirements.txt           # Python 依赖
└── image.png                  # 测试图片

全局 Skill（任何项目下可用）:
~/.reasonix/skills/view_image/
├── SKILL.md                   # Skill 指令
├── image_recognizer.py        # 识别脚本（与项目根同步）
└── config.json                # API 配置（与项目根同步）

桌面独立运行包:
~/Desktop/view_image/
├── SKILL.md
├── image_recognizer.py
├── config.json
└── README.md                  # 本文档
```

---

## 安装

```bash
pip install -r requirements.txt
```

### 配置提供商

编辑 `config.json`，修改 `"provider"` 字段选择使用哪个提供商：

```json
{
    "provider": "aliyun",
    "providers": {
        "aliyun": {
            "api_key": "sk-你的百炼API Key",
            "model_name": "qwen3.5-omni-plus-2026-03-15",
            "api_base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        }
    }
}
```

API Key 支持环境变量引用（如 `"${AGNES_API_KEY}"`），方便跨设备安全分发。
如果使用的提供商不在预定义列表中，脚本会自动按 OpenAI 兼容格式发送请求。

---

## 支持的提供商

| 提供商 | 可用模型 | API Key 格式 |
|:---|:---|:---|
| **阿里云百炼** | qwen3.5-omni-plus-2026-03-15, qwen-vl-plus, qwen-vl-max | `sk-xxx` |
| **OpenAI** | gpt-4o, gpt-4-turbo | `sk-xxx` |
| **Agnes** | agnes-2.0-flash | `${AGNES_API_KEY}`（环境变量） |
| **智谱AI** | glm-4v-plus | `xxx` |

### 阿里云百炼配置

```json
{
    "provider": "aliyun",
    "providers": {
        "aliyun": {
            "api_key": "sk-你的百炼API Key",
            "model_name": "qwen3.5-omni-plus-2026-03-15",
            "api_base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        }
    }
}
```

### OpenAI 配置

```json
{
    "provider": "openai",
    "providers": {
        "openai": {
            "api_key": "sk-你的OpenAI Key",
            "model_name": "gpt-4o",
            "api_base_url": "https://api.openai.com/v1/chat/completions"
        }
    }
}
```

### Agnes 配置

```json
{
    "provider": "agnes",
    "providers": {
        "agnes": {
            "api_key": "${AGNES_API_KEY}",
            "model_name": "agnes-2.0-flash",
            "api_base_url": "https://apihub.agnes-ai.com/v1/chat/completions"
        }
    }
}
```

需在系统环境变量中设置 `AGNES_API_KEY`。

### 智谱AI配置

```json
{
    "provider": "zhipuai",
    "providers": {
        "zhipuai": {
            "api_key": "你的智谱AI Key",
            "model_name": "glm-4v-plus",
            "api_base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        }
    }
}
```

### 任意 OpenAI 兼容提供商

脚本对于不在预定义列表中的提供商自动按 OpenAI 兼容格式发送请求。只需在 `config.json` 中添加配置并切换 `"provider"` 字段即可：

```json
{
    "provider": "你的提供商名称",
    "providers": {
        "你的提供商名称": {
            "api_key": "你的API Key",
            "model_name": "你的模型名",
            "api_base_url": "https://你的接口地址/v1/chat/completions"
        }
    }
}
```

### 获取 API Key

- **阿里云百炼**：[百炼控制台](https://bailian.console.aliyun.com/)
- **OpenAI**：[OpenAI Dashboard](https://platform.openai.com/api-keys)
- **Agnes**：通过 Agnes 平台获取
- **智谱AI**：[智谱开放平台](https://open.bigmodel.cn/)

---

## 使用方法

### 命令行直接使用

```bash
# 基本识别（使用 config.json 中配置的默认提供商）
python image_recognizer.py image.png

# 自定义提问
python image_recognizer.py image.png -p "这张图片里有什么文字？"
python image_recognizer.py image.png --prompt "Describe in English"
```

### Reasonix Desktop 对话中使用（推荐）

```bash
# 在任意项目下调用全局 Skill
/view_image @image.png

# 带自定义提问
/view_image @image.png -p "这张图片里有什么文字？"

# 绝对路径
/view_image C:\photos\test.jpg
```

Agent 会运行识别程序 → 读取结果 → **像正常人一样直接回答你**（不会展示技术细节）。

---

## 输出

### 结果文件

程序会在脚本所在目录生成 txt 文件，文件名格式：

```
<图片名>_result_<时间戳>.txt
```

文件内容示例：

```
图像识别结果
==================================================

图片路径: image.png
使用提示词: 请详细描述这张图片中的内容...
识别时间: 2026-06-06 13:07:22

识别结果：
--------------------------------------------------
<AI 对图片的详细描述>
--------------------------------------------------
```

### 自动清理

每次运行时自动删除超过 **7 天** 的旧结果文件。

---

## 注意事项

- 支持图片格式：jpg、jpeg、png、gif、bmp、webp
- 确保网络连接正常
- API 调用可能耗时几秒到十几秒
- 程序失败时（图片不存在 / API 错误）返回退出码 `1`
- API Key 支持 `${ENV_VAR}` 环境变量引用，方便跨设备安全使用
