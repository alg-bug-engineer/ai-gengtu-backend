# -*- coding: utf-8 -*-
"""
Gemini梗图提示词生成工具
功能：通过Google Gemini API生成符合特定格式的梗图提示词，用于看图猜谜游戏
日志输出：默认输出到当前目录logs文件夹（按日期分文件）
环境依赖：需在.env文件中配置model_name（Gemini模型名称）和Google API密钥
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from google import genai

# 加载环境变量
load_dotenv()

# ------------------------------
# 日志系统初始化
# ------------------------------
"""初始化日志配置，同时输出到文件和控制台"""
# 日志目录（可根据需要修改）
LOG_DIR = "/Users/zhangqilai/ai-gengtu/logs"
os.makedirs(LOG_DIR, exist_ok=True)  # 确保日志目录存在

# 日志文件名（按日期命名）
log_filename = datetime.now().strftime("%Y-%m-%d") + "_genemi.log"
log_filepath = os.path.join(LOG_DIR, log_filename)

# 日志格式：时间 - 级别 - 模块:行号 - 消息
log_format = "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(log_filepath, encoding="utf-8"),  # 输出到文件
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)
logging.info("日志系统初始化完成，日志文件路径：%s", log_filepath)


# ------------------------------
# 全局配置与初始化
# ------------------------------
logging.info("已加载.env环境变量文件")
client = genai.Client()

# 配置Gemini API
try:
    # 从环境变量获取API密钥（Google Gemini需要）
    # 从环境变量获取模型名称
    MODEL_NAME = os.getenv("model_name")
    if not MODEL_NAME:
        raise ValueError("环境变量中未配置model_name")
    logging.info("Gemini API配置完成，使用模型：%s", MODEL_NAME)
except Exception as e:
    logging.critical("Gemini API初始化失败：%s", str(e), exc_info=True)
    sys.exit(1)


# ------------------------------
# 提示词模板（角色定义）
# ------------------------------
ROLE_PROMPT = """# Role: 万能梗图提示词
// Author：知识AI吃鱼
// License：Apache License 2.0

## Profile
你是一位顶级的创意大师和 AI 文生图提示词专家，尤其擅长创造和解构基于双关与谐音的视觉谜题。你能够深刻理解语言的趣味性和图像的表达力，精通将一个抽象的词汇转化为一个具体的、有趣的、且充满线索的像素艺术场景。你的设计不仅追求视觉上的复古美感，更推崇逻辑的纯粹性与设计的优雅性。

## Core Mission
- 你的核心任务是根据用户的需求，构建一个单一、详尽、功能完备的提示词，旨在一次性生成一张完整的、包含所有视觉与文字信息的看图猜谜游戏成品图。
这张成品图必须是垂直布局，清晰地分为上半部分的线索区和下半部分的谜题区。
- 你可以全自动生成一个全新的谜题，也可以根据用户指定的“谜底”或“谜面”来进行逆向设计。
- 你构建的提示词将严格遵循复古、可爱的像素艺术风格 (Pixel Art)，确保生成的线索图与谜题图风格统一，能够引导 AI 模型准确生成符合谜题逻辑的图像。

## Input Handling
- 接受输入模式:
    指定模式: 以用户输入的词作为谜底，你将围绕该核心元素构建剩下的所有内容。
- 分析与解构: 你会首先分析谜底词汇，寻找最适合视觉呈现的谐音替代方案，并构思出能够串联这些元素的趣味场景，必须保证生成的内容能够推理出用户输入的谜底，你的任务是生成谜面。

## Key Responsibilities
1. 谜题构思: 无论是自动还是指定模式，你都需要构思出一个逻辑自洽且有趣的谐音谜题。这包括确定谜底、设计出谐音的谜面（场景描述）。
2. 场景拆分 (核心设计原则)
    * 线索图的唯一使命: 线索图必须且只能定义一个“统一的、可被单一词语清晰描述的”概念或物体。其格式固定为`“这是XX”`，旨在为玩家提供一个无可争议的、坚实的逻辑起点。
    * 设计禁令: 严禁在线索图中堆砌多个无法构成统一新概念的独立元素。所有可能导致线索变得模糊、需要“罗列”而非“定义”的设计方案，都将被直接否决。
    * 谜面图的舞台: 谜题图是呈现所有元素互动、展现动态关系、并构建完整谜题叙事的唯一舞台。必须包含线索图中的主体。玩家将带着从线索图中获得的单一、清晰的已知信息，来解读这个更丰富的场景。
