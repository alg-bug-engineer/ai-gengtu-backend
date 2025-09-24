# app.py
import os
import sys
import re
import logging
import requests  # 新增导入 requests 库
from datetime import datetime, timezone

from flask import Flask, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from bcrypt import hashpw, gensalt, checkpw
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()
from dotenv import load_dotenv

load_dotenv()

# 将 api 目录添加到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
# 移除 genemi_api 导入，因为它将不再被直接调用
from api.jimeng_api import jimeng_generate_api

# 应用配置
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://your_db_user:your_db_password@localhost:5433/meme_generator')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_session')
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
)
app.config['CORS_HEADERS'] = 'Content-Type'

# 从环境变量中获取新加坡服务的URL
SINGAPORE_GEMINI_API_URL = os.environ.get('SINGAPORE_GEMINI_API_URL')
if not SINGAPORE_GEMINI_API_URL:
    logging.critical("SINGAPORE_GEMINI_API_URL is not set in environment variables!")
    sys.exit(1)

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/api/*": {"origins": ["http://8.149.232.39:4000", "http://127.0.0.1:4000"], "supports_credentials": True}})


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Flask 应用初始化完成。")

# --- 数据库模型 ---

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    generation_credits = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    generations = db.relationship('Generation', backref='user', lazy=True)

    def set_password(self, password):
        logging.info(f"Setting password for user: {self.email}")
        self.password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        logging.info(f"Password hash created.")

    def check_password(self, password):
        logging.info(f"Checking password for user: {self.email}")
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class InvitationCode(db.Model):
    __tablename__ = 'invitation_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    expires_at = db.Column(db.TIMESTAMP(timezone=True))
    is_used = db.Column(db.Boolean, nullable=False, default=False)
    used_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))

class Generation(db.Model):
    __tablename__ = 'generations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    riddle_answer = db.Column(db.Text)
    prompt_text = db.Column(db.Text)
    image_url = db.Column(db.String(512))
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))

# --- Flask-Login 用户加载器 ---
@login_manager.user_loader
def load_user(user_id):
    logging.info(f"Attempting to load user with ID: {user_id}")
    return User.query.get(int(user_id))

# --- API 路由 ---
PROMPT_PATTERN = r'```json(.*?)```'


@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """
    获取当前用户的所有历史生成记录
    """
    logging.info(f"API route /api/history called for user: {current_user.email}")
    
    # 查询当前用户的所有生成记录，按创建时间降序排列
    user_generations = Generation.query.filter_by(user_id=current_user.id).order_by(Generation.created_at.desc()).all()
    
    history_list = []
    for gen in user_generations:
        history_list.append({
            "id": gen.id,
            "riddle_answer": gen.riddle_answer,
            "image_url": gen.image_url,
            "created_at": gen.created_at.isoformat()
        })
    
    logging.info(f"Returning {len(history_list)} history records for user {current_user.email}")
    return jsonify(history_list), 200

@app.route('/generated_images/<path:filename>')
def serve_generated_image(filename):
    """
    通过 HTTP 接口向前端提供生成的图片文件
    """
    # 构造完整的本地文件路径
    image_dir = os.environ.get("DEFAULT_IMAGE_DIR", "/root/ai-gengtu-backend/images")
    full_path = os.path.join(image_dir, filename)
    
    # 检查文件是否存在
    if not os.path.exists(full_path):
        return "File not found", 404

    # 使用 Flask 的 send_file 发送文件
    # mimetype 'image/jpeg' 或 'image/png' 根据实际情况调整
    return send_file(full_path, mimetype='image/jpeg')

@app.route('/api/register', methods=['POST'])
def register():
    logging.info("API route /api/register called.")
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    invitation_code = data.get('invitationCode')

    if not all([email, password, invitation_code]):
        logging.warning("Registration failed: Missing required fields.")
        return jsonify({"message": "Missing required fields."}), 400

    logging.info(f"Attempting registration for email: {email}")

    # 1. 验证邀请码
    code_record = InvitationCode.query.filter_by(code=invitation_code).first()
    if not code_record or code_record.is_used:
        logging.warning(f"Registration failed for email {email}: Invalid or used invitation code provided.")
        # 在这里直接返回错误，而不是抛出异常
        return jsonify({"message": "Invalid or used invitation code."}), 400

    logging.info("Invitation code validated successfully.")

    # 2. 验证邮箱是否已注册
    if User.query.filter_by(email=email).first():
        logging.warning(f"Registration failed: Email {email} is already registered.")
        return jsonify({"message": "Email already registered."}), 409

    try:
        # 3. 创建新用户
        logging.info("Creating new user account.")
        new_user = User(email=email, username=email, generation_credits=10)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # 4. 更新邀请码状态
        logging.info(f"Updating invitation code {invitation_code} status.")
        code_record.is_used = True
        code_record.used_by_user_id = new_user.id
        
        db.session.commit()
        logging.info(f"User {email} registered successfully.")
        return jsonify({"message": "Registration successful."}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration failed for email {email}: {e}", exc_info=True)
        return jsonify({"message": "An error occurred during registration."}), 500

@app.route('/api/login', methods=['POST'])
def login():
    logging.info("API route /api/login called.")
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    logging.info(f"Attempting login for email: {email}")
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        logging.info(f"Login successful for user: {email}. Credits: {user.generation_credits}")
        return jsonify({"message": "Login successful.", "email": user.email, "credits": user.generation_credits}), 200
    else:
        logging.warning(f"Login failed for email {email}: Invalid credentials.")
        return jsonify({"message": "Invalid email or password."}), 401

@app.route('/api/logout')
@login_required
def logout():
    logging.info(f"User {current_user.email} is logging out.")
    logout_user()
    logging.info("Logout successful.")
    return jsonify({"message": "Logout successful."}), 200

@app.route('/api/user', methods=['GET'])
@login_required
def get_user_info():
    logging.info(f"API route /api/user called for user: {current_user.email}")
    return jsonify({
        "email": current_user.email,
        "credits": current_user.generation_credits
    }), 200

@app.route('/api/generate_meme', methods=['POST'])
@login_required
def generate_meme():
    logging.info(f"API route /api/generate_meme called by user: {current_user.email}")
    data = request.get_json()
    answer = data.get('answer')
    logging.info(f"Received request for meme generation. Answer: {answer}")

    if not answer:
        logging.warning("Meme generation failed: Missing 'answer' parameter.")
        return jsonify({"message": "Missing 'answer' parameter."}), 400
    
    # 商业化逻辑: 检查用户额度
    logging.info(f"Checking credits for user {current_user.email}. Current credits: {current_user.generation_credits}")
    if current_user.generation_credits <= 0:
        logging.warning(f"Meme generation failed for user {current_user.email}: No credits left.")
        return jsonify({"message": "You have no credits left."}), 402

    # 创建生成记录，初始状态为 pending
    logging.info("Creating new generation record in the database.")
    new_generation = Generation(user_id=current_user.id, riddle_answer=answer, status='pending')
    db.session.add(new_generation)
    db.session.commit()
    logging.info(f"New generation record created with ID: {new_generation.id}")

    try:
        # 1. 调用部署在新加坡的 Gemini API 代理服务
        logging.info("Step 1: Calling remote Gemini API proxy.")
        # 向新加坡服务发送请求，获取提示词
        gemini_response = requests.post(SINGAPORE_GEMINI_API_URL, json={'answer': answer})
        gemini_response.raise_for_status() # 检查HTTP响应状态
        
        gemini_data = gemini_response.json()
        raw_prompt_text = gemini_data.get('prompt')

        if not raw_prompt_text:
            raise ValueError("Gemini API proxy returned an empty response.")
        
        matches = re.findall(PROMPT_PATTERN, raw_prompt_text, re.DOTALL)
        if not matches or len(matches) < 2:
            logging.error(f"Failed to parse Gemini response. Response was: {raw_prompt_text}")
            raise ValueError("Gemini 响应格式不正确，无法解析出提示词。")
        chinese_prompt = matches[1].strip()
        logging.info("Step 1 complete. Successfully parsed Chinese prompt.")

        # 2. 调用 jimeng_api 生成图片
        logging.info("Step 2: Calling jimeng_api to generate image.")
        image_path = jimeng_generate_api(chinese_prompt)
        
        if not image_path:
            logging.error("Jimeng API call failed. No image path returned.")
            raise Exception("图片生成失败，未返回有效的图片路径。")
        logging.info(f"Step 2 complete. Image saved at: {image_path}")
            
        # 3. 成功后，更新数据库记录和用户额度
        logging.info(f"Step 3: Updating user credits and generation record for ID: {new_generation.id}")
        current_user.generation_credits -= 1
        new_generation.prompt_text = raw_prompt_text # 存储完整提示词
        new_generation.image_url = f"/generated_images/{os.path.basename(image_path)}" # 存储相对URL
        new_generation.status = 'completed'
        db.session.commit()
        logging.info(f"Database updated successfully. Remaining credits for user {current_user.email}: {current_user.generation_credits}")
        
        return send_file(image_path, mimetype='image/png')
        
    except ValueError as ve:
        logging.error(f"Processing failed due to a ValueError: {ve}")
        db.session.rollback()
        new_generation.status = 'failed'
        db.session.commit()
        return jsonify({"message": str(ve)}), 500
    except requests.exceptions.RequestException as ree:
        logging.error(f"Failed to connect to Singapore Gemini API proxy: {ree}")
        db.session.rollback()
        new_generation.status = 'failed'
        db.session.commit()
        return jsonify({"message": "无法连接到海外服务，请稍后再试。"}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred during meme generation: {e}", exc_info=True)
        db.session.rollback()
        new_generation.status = 'failed'
        db.session.commit()
        return jsonify({"message": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    logging.info("Starting Flask application.")
    # 在应用启动时创建数据库表（仅在开发环境中）
    with app.app_context():
        logging.info("Creating database tables...")
        db.create_all()
        logging.info("Database tables created successfully.")
    app.run(debug=False, host='0.0.0.0', port=5550)