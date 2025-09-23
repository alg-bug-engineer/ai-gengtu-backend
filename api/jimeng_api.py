# 导入所需库
import json  # 用于JSON数据的序列化和反序列化
import sys  # 用于系统相关操作，如程序退出
import base64  # 用于Base64编码和解码
import datetime  # 用于处理日期和时间
import hashlib  # 用于哈希算法
import hmac  # 用于HMAC加密
import requests  # 用于发送HTTP请求
import os  # 用于文件系统操作
from io import BytesIO  # 用于处理字节流
from PIL import Image  # 用于图片处理
from dotenv import load_dotenv
load_dotenv()

# API请求配置参数
method = 'POST'  # HTTP请求方法
host = 'visual.volcengineapi.com'  # API主机地址
region = 'cn-north-1'  # 服务区域
endpoint = 'https://visual.volcengineapi.com'  # API完整端点
service = 'cv'  # 服务名称（计算机视觉）

# 从.env读取密钥（关键修改）
access_key = os.getenv("access_key")
secret_key = os.getenv("secret_key")
# 从.env读取默认图片路径（可选，更灵活）
default_dir = os.getenv("default_dir", "/Users/zhangqilai/ai-gengtu/images")  # 第二个参数为默认值


def base64_to_image(base64_str, output_path=None):
    """
    将base64字符串转换为图片并保存到本地
    
    参数:
        base64_str: 包含图片数据的base64字符串
        output_path: 可选参数，图片保存路径。如果为None，
                    则默认保存到default_dir文件夹，命名格式为yyyymmddhhmmss
                    
    返回:
        成功：图片保存路径字符串
        失败：None
    """
    try:
        print(f"[INFO] 开始处理base64字符串转换为图片")
        
        # 移除可能存在的前缀（如'data:image/png;base64,'）
        if 'base64,' in base64_str:
            print(f"[INFO] 检测到base64前缀，进行处理")
            base64_str = base64_str.split('base64,')[1]
        
        # 解码base64字符串为二进制数据
        print(f"[INFO] 开始解码base64字符串")
        image_data = base64.b64decode(base64_str)
        
        # 将二进制数据转换为PIL Image对象
        print(f"[INFO] 将二进制数据转换为图片对象")
        image = Image.open(BytesIO(image_data))
        
        # 确定图片保存路径
        if output_path is None:
            print(f"[INFO] 未指定保存路径，使用默认配置")
            # 确保默认文件夹存在，如果不存在则创建
            os.makedirs(default_dir, exist_ok=True)
            print(f"[INFO] 确认/创建图片保存目录: {default_dir}")
            
            # 获取当前时间并格式化为yyyymmddhhmmss作为文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            print(f"[INFO] 生成时间戳文件名: {timestamp}")
            
            # 获取图片格式（如PNG、JPG等），默认为png
            img_format = image.format.lower() if image.format else "png"
            print(f"[INFO] 检测到图片格式: {img_format}")
            
            # 构建完整保存路径
            output_path = os.path.join(default_dir, f"{timestamp}.{img_format}")
        
        # 保存图片到指定路径
        print(f"[INFO] 开始保存图片到: {output_path}")
        image.save(output_path)
        print(f"[SUCCESS] 图片已成功保存到: {output_path}")
        return output_path  # 返回实际保存路径，方便后续使用
        
    except Exception as e:
        print(f"[ERROR] 图片转换/保存失败: {str(e)}")
        return None


