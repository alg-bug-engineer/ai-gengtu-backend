# app.py
from flask import Flask, request, jsonify, send_file
import re
import os
import sys
from flask_cors import CORS  # <-- Add this line

# 将上一级目录添加到系统路径，以便可以导入 api 文件夹中的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.genemi_api import genemi_generate_api
from api.jimeng_api import jimeng_generate_api

app = Flask(__name__)
CORS(app)  # <-- Add this line to enable CORS for all routes

# 定义正则表达式，用于从 Gemini 响应中提取中文提示词
# 该正则模式来自于您提供的 testre.py 文件
PROMPT_PATTERN = r'```json(.*?)```'


@app.route('/generate_meme', methods=['POST'])
def generate_meme():
    """
    API 路由：接收谜底，调用 Gemini 和即梦 API，生成并返回梗图。
    """
    # 1. 获取用户输入
    data = request.get_json()
    answer = data.get('answer')
    
    if not answer:
        app.logger.error("请求失败: 缺少 'answer' 参数。")
        return jsonify({"success": False, "message": "Missing 'answer' parameter."}), 400

    app.logger.info(f"收到新的梗图生成请求，谜底: {answer}")

    try:
        # 2. 调用 genemi_api 生成提示词
        gemini_response = genemi_generate_api(answer)

        # 3. 解析 Gemini 响应，提取中文提示词
        matches = re.findall(PROMPT_PATTERN, gemini_response, re.DOTALL)
        if not matches or len(matches) < 2:
            raise ValueError("Gemini 响应格式不正确，无法解析出提示词。")
        
        # 假设第二个匹配项是中文提示词
        chinese_prompt = matches[1].strip()
        app.logger.info(f"成功从 Gemini 响应中提取中文提示词。提示词是：{chinese_prompt}")

        # 4. 调用 jimeng_api 生成图片
        # 这里的 jimeng_api 函数需要返回图片的绝对路径
        image_path = jimeng_generate_api(chinese_prompt)
        
        if not image_path:
            raise Exception("图片生成失败，未返回有效的图片路径。")
        
        # 5. 返回图片文件给前端
        app.logger.info(f"图片生成成功，准备发送文件: {image_path}")
        # 这里直接发送文件，前端可以通过URL访问
        return send_file(image_path, mimetype='image/png')
        
    except ValueError as ve:
        app.logger.error(f"处理失败: {ve}")
        return jsonify({"success": False, "message": str(ve)}), 500
    except Exception as e:
        app.logger.error(f"发生未预期错误: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    # 启用日志记录
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host='0.0.0.0', port=5550)