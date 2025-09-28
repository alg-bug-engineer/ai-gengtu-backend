# alg-bug-engineer/ai-gengtu-backend/ai-gengtu-backend-683d3a06f02d6e71016f8d8e977d1795d9f89ed9/singapore_gemini_server.py
# -*- coding: utf-8 -*-
"""
Gemini API代理服务
功能: 接收HTTP请求，调用Google Gemini API，解析并返回干净的、可直接使用的提示词。
"""
import os
import sys
import logging
import json
import io
from flask import send_file
import re  # 导入 re 模块
import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()

# 将 api 目录添加到系统路径
# 假设 genemi_api.py 与此文件在同一目录下或可通过python path访问
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
from genemi_api import genemi_generate_api, generate_figurine_image

# 应用配置
app = Flask(__name__)

# 配置日志
LOG_DIR = os.getenv("LOGS_PATH")
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = datetime.datetime.now().strftime("%Y-%m-%d") + "_gemini_server.log"
log_filepath = os.path.join(LOG_DIR, log_filename)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler(log_filepath, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.info("新加坡 Gemini 服务日志系统初始化完成。")

# 定义用于解析的正则表达式
PROMPT_PATTERN = r'```json(.*?)```'

@app.route('/api/genemi', methods=['POST'])
def generate_gemini_prompt():
    """
    接收来自主后端服务的请求，调用本地 Gemini API，解析后返回最终的中文提示词。
    """
    data = request.get_json()
    answer = data.get('answer')
    
    if not answer:
        logging.warning("请求缺少 'answer' 参数。")
        return jsonify({"message": "Missing 'answer' parameter."}), 400

    logging.info("收到生成梗图提示词的请求，谜底: %s", answer)

    try:
        # 1. 调用核心的 Gemini 生成函数
        raw_gemini_response = genemi_generate_api(prompt=answer)

        if not raw_gemini_response:
            logging.error("genemi_generate_api 返回了空响应。")
            return jsonify({"message": "Gemini API returned an empty response."}), 500

        # 2. 在新加坡服务内部解析响应
        logging.info("解析 Gemini 的响应以提取中文提示词。")
        matches = re.findall(PROMPT_PATTERN, raw_gemini_response, re.DOTALL)
        
        if not matches or len(matches) < 2:
            logging.error(f"无法从 Gemini 响应中解析出提示词。响应内容: {raw_gemini_response}")
            raise ValueError("Gemini 响应格式不正确。")
        
        # 3. 提取并返回干净的中文提示词
        chinese_prompt = matches[1].strip()
        logging.info("成功提取中文提示词。")
        
        return jsonify({"chinese_prompt": chinese_prompt}), 200

    except Exception as e:
        logging.error(f"调用 Gemini API 或解析时发生未知错误: {e}", exc_info=True)
        return jsonify({"message": "An unexpected error occurred on the Gemini server."}), 500


# --- 新增立体雕塑生成路由 ---
@app.route('/api/generate_figurine', methods=['POST'])
def generate_figurine_from_image_proxy():
    """
    接收来自主后端上传的图片，调用Gemini完成“图生图”流程，并返回最终图片。
    """
    logging.info("收到立体雕塑生成请求...")
    
    if 'image' not in request.files:
        logging.warning("请求中未找到图片文件 'image'。")
        return jsonify({"message": "Missing image file."}), 400

    file = request.files['image']
    
    if file.filename == '':
        logging.warning("上传了空文件。")
        return jsonify({"message": "Empty file."}), 400

    try:
        image_bytes = file.read()
        logging.info(f"已读取上传的图片，大小: {len(image_bytes)} bytes。")

        # 调用核心AI逻辑
        generated_image_bytes = generate_figurine_image(uploaded_image_bytes=image_bytes)

        if not generated_image_bytes:
            logging.error("generate_figurine_image 未能返回图片数据。")
            return jsonify({"message": "Failed to generate figurine image via Gemini."}), 500
        
        logging.info("成功从Gemini获取生成的图片，正在返回...")
        # 将二进制数据作为图片文件返回
        return send_file(
            io.BytesIO(generated_image_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name='figurine.png'
        )

    except Exception as e:
        logging.error(f"处理立体雕塑请求时发生未知错误: {e}", exc_info=True)
        return jsonify({"message": "An unexpected error occurred on the Singapore server."}), 500


if __name__ == '__main__':
    logging.info("启动新加坡 Gemini API 服务...")
    app.run(host='0.0.0.0', port=5551)