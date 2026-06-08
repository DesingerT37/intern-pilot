"""
SQLite 数据库初始化脚本
用于开发和 MVP 阶段
"""
import sqlite3
import os
from pathlib import Path


def init_sqlite_db(db_path: str = "internpilot.db"):
    """初始化 SQLite 数据库"""
    
    # 确保数据库目录存在
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取 SQL 脚本
    schema_file = Path(__file__).parent / "schema.sql"
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 执行建表语句
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"✅ SQLite 数据库初始化成功: {db_path}")
        
        # 显示表列表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📊 已创建 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def check_db_exists(db_path: str = "internpilot.db") -> bool:
    """检查数据库是否存在"""
    return Path(db_path).exists()


def reset_db(db_path: str = "internpilot.db"):
    """重置数据库（删除并重新创建）"""
    if check_db_exists(db_path):
        os.remove(db_path)
        print(f"🗑️  已删除旧数据库: {db_path}")
    
    return init_sqlite_db(db_path)


if __name__ == "__main__":
    import sys
    
    # 默认数据库路径
    db_path = "internpilot.db"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "reset":
            print("⚠️  警告: 即将重置数据库，所有数据将被删除！")
            confirm = input("确认继续？(yes/no): ")
            if confirm.lower() == "yes":
                reset_db(db_path)
            else:
                print("❌ 操作已取消")
        else:
            db_path = sys.argv[1]
            init_sqlite_db(db_path)
    else:
        # 检查数据库是否已存在
        if check_db_exists(db_path):
            print(f"⚠️  数据库已存在: {db_path}")
            print("提示: 使用 'python init_sqlite.py reset' 重置数据库")
        else:
            init_sqlite_db(db_path)
