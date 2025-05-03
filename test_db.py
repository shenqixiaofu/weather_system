from app import app, db
with app.app_context():
    try:
        db.engine.connect()
        print("[成功] 数据库连接正常")
        db.drop_all()
        db.create_all()
        print("[成功] 数据表创建完成")
    except Exception as e:
        print(f"[失败] 错误信息: {str(e)}")