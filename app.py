# app.py
import os
import sys
import re
import logging
from datetime import datetime, timezone

from flask import Flask, request, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from bcrypt import hashpw, gensalt, checkpw
from flask_migrate import Migrate # <-- 新增导入

# 将 api 目录添加到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
from api.genemi_api import genemi_generate_api
from api.jimeng_api import jimeng_generate_api

# 应用配置
app = Flask(__name__)
# 使用环境变量配置数据库，确保生产环境安全
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://your_db_user:your_db_password@localhost:5432/meme_generator')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_session')
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=False, # 在本地开发时可以设置为 False
    SESSION_COOKIE_DOMAIN='localhost' # 设置为你的后端域名或IP
)
app.config['CORS_HEADERS'] = 'Content-Type'

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db) # <-- 新增这行，关联应用和数据库
CORS(app, supports_credentials=True) # 启用 CORS，允许跨域携带凭证
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000", "supports_credentials": True}})


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        self.password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    def check_password(self, password):
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
    return User.query.get(int(user_id))

# --- API 路由 ---
PROMPT_PATTERN = r'```json(.*?)```'

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    invitation_code = data.get('invitationCode')

    if not all([email, password, invitation_code]):
        return jsonify({"message": "Missing required fields."}), 400

    # 1. 验证邀请码
    code_record = InvitationCode.query.filter_by(code=invitation_code).first()
    if not code_record or code_record.is_used:
        return jsonify({"message": "Invalid or used invitation code."}), 400

    # 2. 验证邮箱是否已注册
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered."}), 409

    try:
        # 3. 创建新用户
        new_user = User(email=email, username=email, generation_credits=10) # 假设邀请码赠送10次
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush() # 确保获取到新用户的ID

        # 4. 更新邀请码状态
        code_record.is_used = True
        code_record.used_by_user_id = new_user.id
        
        db.session.commit()
        return jsonify({"message": "Registration successful."}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration failed: {e}")
        return jsonify({"message": "An error occurred during registration."}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Login successful.", "email": user.email, "credits": user.generation_credits}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful."}), 200

@app.route('/api/user', methods=['GET'])
@login_required
def get_user_info():
    return jsonify({
        "email": current_user.email,
        "credits": current_user.generation_credits
    }), 200

@app.route('/api/generate_meme', methods=['POST'])
@login_required
def generate_meme():
    data = request.get_json()
    answer = data.get('answer')

    if not answer:
        return jsonify({"message": "Missing 'answer' parameter."}), 400
    
    # 商业化逻辑: 检查用户额度
    if current_user.generation_credits <= 0:
        return jsonify({"message": "You have no credits left."}), 402

    # 创建生成记录，初始状态为 pending
    new_generation = Generation(user_id=current_user.id, riddle_answer=answer, status='pending')
    db.session.add(new_generation)
    db.session.commit()

    try:
        # 1. 调用 genemi_api 生成提示词
        gemini_response = genemi_generate_api(answer)
        matches = re.findall(PROMPT_PATTERN, gemini_response, re.DOTALL)
        if not matches or len(matches) < 2:
            raise ValueError("Gemini 响应格式不正确，无法解析出提示词。")
        chinese_prompt = matches[1].strip()

        # 2. 调用 jimeng_api 生成图片
        image_path = jimeng_generate_api(chinese_prompt)
        
        if not image_path:
            raise Exception("图片生成失败，未返回有效的图片路径。")
            
        # 3. 成功后，更新数据库记录和用户额度
        current_user.generation_credits -= 1
        new_generation.prompt_text = gemini_response # 存储完整提示词
        new_generation.image_url = f"/generated_images/{os.path.basename(image_path)}" # 存储相对URL
        new_generation.status = 'completed'
        db.session.commit()
        
        return send_file(image_path, mimetype='image/png')
        
    except ValueError as ve:
        db.session.rollback()
        new_generation.status = 'failed'
        db.session.commit()
        logging.error(f"处理失败: {ve}")
        return jsonify({"message": str(ve)}), 500
    except Exception as e:
        db.session.rollback()
        new_generation.status = 'failed'
        db.session.commit()
        logging.error(f"发生未预期错误: {e}")
        return jsonify({"message": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    # 在应用启动时创建数据库表（仅在开发环境中）
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='localhost', port=5550)