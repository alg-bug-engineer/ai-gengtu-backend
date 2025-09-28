# -*- coding: utf-8 -*-
"""
即梦生图API调用工具
功能：通过火山引擎即梦生图API生成图片，并将Base64结果转换为本地图片文件
日志输出：/Users/zhangqilai/ai-gengtu/logs（按日期分文件）
环境依赖：需在.env文件中配置 access_key、secret_key（可选配置default_dir）
"""

# ------------------------------
# 1. 导入依赖库（按：标准库 → 第三方库 顺序）
# ------------------------------
import json
import sys
import base64
import datetime
import hashlib
import hmac
from PIL import Image  # 用于图片处理
import os
from typing import Optional  # 类型提示：可选参数
from io import BytesIO

# 第三方库
import requests
from dotenv import load_dotenv
import logging  # 日志模块

# ------------------------------
# 2. 日志系统初始化（输出到文件+控制台）
# ------------------------------
"""初始化日志配置：同时输出到指定文件和控制台"""
# 日志目录（用户指定路径）
LOG_DIR = os.getenv('LOGS_PATH')
# 确保日志目录存在（不存在则创建）
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件名（按日期命名，如：2024-05-20.log）
log_file = os.path.join(LOG_DIR, datetime.datetime.now().strftime("%Y-%m-%d") + "_jimeng.log")

# 日志格式（包含：时间、级别、模块行号、消息）
log_format = "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"

# 配置日志处理器（文件+控制台）
logging.basicConfig(
    level=logging.INFO,  # 日志级别：INFO及以上会被记录
    format=log_format,
    handlers=[
        # 1. 输出到文件（UTF-8编码，避免中文乱码）
        logging.FileHandler(log_file, encoding="utf-8"),
        # 2. 输出到控制台
        logging.StreamHandler(sys.stdout)
    ]
)

# ------------------------------
# 3. 全局配置加载（从.env文件读取密钥和路径）
# ------------------------------

logging.info("成功加载.env环境变量文件")

# API固定配置（火山引擎即梦生图）
API_CONFIG = {
    "method": "POST",          # HTTP请求方法
    "host": "visual.volcengineapi.com",  # API主机
    "region": "cn-north-1",    # 服务区域
    "endpoint": "https://visual.volcengineapi.com",  # API完整端点
    "service": "cv"            # 服务类型（计算机视觉）
}

# 从.env读取密钥（必选，缺失将退出程序）
ACCESS_KEY = os.getenv("access_key")
SECRET_KEY = os.getenv("secret_key")

# 从.env读取默认图片保存路径（可选，默认路径为用户指定的默认值）
DEFAULT_IMAGE_DIR = os.getenv(
    "default_dir", 
    "./images"
)


