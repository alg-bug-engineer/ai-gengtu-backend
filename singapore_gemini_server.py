# -*- coding: utf-8 -*-
"""
Gemini API代理服务
功能: 接收HTTP请求，调用Google Gemini API，返回生成的提示词。
"""
import os
import sys
import logging
import json
import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# 将 api 目录添加到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../api'))

# 从同一个目录中导入核心的 Gemini 生成逻辑
from genemi_api import genemi_generate_api

# 应用配置
app = Flask(__name__)

# 配置日志
LOG_DIR = "/root/ai-gengtu-backend/logs"
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
logging.info("新加坡 Gemini 服务日志系统初始化完成，日志文件路径：%s", log_filepath)

@app.route('/api/genemi', methods=['POST'])
def generate_gemini_prompt():
    """
    接收来自主后端服务的请求，调用本地 Gemini API，并返回结果
    """
    data = request.get_json()
    answer = data.get('answer')
    
    if not answer:
        logging.warning("Received request with missing 'answer' parameter.")
        return jsonify({"message": "Missing 'answer' parameter."}), 400

    logging.info("Received request for Gemini prompt generation. Answer: %s", answer)

    try:
        # 调用核心的生成函数
        gemini_response = genemi_generate_api(prompt=answer)

        if not gemini_response:
            logging.error("genemi_generate_api returned an empty response.")
            return jsonify({"message": "Gemini API returned an empty response, possibly due to content filtering."}), 500

        logging.info("Gemini prompt generated successfully.")
        # 返回原始的JSON字符串，以便主后端解析
        return jsonify({"prompt": gemini_response}), 200

    except Exception as e:
        logging.error("An unexpected error occurred during Gemini API call: %s", str(e), exc_info=True)
        return jsonify({"message": "An unexpected error occurred on the Gemini server."}), 500

if __name__ == '__main__':
    logging.info("Starting Singapore Gemini API server.")
    app.run(host='0.0.0.0', port=5551)