"""
快速测试脚本
测试简历解析和 JD 解析功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.resume_service import resume_service
from app.services.jd_service import jd_service


async def test_resume_parse():
    """测试简历解析"""
    print("\n" + "="*50)
    print("测试简历解析")
    print("="*50)
    
    resume_file = "test_resume.md"
    
    if not Path(resume_file).exists():
        print(f"❌ 测试文件不存在: {resume_file}")
        return
    
    try:
        md_text, resume_data = await resume_service.parse_resume_file(resume_file)
        
        print(f"\n✅ 解析成功!")
        print(f"姓名: {resume_data.name}")
        print(f"邮箱: {resume_data.email}")
        print(f"电话: {resume_data.phone}")
        print(f"目标职位: {resume_data.target_position}")
        print(f"技能数量: {len(resume_data.skills)}")
        print(f"项目数量: {len(resume_data.projects)}")
        print(f"教育背景: {len(resume_data.education)}")
        
        if resume_data.skills:
            print(f"\n核心技能: {', '.join(resume_data.skills[:5])}")
        
    except Exception as e:
        print(f"\n❌ 解析失败: {str(e)}")


async def test_jd_parse():
    """测试 JD 解析"""
    print("\n" + "="*50)
    print("测试 JD 解析")
    print("="*50)
    
    jd_text = """
【岗位职责】
1. 负责公司前端项目的开发和维护
2. 参与产品需求评审，提供技术方案
3. 优化前端性能，提升用户体验

【任职要求】
1. 本科及以上学历，计算机相关专业
2. 熟练掌握 Vue 3 或 React 框架
3. 熟悉 TypeScript、Webpack、Vite 等工具
4. 了解前端工程化和性能优化
5. 有良好的团队协作能力

【加分项】
1. 有开源项目经验
2. 熟悉 Node.js 后端开发
3. 了解微前端架构
    """
    
    try:
        jd_data, keywords = await jd_service.parse_jd(jd_text)
        
        print(f"\n✅ 解析成功!")
        print(f"公司: {jd_data.company}")
        print(f"职位: {jd_data.position}")
        print(f"必备技能数量: {len(jd_data.required_skills)}")
        print(f"加分项数量: {len(jd_data.preferred_skills)}")
        
        if jd_data.required_skills:
            print(f"\n必备技能: {', '.join(jd_data.required_skills[:5])}")
        
        if keywords:
            print(f"\n关键词: {', '.join(keywords)}")
        
    except Exception as e:
        print(f"\n❌ 解析失败: {str(e)}")


async def main():
    """主函数"""
    print("\n🚀 InternPilot API 快速测试")
    print("="*50)
    
    # 检查环境变量
    from app.core.config import settings
    
    if not settings.OPENAI_API_KEY:
        print("\n⚠️  警告: 未配置 OPENAI_API_KEY")
        print("请在 .env 文件中配置 LLM API Key")
        print("\n示例:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    print(f"\n✅ LLM 配置: {settings.OPENAI_MODEL}")
    
    # 运行测试
    await test_resume_parse()
    await test_jd_parse()
    
    print("\n" + "="*50)
    print("测试完成!")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
