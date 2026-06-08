"""
执行 resume_versions 表迁移脚本
"""
import sqlite3
import uuid
from pathlib import Path

def run_migration():
    """执行迁移"""
    db_path = Path("internpilot.db")
    sql_file = Path("create_resume_versions_table.sql")
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    if not sql_file.exists():
        print(f"❌ SQL 文件不存在: {sql_file}")
        return False
    
    # 读取 SQL 文件
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 连接数据库
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 执行 SQL 脚本
        print("📝 开始执行迁移脚本...")
        cursor.executescript(sql_content)
        conn.commit()
        print("✅ 迁移脚本执行成功！")
        
        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resume_versions'")
        result = cursor.fetchone()
        
        if result:
            print("\n✅ resume_versions 表创建成功！")
            
            # 显示表结构
            cursor.execute("PRAGMA table_info(resume_versions)")
            columns = cursor.fetchall()
            print("\n📋 表结构：")
            for col in columns:
                col_id, name, type_, notnull, default, pk = col
                nullable = "NOT NULL" if notnull else "NULL"
                pk_str = " PRIMARY KEY" if pk else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  - {name}: {type_} {nullable}{default_str}{pk_str}")
            
            # 显示索引
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='resume_versions'")
            indexes = cursor.fetchall()
            if indexes:
                print("\n📊 索引：")
                for idx in indexes:
                    print(f"  - {idx[0]}")
            
            # 显示外键
            cursor.execute("PRAGMA foreign_key_list(resume_versions)")
            foreign_keys = cursor.fetchall()
            if foreign_keys:
                print("\n🔗 外键约束：")
                for fk in foreign_keys:
                    fk_id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                    print(f"  - {from_col} -> {table}({to_col}) ON DELETE {on_delete}")
            
            return True
        else:
            print("❌ 表创建失败！")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ 执行迁移时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Resume Versions 表迁移脚本")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    print("=" * 60)
    if success:
        print("✅ 迁移完成！")
    else:
        print("❌ 迁移失败！")
    print("=" * 60)
