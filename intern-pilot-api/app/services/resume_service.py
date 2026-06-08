"""
简历解析服务
"""
import json
from pathlib import Path
from typing import Optional
from loguru import logger

from app.tools.document_parser import DocumentParser
from app.services.llm_service import llm_service
from app.models.schemas import Resume


class ResumeService:
    """简历解析服务"""
    
    @staticmethod
    async def parse_resume_file(file_path: str) -> tuple[str, Resume]:
        """
        解析简历文件
        
        Args:
            file_path: 简历文件路径
            
        Returns:
            (markdown_text, resume_data)
        """
        # 1. 文档解析：转换为 Markdown
        logger.info(f"📄 开始解析简历文件: {file_path}")
        md_text = DocumentParser.parse(file_path)
        
        # 2. LLM 结构化提取
        logger.info("🤖 使用 LLM 提取结构化信息...")
        resume_data = await ResumeService._extract_structured_data(md_text)
        
        return md_text, resume_data
    
    @staticmethod
    async def _extract_structured_data(md_text: str) -> Resume:
        """
        使用 LLM 从 Markdown 文本中提取结构化数据
        
        Args:
            md_text: Markdown 格式的简历文本
            
        Returns:
            Resume 对象
        """
        # 构建 Prompt
        system_prompt = """你是一个专业的简历解析专家。你的任务是从简历文本中提取结构化信息。

请严格按照以下 JSON Schema 格式返回数据：

{
  "name": "姓名",
  "email": "邮箱（如果有）",
  "phone": "电话（如果有）",
  "target_position": "目标职位（如果有）",
  "education": [
    {
      "school": "学校名称",
      "degree": "学位（本科/硕士/博士）",
      "major": "专业",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "gpa": GPA（数字，如果有）
    }
  ],
  "skills": ["技能1", "技能2", ...],
  "projects": [
    {
      "name": "项目名称",
      "role": "担任角色",
      "tech_stack": ["技术1", "技术2"],
      "description": "项目描述",
      "achievements": ["成果1", "成果2"],
      "start_date": "开始时间（如果有）",
      "end_date": "结束时间（如果有）"
    }
  ],
  "work_experience": [
    {
      "company": "公司名称",
      "position": "职位",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "responsibilities": ["职责1", "职责2"],
      "achievements": ["成果1", "成果2"]
    }
  ],
  "certifications": ["证书1", "证书2"],
  "awards": ["奖项1", "奖项2"]
}

注意：
1. 如果某个字段在简历中没有，可以设为 null 或空数组
2. 日期格式尽量统一为 "YYYY-MM" 或 "YYYY"
3. 技能要提取编程语言、框架、工具等
4. 只返回 JSON，不要包含任何其他文本
"""
        
        user_prompt = f"请解析以下简历：\n\n{md_text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 调用 LLM
        response = await llm_service.chat_completion(
            messages=messages,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        # 解析 JSON
        try:
            data = json.loads(response)
            resume = Resume(**data)
            logger.info(f"✅ 简历解析成功: {resume.name}")
            return resume
        except Exception as e:
            logger.error(f"❌ JSON 解析失败: {str(e)}")
            logger.error(f"LLM 响应: {response}")
            raise Exception(f"简历数据解析失败: {str(e)}")


# 创建全局服务实例
resume_service = ResumeService()
