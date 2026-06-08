"""
测试 ExportService 导出功能
"""
import os
import tempfile
from app.services.export_service import ExportService

# 测试用的 Markdown 内容
test_markdown = """# 张三

**联系方式**: zhangsan@example.com | 138-0000-0000

## 教育经历

### 清华大学 - 计算机科学与技术 (2018-2022)
- GPA: 3.8/4.0
- 主修课程: 数据结构、算法设计、机器学习

## 工作经验

### 字节跳动 - 后端开发工程师 (2022-至今)
- 负责推荐系统后端开发
- 使用 Python、Go 开发高性能服务
- 优化系统性能，QPS 提升 30%

## 项目经历

### 智能简历优化系统
- **技术栈**: Python, FastAPI, Vue.js, PostgreSQL
- **职责**: 
  - 设计并实现 AI 简历优化功能
  - 集成 LLM API 进行智能对话
  - 实现 PDF/DOCX 导出功能

## 技能

- **编程语言**: Python, JavaScript, Go
- **框架**: FastAPI, Vue.js, Django
- **数据库**: PostgreSQL, MySQL, Redis
- **工具**: Git, Docker, Kubernetes
"""

def test_markdown_to_html():
    """测试 Markdown 转 HTML"""
    print("🧪 测试 Markdown 转 HTML...")
    html = ExportService.markdown_to_html(test_markdown)
    assert '<h1>' in html
    assert '<h2>' in html
    assert '<ul>' in html or '<li>' in html
    print("✅ Markdown 转 HTML 测试通过")

def test_export_to_pdf():
    """测试导出 PDF"""
    print("\n🧪 测试导出 PDF...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        # 测试三种样式
        for style in ['default', 'modern', 'classic']:
            output_path = os.path.join(tmpdir, f'resume_{style}.pdf')
            result = ExportService.export_to_pdf(test_markdown, output_path, style)
            
            assert os.path.exists(result), f"PDF 文件未生成: {result}"
            assert os.path.getsize(result) > 0, f"PDF 文件为空: {result}"
            print(f"  ✅ {style} 样式 PDF 生成成功: {os.path.getsize(result)} bytes")

def test_export_to_docx():
    """测试导出 DOCX"""
    print("\n🧪 测试导出 DOCX...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        # 测试三种样式
        for style in ['default', 'modern', 'classic']:
            output_path = os.path.join(tmpdir, f'resume_{style}.docx')
            result = ExportService.export_to_docx(test_markdown, output_path, style)
            
            assert os.path.exists(result), f"DOCX 文件未生成: {result}"
            assert os.path.getsize(result) > 0, f"DOCX 文件为空: {result}"
            print(f"  ✅ {style} 样式 DOCX 生成成功: {os.path.getsize(result)} bytes")

def test_chinese_support():
    """测试中文字符支持"""
    print("\n🧪 测试中文字符支持...")
    
    chinese_markdown = """# 简历测试

## 个人信息
- 姓名: 张三
- 邮箱: zhangsan@example.com

## 技能
- Python 开发
- 机器学习
- 数据分析
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 测试 PDF
        pdf_path = os.path.join(tmpdir, 'chinese_test.pdf')
        ExportService.export_to_pdf(chinese_markdown, pdf_path)
        assert os.path.exists(pdf_path)
        print("  ✅ 中文 PDF 生成成功")
        
        # 测试 DOCX
        docx_path = os.path.join(tmpdir, 'chinese_test.docx')
        ExportService.export_to_docx(chinese_markdown, docx_path)
        assert os.path.exists(docx_path)
        print("  ✅ 中文 DOCX 生成成功")

if __name__ == '__main__':
    print("=" * 60)
    print("ExportService 功能测试")
    print("=" * 60)
    
    try:
        test_markdown_to_html()
        test_export_to_pdf()
        test_export_to_docx()
        test_chinese_support()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
