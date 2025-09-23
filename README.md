# ai-gengtu-backend

数据迁移：

export FLASK_APP=app.py

# 1. 初始化 (只需执行一次)
flask db init

# 2. 生成迁移脚本
flask db migrate -m "Initial migration with user, code, and generation tables."

# 3. 应用迁移到数据库
flask db upgrade