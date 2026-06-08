"""
测试 ResumeOptimizationService 的核心逻辑
"""
from app.services.resume_optimization_service import ResumeOptimizationService


def test_extract_markdown_section():
    """测试 Markdown 代码块提取"""
    
    # 测试用例 1: 标准格式
    response1 = """我建议优化你的项目经历：

```markdown
### 项目经历

#### 智能简历分析系统
- 开发了基于 AI 的简历分析平台
- 使用 Python + FastAPI + Vue 3
```

这样会更清晰。"""
    
    result1 = ResumeOptimizationService.extract_markdown_section(response1)
    print("测试 1 - 标准格式:")
    print(f"提取结果: {result1}")
    assert result1 is not None
    assert "项目经历" in result1
    print("✅ 通过\n")
    
    # 测试用例 2: 通用代码块
    response2 = """这是修改后的内容：

```
### 教育经历

**北京大学** | 计算机科学与技术 | 本科 | 2019-2023
```
"""
    
    result2 = ResumeOptimizationService.extract_markdown_section(response2)
    print("测试 2 - 通用代码块:")
    print(f"提取结果: {result2}")
    assert result2 is not None
    assert "教育经历" in result2
    print("✅ 通过\n")
    
    # 测试用例 3: 没有代码块
    response3 = "这是一个普通的回复，没有代码块。"
    
    result3 = ResumeOptimizationService.extract_markdown_section(response3)
    print("测试 3 - 没有代码块:")
    print(f"提取结果: {result3}")
    assert result3 is None
    print("✅ 通过\n")


def test_detect_section_type():
    """测试段落类型检测"""
    
    # 测试教育经历
    content1 = """### 教育经历

**北京大学** | 计算机科学与技术 | 本科 | 2019-2023"""
    
    result1 = ResumeOptimizationService.detect_section_type(content1)
    print("测试 1 - 教育经历:")
    print(f"检测结果: {result1}")
    assert result1 == "education"
    print("✅ 通过\n")
    
    # 测试项目经历
    content2 = """### 项目经历

#### 智能简历分析系统
**技术栈**: Python, FastAPI, Vue 3"""
    
    result2 = ResumeOptimizationService.detect_section_type(content2)
    print("测试 2 - 项目经历:")
    print(f"检测结果: {result2}")
    assert result2 == "projects"
    print("✅ 通过\n")
    
    # 测试工作经验
    content3 = """### 工作经历

**字节跳动** | 后端开发实习生 | 2023.06 - 2023.12"""
    
    result3 = ResumeOptimizationService.detect_section_type(content3)
    print("测试 3 - 工作经历:")
    print(f"检测结果: {result3}")
    assert result3 == "work_experience"
    print("✅ 通过\n")
    
    # 测试技能
    content4 = """### 专业技能

- **编程语言**: Python, JavaScript, TypeScript
- **框架**: FastAPI, Vue 3, React"""
    
    result4 = ResumeOptimizationService.detect_section_type(content4)
    print("测试 4 - 技能:")
    print(f"检测结果: {result4}")
    assert result4 == "skills"
    print("✅ 通过\n")
    
    # 测试无法识别
    content5 = """这是一段普通文本，没有明确的类型标识。"""
    
    result5 = ResumeOptimizationService.detect_section_type(content5)
    print("测试 5 - 无法识别:")
    print(f"检测结果: {result5}")
    assert result5 is None
    print("✅ 通过\n")


def test_extract_explanation():
    """测试修改说明提取"""
    
    # 测试用例 1: 有说明和代码块
    response1 = """我建议对你的项目经历进行以下优化：
1. 突出技术栈和具体成果
2. 使用量化数据展示项目影响力

修改后的内容如下：

```markdown
### 项目经历

#### 智能简历分析系统
```
"""
    
    result1 = ResumeOptimizationService.extract_explanation(response1)
    print("测试 1 - 有说明和代码块:")
    print(f"提取结果: {result1}")
    assert result1 is not None
    assert "优化" in result1
    assert "```" not in result1  # 不应包含代码块标记
    print("✅ 通过\n")
    
    # 测试用例 2: 只有代码块
    response2 = """```markdown
### 教育经历
```"""
    
    result2 = ResumeOptimizationService.extract_explanation(response2)
    print("测试 2 - 只有代码块:")
    print(f"提取结果: {result2}")
    # 应该返回空字符串或 None
    print("✅ 通过\n")
    
    # 测试用例 3: 没有代码块
    response3 = "这是一个完整的说明文本，没有代码块。"
    
    result3 = ResumeOptimizationService.extract_explanation(response3)
    print("测试 3 - 没有代码块:")
    print(f"提取结果: {result3}")
    assert result3 == response3
    print("✅ 通过\n")


def test_build_messages():
    """测试消息构建逻辑"""
    from app.models.schemas import ResumeChatMessage
    from datetime import datetime
    
    resume_content = """# 张三的简历

## 教育经历
北京大学 | 计算机科学 | 2019-2023

## 项目经历
智能简历分析系统"""
    
    user_message = "请帮我优化项目经历部分"
    
    # 创建历史对话
    context = [
        ResumeChatMessage(
            role="user",
            content="你好",
            timestamp=datetime.now()
        ),
        ResumeChatMessage(
            role="assistant",
            content="你好！我是简历优化助手。",
            timestamp=datetime.now()
        )
    ]
    
    suggestions = ["突出技术栈", "添加量化数据"]
    
    messages = ResumeOptimizationService._build_messages(
        resume_content=resume_content,
        user_message=user_message,
        context=context,
        suggestions=suggestions
    )
    
    print("测试 - 消息构建:")
    print(f"消息数量: {len(messages)}")
    
    # 验证消息结构
    assert len(messages) >= 4  # system + resume + context + user
    assert messages[0]["role"] == "system"
    assert "简历优化顾问" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "完整简历内容" in messages[1]["content"]
    
    # 验证建议被添加
    last_message = messages[-1]["content"]
    assert "突出技术栈" in last_message
    assert "添加量化数据" in last_message
    
    print("✅ 通过\n")


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试 ResumeOptimizationService")
    print("=" * 60 + "\n")
    
    try:
        test_extract_markdown_section()
        test_detect_section_type()
        test_extract_explanation()
        test_build_messages()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
