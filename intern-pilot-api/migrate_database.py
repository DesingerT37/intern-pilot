"""
数据库迁移脚本：修改 boss_jobs 表结构
执行前请备份数据库！
"""
from sqlalchemy import text
from app.core.database import engine

def migrate():
    print("开始数据库迁移...")
    print("=" * 50)
    
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        
        try:
            # 1. 移除 job_id 的唯一约束
            print("1. 移除 job_id 的唯一约束...")
            conn.execute(text("""
                ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_job_id_key;
            """))
            print("   ✓ 完成")
            
            # 2. 移除 user_id 列
            print("2. 移除 user_id 列...")
            conn.execute(text("""
                ALTER TABLE boss_jobs DROP COLUMN IF EXISTS user_id;
            """))
            print("   ✓ 完成")
            
            # 3. 修改 crawl_task_id 为 NOT NULL
            print("3. 修改 crawl_task_id 为 NOT NULL...")
            # 先删除 crawl_task_id 为 NULL 的记录（如果有）
            result = conn.execute(text("""
                DELETE FROM boss_jobs WHERE crawl_task_id IS NULL;
            """))
            print(f"   删除了 {result.rowcount} 条 crawl_task_id 为 NULL 的记录")
            
            conn.execute(text("""
                ALTER TABLE boss_jobs ALTER COLUMN crawl_task_id SET NOT NULL;
            """))
            print("   ✓ 完成")
            
            # 4. 删除旧的外键约束
            print("4. 删除旧的外键约束...")
            conn.execute(text("""
                ALTER TABLE boss_jobs DROP CONSTRAINT IF EXISTS boss_jobs_crawl_task_id_fkey;
            """))
            print("   ✓ 完成")
            
            # 5. 添加新的外键约束（CASCADE 删除）
            print("5. 添加新的外键约束（CASCADE 删除）...")
            conn.execute(text("""
                ALTER TABLE boss_jobs 
                ADD CONSTRAINT boss_jobs_crawl_task_id_fkey 
                FOREIGN KEY (crawl_task_id) 
                REFERENCES crawl_tasks(task_id) 
                ON DELETE CASCADE;
            """))
            print("   ✓ 完成")
            
            # 提交事务
            trans.commit()
            print("\n" + "=" * 50)
            print("✅ 数据库迁移成功完成！")
            print("=" * 50)
            
            # 验证修改
            print("\n验证表结构...")
            result = conn.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'boss_jobs'
                ORDER BY ordinal_position;
            """))
            
            print("\nboss_jobs 表结构：")
            for row in result:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"  - {row[0]}: {row[1]} ({nullable})")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ 迁移失败: {e}")
            print("已回滚所有更改")
            raise

if __name__ == "__main__":
    import sys
    
    print("⚠️  警告：此脚本将修改数据库结构！")
    print("请确保已备份数据库！")
    print()
    
    confirm = input("确认继续？(输入 'yes' 继续): ")
    
    if confirm.lower() == 'yes':
        migrate()
    else:
        print("已取消迁移")
        sys.exit(0)