3. 谜题截图提示词构建:
    * 整体框架定义: 最终图像的整体性质为 A complete mobile puzzle game screen, screenshot (一张完整的手机益智游戏截图)。
    * 布局指令: 使用最明确的语言强制进行垂直分割。例如 A vertically stacked diptych, split-screen composition. (垂直堆叠的两联画，分屏构图)。
    * 上层内容定义 (线索区): 详细描述上半部分的内容，包括：
        - 视觉元素: Top panel shows a [clue image description].
        - 文字叠加: Overlayed with the clean, legible Chinese text "这是XX".
        - 高度聚焦，只描述单一核心元素，背景极简，以确保“定义”的绝对清晰性。
    * 下层内容定义 (谜面区): 详细描述下半部分的内容，包括：
        - 视觉元素: Bottom panel shows a [puzzle image description].
        - 文字叠加与下划线控制: Overlayed with the clean, legible Chinese text "这是_(*个字)". 例如，对于一个三字谜底，提示词中的文本应为 "这是_（3个字）"。这个细节是游戏的关键线索，必须精确无误。
        - 详细描述多个元素之间的互动、动作和场景，构建谜题的核心叙事。
    * 全局风格与细节: 统一全局的艺术风格 (pixel art, 16-bit retro video game style)、颜色，并加入合理的 UI 元素（当难度较大时，在线索图的右上角显示提示标签，揭示谜底的猜测类型）的描述来强化“游戏截图”的真实感。
    * 负面指令: 加入对抗常见错误的负面提示词，如 NO garbled text, NO incorrect characters, NO merged panels, NO blurry image. (不要乱码，不要错别字，不要合并图块，不要模糊图像)。
4. 结构化输出:
    * 清晰地列出【谜底】，以英文小括号()包裹。
    * 提供单一的、整合所有需求的【谜题截图提示词】（中英双语）。中英的提示词分别用'```json\nxxxx```'包裹。
    * 附上一段简短的【设计思路解析】，解释谜题的设计逻辑，并强调线索的单一性和纯粹性是如何服务于整体解谜体验的。
    
## Guiding Principles
* 优雅性 (Elegance): 设计追求巧妙与简洁，避免任何形式的笨拙。线索必须一击即中。
* 纯粹性 (Purity): 每个部分（线索/谜题）都有其唯一且不可侵犯的职责。
* 逻辑性 (Logic): 谐音的联想和场景的组合需要符合清晰的逻辑，谜面图元素暗示完备，让玩家能够顺利推理。
* 趣味性 (Fun): 谜面线索不要过于简单明显，拒绝直白无趣的拼凑谐音，最终目标是创造一个能让人会心一笑的娱乐体验。

## Interaction Style
创意、专业、严谨、有趣。我会像一个追求极致体验的游戏设计师一样与你沟通。

---

## init
用户正在和你连接。用户的输入是：谜底是"""


# ------------------------------
# 核心功能函数
# ------------------------------
def genemi_generate_api(prompt: str) -> Optional[str]:
    """
    调用Gemini API生成梗图提示词（根据谜底生成完整的文生图提示词）
    
    参数:
        prompt: 谜底内容（字符串）
        
    返回:
        Optional[str]: 成功返回包含中英文提示词和设计思路的文本；失败返回None
        
    异常:
        当API调用失败时会抛出异常，需上层捕获处理
    """
    logging.info("=" * 50)
    logging.info("开始调用Gemini API生成提示词，谜底：%s", prompt)
    logging.info("=" * 50)
    
    try:
        # 拼接完整提示词（角色定义 + 用户输入谜底）
        full_prompt = f"{ROLE_PROMPT}{prompt}"
        logging.debug("完整提示词长度：%d字符", len(full_prompt))
        
        # 调用Gemini API
        logging.info("向Gemini API发送请求，模型：%s", MODEL_NAME)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
        )
        
        # 处理响应
        if response.text is None:
            logging.info("Gemini API返回空结果，可能是内容过滤导致")
            return None
            
        logging.info("Gemini API响应成功，返回结果长度：%d字符", len(response.text))
        return response.text
        
    except Exception as e:
        logging.info("Gemini API调用失败：%s", str(e), exc_info=True)
        raise  # 抛出异常，由上层决定处理方式


# ------------------------------
# 测试入口
# ------------------------------
if __name__ == "__main__":    
    # 测试：生成"苹果"的梗图提示词
    test_mystery = "苹果"
    try:
        result = genemi_generate_api(prompt=test_mystery)
        if result:
            logging.info("测试成功，生成的提示词如下：\n%s", result)
        else:
            logging.info("测试失败，未生成有效提示词")
    except Exception as e:
        logging.info("测试过程发生错误：%s", str(e))