# ------------------------------
# 4. 工具函数：Base64转图片
# ------------------------------
def base64_to_image(base64_str: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    将Base64字符串解码为图片并保存到本地
    
    参数:
        base64_str: 包含图片数据的Base64字符串（支持带前缀如'data:image/png;base64,'）
        output_path: 可选，图片保存路径。为None时使用默认目录+时间戳命名
    
    返回:
        Optional[str]: 成功返回图片保存路径；失败返回None
    
    异常:
        捕获所有解码/保存过程中的异常，通过日志记录堆栈信息
    """
    logging.info("开始处理Base64字符串转图片")
    
    try:
        # 步骤1：移除Base64前缀（如存在）
        if "base64," in base64_str:
            logging.debug("检测到Base64前缀，执行切割处理")
            base64_str = base64_str.split("base64,")[1]
        
        # 步骤2：Base64解码为二进制数据
        logging.debug("开始解码Base64字符串（长度：%d）", len(base64_str))
        image_bin = base64.b64decode(base64_str)
        
        # 步骤3：二进制数据转PIL图片对象
        logging.debug("将二进制数据转换为PIL Image对象")
        # 将保存操作移入 with 语句中
        with BytesIO(image_bin) as img_buffer:
            image = Image.open(img_buffer)
            # 保留图片原始格式（如PNG/JPG），无格式时默认PNG
            img_format = image.format.lower() if image.format else "png"
            logging.info("检测到图片格式：%s", img_format)
            
            # 步骤4：确定保存路径（未指定则用默认目录+时间戳）
            if not output_path:
                logging.debug("未指定保存路径，使用默认配置")
                # 确保默认图片目录存在
                os.makedirs(DEFAULT_IMAGE_DIR, exist_ok=True)
                logging.info("确认/创建默认图片目录：%s", DEFAULT_IMAGE_DIR)
                
                # 生成时间戳文件名（避免重复）：20240520143025.png
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                output_path = os.path.join(DEFAULT_IMAGE_DIR, f"{timestamp}.{img_format}")
            
            # 步骤5：保存图片到本地
            logging.info("开始保存图片到：%s", output_path)
            image.save(output_path)
            logging.info("图片保存成功，路径：%s", output_path)
            return output_path
    
    except Exception as e:
        # 记录异常详情（含堆栈），方便排查问题
        logging.error("Base64转图片失败：%s", str(e), exc_info=True)
        return None



# ------------------------------
# 5. 工具函数：V4签名相关（火山引擎API认证）
# ------------------------------
def hmac_sha256_sign(key: bytes, msg: str) -> bytes:
    """
    单次HMAC-SHA256签名（V4签名的基础步骤）
    
    参数:
        key: 签名密钥（字节类型）
        msg: 待签名的字符串（需UTF-8编码）
    
    返回:
        bytes: 签名后的字节数据
    """
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def generate_v4_sign_key(secret_key: str, date_stamp: str, region: str, service: str) -> bytes:
    """
    生成火山引擎V4签名所需的最终签名密钥（分层推导）
    
    推导流程：kSecret → kDate → kRegion → kService → kSigning
    每层均使用HMAC-SHA256签名
    
    参数:
        secret_key: 原始SecretKey（从.env读取）
        date_stamp: 日期戳（格式：YYYYMMDD，如20240520）
        region: 服务区域（如cn-north-1）
        service: 服务名称（如cv）
    
    返回:
        bytes: 最终用于请求签名的密钥（kSigning）
    """
    logging.info("开始生成V4签名密钥，参数：日期=%s，区域=%s，服务=%s", date_stamp, region, service)
    
    # 分层推导签名密钥
    k_date = hmac_sha256_sign(key=secret_key.encode("utf-8"), msg=date_stamp)
    k_region = hmac_sha256_sign(key=k_date, msg=region)
    k_service = hmac_sha256_sign(key=k_region, msg=service)
    k_signing = hmac_sha256_sign(key=k_service, msg="request")
    
    logging.debug("V4签名密钥生成完成（kSigning长度：%d字节）", len(k_signing))
    return k_signing


def format_query_params(params: dict) -> str:
    """
    格式化查询参数（V4签名要求：按字母排序+key=value&key=value格式）
    
    参数:
        params: 原始查询参数字典（如{"Action":"CVProcess", "Version":"2022-08-31"}）
    
    返回:
        str: 格式化后的查询参数字符串
    """
    logging.debug("开始格式化查询参数，原始参数：%s", params)
    
    # 1. 按参数名字母升序排序
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    # 2. 拼接为key=value格式，用&连接
    formatted = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    logging.debug("格式化后查询参数：%s", formatted)
    return formatted


# ------------------------------
# 6. 核心函数：V4签名+API请求
# ------------------------------
def send_v4_signed_request(
    access_key: str,
    secret_key: str,
    query_params: dict,
    request_body: dict
) -> Optional[str]:
    """
    生成V4签名并发送API请求，最终返回图片保存路径
    
    参数:
        access_key: 火山引擎AccessKey
        secret_key: 火山引擎SecretKey
        query_params: API查询参数（如Action、Version）
        request_body: API请求体（如prompt、req_key）
    
    返回:
        Optional[str]: 成功返回图片路径；失败返回None
    """
    # 前置检查：密钥是否缺失
    if not (access_key and secret_key):
        logging.critical("AccessKey或SecretKey缺失，无法进行V4签名，程序退出")
        sys.exit(1)  # 密钥缺失为致命错误，退出程序
    
    # 步骤1：获取当前UTC时间（V4签名要求）
    utc_now = datetime.datetime.utcnow()
    current_date = utc_now.strftime("%Y%m%dT%H%M%SZ")  # 带时间的UTC戳（如20240520T063025Z）
    date_stamp = utc_now.strftime("%Y%m%d")            # 仅日期戳（如20240520）
    logging.info("当前UTC时间：%s，日期戳：%s", current_date, date_stamp)
    
    # 步骤2：构建规范请求（Canonical Request）
    # 2.1 固定参数
    canonical_uri = "/"  # API请求URI（即梦生图固定为/）
    algorithm = "HMAC-SHA256"  # 签名算法
    signed_headers = "content-type;host;x-content-sha256;x-date"  # 需签名的请求头
    content_type = "application/json"  # 请求体格式
    
    # 2.2 格式化查询参数和请求体
    canonical_query = format_query_params(query_params)
    request_body_str = json.dumps(request_body, ensure_ascii=False)  # 转为JSON字符串
    
    # 2.3 计算请求体的SHA256哈希（V4签名要求）
    payload_hash = hashlib.sha256(request_body_str.encode("utf-8")).hexdigest()
    logging.debug("请求体SHA256哈希：%s", payload_hash)
    
    # 2.4 构建规范请求头（小写key+值，末尾换行）
    canonical_headers = (
        f"content-type:{content_type}\n"
        f"host:{API_CONFIG['host']}\n"
        f"x-content-sha256:{payload_hash}\n"
        f"x-date:{current_date}\n"
    )
    logging.debug("规范请求头：%s", canonical_headers.strip())  # strip()去除末尾换行，避免日志冗余
    
    # 2.5 拼接完整规范请求
    canonical_request = (
        f"{API_CONFIG['method']}\n"
        f"{canonical_uri}\n"
        f"{canonical_query}\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    )
    logging.debug("规范请求构建完成（长度：%d字节）", len(canonical_request))
    
    # 步骤3：构建待签名字符串（String to Sign）
    credential_scope = f"{date_stamp}/{API_CONFIG['region']}/{API_CONFIG['service']}/request"
    string_to_sign = (
        f"{algorithm}\n"
        f"{current_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )
    logging.debug("待签名字符串构建完成，凭证范围：%s", credential_scope)
    
    # 步骤4：生成签名密钥并计算最终签名
    signing_key = generate_v4_sign_key(secret_key, date_stamp, API_CONFIG['region'], API_CONFIG['service'])
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    logging.info("V4签名计算完成：%s", signature)
    
    # 步骤5：构建Authorization请求头
    auth_header = (
        f"{algorithm} "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )
    
    # 步骤6：构建完整请求头
    request_headers = {
        "X-Date": current_date,
        "Authorization": auth_header,
        "X-Content-Sha256": payload_hash,
        "Content-Type": content_type
    }
    logging.debug("请求头构建完成：%s", request_headers)
    
    # 步骤7：发送POST请求
    request_url = f"{API_CONFIG['endpoint']}?{canonical_query}"
    logging.info("开始发送API请求，URL：%s", request_url)
    logging.debug("请求体：%s", request_body_str)
    
    try:
        response = requests.post(
            url=request_url,
            headers=request_headers,
            data=request_body_str.encode("utf-8"),  # 显式指定UTF-8编码，避免中文乱码
            timeout=30  # 超时时间30秒，防止长期阻塞
        )
        # 检查HTTP状态码（200为成功）
        response.raise_for_status()
        logging.info("API请求成功，HTTP状态码：%d", response.status_code)
    
    except requests.exceptions.RequestException as e:
        # 捕获所有HTTP请求异常（超时、连接失败、4xx/5xx等）
        logging.error("API请求失败：%s", str(e), exc_info=True)
        return None
    
    # 步骤8：解析响应并提取Base64图片
    try:
        response_json = response.json()
        logging.debug("API响应内容：%s", json.dumps(response_json, indent=2, ensure_ascii=False))
        
        # 提取即梦生图返回的Base64数据（响应结构：data → binary_data_base64[0]）
        base64_image = response_json["data"]["binary_data_base64"][0]
        logging.info("成功提取Base64图片数据（长度：%d字节）", len(base64_image))
        
        # 调用工具函数将Base64转为本地图片
        return base64_to_image(base64_str=base64_image)
    
    except KeyError as e:
        logging.error("API响应结构异常，缺失字段：%s", str(e))
        return None
    except json.JSONDecodeError:
        logging.error("API响应不是合法JSON格式，响应内容：%s", response.text)
        return None


# ------------------------------
# 7. 业务函数：即梦生图API调用入口
# ------------------------------
def jimeng_generate_api(prompt: str, width: int, height: int) -> Optional[str]:
    """
    即梦生图API调用入口：输入提示词，返回图片保存路径

    参数:
        prompt: 图片生成提示词（中文，需符合即梦生图格式要求）
        width: 图片宽度
        height: 图片高度

    返回:
        Optional[str]: 成功返回图片路径；失败返回None
    """
    logging.info("=" * 50)
    logging.info("开始调用即梦生图API，提示词：%s，尺寸：%dx%d", prompt, width, height)
    logging.info("=" * 50)
    
    # 1. 构建API查询参数（即梦生图固定参数）
    query_params = {
        "Action": "CVProcess",    # API动作名
        "Version": "2022-08-31"   # API版本
    }
    
    # 2. 构建API请求体（核心参数：提示词、模型版本）
    request_body = {
        "req_key": "jimeng_t2i_v40",  # 即梦生图V4.0模型
        "prompt": prompt,             # 用户输入的提示词
        "width": width,
        "height": height
    }
    
    # 3. 发送签名请求并返回图片路径
    try:
        image_path = send_v4_signed_request(
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            query_params=query_params,
            request_body=request_body
        )
        
        if image_path:
            logging.info("即梦生图API调用完成，图片保存路径：%s", image_path)
            return image_path
        else:
            logging.error("即梦生图API调用失败，未获取到图片路径")
            return None
    
    except Exception as e:
        logging.error("即梦生图API调用过程中发生未知错误：%s", str(e), exc_info=True)
        return None


# ------------------------------
# 8. 主程序入口（测试用）
# ------------------------------
if __name__ == "__main__":    
    # 测试：调用即梦生图API生成图片
    test_prompt = "一只可爱的柯基犬在绿色草地上玩耍，背景是蓝天白云，阳光明媚，高清照片质感"
    result_path = jimeng_generate_api(prompt=test_prompt)
    
    # 输出测试结果
    if result_path:
        logging.info("测试成功！生成图片路径：%s", result_path)
    else:
        logging.error("测试失败！未生成图片")