def sign(key, msg):
    """
    使用HMAC-SHA256算法进行签名
    
    参数:
        key: 签名密钥（字节类型）
        msg: 待签名的消息（字符串）
        
    返回:
        签名结果（字节类型）
    """
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    """
    生成V4签名所需的签名密钥
    
    签名密钥生成流程：kSecret -> kDate -> kRegion -> kService -> kSigning
    
    参数:
        key: 原始密钥（secret_key）
        dateStamp: 日期戳（格式：YYYYMMDD）
        regionName: 区域名称
        serviceName: 服务名称
        
    返回:
        最终的签名密钥（字节类型）
    """
    print(f"[INFO] 开始生成签名密钥，日期: {dateStamp}, 区域: {regionName}, 服务: {serviceName}")
    kDate = sign(key.encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning


def formatQuery(parameters):
    """
    格式化查询参数，按字母顺序排序并拼接为key=value&key=value形式
    
    参数:
        parameters: 字典类型的查询参数
        
    返回:
        格式化后的查询参数字符串
    """
    print(f"[INFO] 开始格式化查询参数: {parameters}")
    request_parameters_init = ''
    # 按字母顺序排序参数，确保签名一致性
    for key in sorted(parameters):
        request_parameters_init += f"{key}={parameters[key]}&"
    # 移除最后一个多余的&符号
    request_parameters = request_parameters_init[:-1]
    print(f"[INFO] 格式化后的查询参数: {request_parameters}")
    return request_parameters


def signV4Request(access_key, secret_key, service, req_query, req_body):
    """
    生成V4签名并发送HTTP请求
    
    参数:
        access_key: 访问密钥ID
        secret_key: 秘密访问密钥
        service: 服务名称
        req_query: 格式化后的查询参数字符串
        req_body: 请求体（JSON字符串）
        
    返回:
        图片保存路径（成功）或None（失败）
    """
    # 检查凭证是否存在
    if access_key is None or secret_key is None:
        print(f"[ERROR] 缺少访问凭证（access_key或secret_key）")
        sys.exit(1)

    # 获取当前UTC时间，用于签名和请求头
    t = datetime.datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')  # 带时间的UTC时间戳
    datestamp = t.strftime('%Y%m%d')  # 仅日期部分，用于凭证范围
    print(f"[INFO] 当前UTC时间: {current_date}")

    # 构建规范请求（Canonical Request）的各个部分
    canonical_uri = '/'  # 请求URI，默认为/
    algorithm = 'HMAC-SHA256'  # 签名算法
    canonical_querystring = req_query  # 规范查询字符串
    signed_headers = 'content-type;host;x-content-sha256;x-date'  # 需要签名的请求头
    
    # 计算请求体的SHA256哈希
    payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
    print(f"[INFO] 请求体哈希值: {payload_hash}")
    
    content_type = 'application/json'  # 请求内容类型
    
    # 构建规范请求头
    canonical_headers = (
        f'content-type:{content_type}\n'
        f'host:{host}\n'
        f'x-content-sha256:{payload_hash}\n'
        f'x-date:{current_date}\n'
    )
    canonical_headers = canonical_headers.replace('\\n', ' ')
    print(f"[INFO] 规范请求头: {canonical_headers}")
    
    # 拼接完整的规范请求
    canonical_request = (
        f"{method}\n"
        f"{canonical_uri}\n"
        f"{canonical_querystring}\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    )
    print(f"[INFO] 规范请求构建完成")

    # 构建待签名字符串
    credential_scope = f"{datestamp}/{region}/{service}/request"  # 凭证范围
    string_to_sign = (
        f"{algorithm}\n"
        f"{current_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )
    print(f"[INFO] 待签名字符串构建完成，凭证范围: {credential_scope}")

    # 生成签名密钥并计算签名
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    print(f"[INFO] 签名计算完成: {signature}")

    # 构建Authorization请求头
    authorization_header = (
        f"{algorithm} "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )
    
    # 构建完整请求头
    headers = {
        'X-Date': current_date,
        'Authorization': authorization_header,
        'X-Content-Sha256': payload_hash,
        'Content-Type': content_type
    }
    print(f"[INFO] 请求头构建完成")

    # 发送请求
    request_url = f"{endpoint}?{canonical_querystring}"
    print(f'\n[INFO] 开始发送请求++++++++++++++++++++++++++++++++++++')
    print(f'[INFO] 请求URL: {request_url}')
    
    try:
        # 发送POST请求
        print(f"[INFO] 发送POST请求，请求体: {req_body}")
        r = requests.post(request_url, headers=headers, data=req_body)
    except Exception as err:
        print(f'[ERROR] 请求发送失败: {err}')
        raise  # 抛出异常，让上层处理
    else:
        print(f'\n[INFO] 收到响应++++++++++++++++++++++++++++++++++++')
        print(f'[INFO] 响应状态码: {r.status_code}')
        
        # 处理响应
        try:
            val = r.json()
            print(f"[INFO] 响应内容: {json.dumps(val, indent=2)}")
            
            # 提取base64图片数据并转换保存
            api_response_base64 = val['data']['binary_data_base64'][0]
            print(f"[INFO] 提取到图片base64数据，长度: {len(api_response_base64)}")
            return base64_to_image(api_response_base64)
            
        except KeyError as e:
            print(f"[ERROR] 响应数据格式错误，缺少字段: {e}")
            return None
        except json.JSONDecodeError:
            print(f"[ERROR] 响应内容不是有效的JSON格式: {r.text}")
            return None


def jimeng_generate_api(prompt):
    """
    调用火山引擎即梦生图API生成图片
    
    参数:
        prompt: 生成图片的提示词（文本描述）
    """
    print(f"[INFO] 开始调用即梦生图API，提示词: {prompt}")
    
    # 构建请求查询参数（按API文档要求）
    query_params = {
        'Action': 'CVProcess',  # API操作名称
        'Version': '2022-08-31',  # API版本
    }
    formatted_query = formatQuery(query_params)

    # 构建请求体（按API文档要求）
    body_params = {
        "req_key": "jimeng_t2i_v40",  # 指定生图模型
        "prompt": prompt  # 图片生成提示词
    }
    formatted_body = json.dumps(body_params)
    print(f"[INFO] 构建请求体: {formatted_body}")
    
    # 调用签名并发送请求
    signV4Request(access_key, secret_key, service, formatted_query, formatted_body)


if __name__ == "__main__":
    """程序入口：调用即梦生图API生成"一个可爱的小狗"的图片"""
    print(f"[INFO] 程序启动，开始生成图片...")
    jimeng_generate_api("一个可爱的小狗")
    print(f"[INFO] 程序执行完成")