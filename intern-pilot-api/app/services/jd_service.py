"""
JD (岗位需求) 解析服务
"""
import json
import re
from typing import List
from loguru import logger

from app.services.llm_service import llm_service
from app.models.schemas import JobDescription


class JDService:
    """JD 解析服务"""
    
    @staticmethod
    def preprocess_jd_text(jd_text: str) -> str:
        """
        预处理 JD 文本
        
        - 去除多余空白
        - 截断超长文本
        """
        # 去除多余空白
        jd_text = re.sub(r'\s+', ' ', jd_text).strip()
        
        # 截断超长文本（保留前 5000 字符）
        if len(jd_text) > 5000:
            jd_text = jd_text[:5000] + "..."
            logger.warning("⚠️ JD 文本过长，已截断至 5000 字符")
        
        return jd_text
    
    @staticmethod
    async def parse_jd(jd_text: str) -> tuple[JobDescription, List[str]]:
        """
        解析 JD 文本
        
        Args:
            jd_text: JD 文本内容
            
        Returns:
            (jd_data, keywords)
        """
        # 1. 预处理
        jd_text = JDService.preprocess_jd_text(jd_text)
        logger.info(f"📝 开始解析 JD ({len(jd_text)} 字符)")
        
        # 2. LLM 结构化解析
        jd_data = await JDService._extract_structured_data(jd_text)
        
        # 3. 提取关键词
        keywords = await JDService._extract_keywords(jd_text, jd_data)
        
        return jd_data, keywords
    
    @staticmethod
    async def _extract_structured_data(jd_text: str) -> JobDescription:
        """
        使用 LLM 从 JD 文本中提取结构化数据
        """
        system_prompt = """你是一个专业的招聘需求分析专家。你的任务是从岗位需求（JD）中提取结构化信息，用于简历匹配分析。

请严格按照以下 JSON Schema 格式返回数据：

{
  "required_skills": ["必备技能1", "必备技能2", ...],
  "preferred_skills": ["加分项技能1", "加分项技能2", ...],
  "responsibilities": ["工作职责1", "工作职责2", ...],
  "requirements": ["任职要求1", "任职要求2", ...],
  "keywords": ["关键词1", "关键词2", ...]
}

注意：
1. required_skills 是必备技能（如编程语言、框架、工具等），preferred_skills 是加分项技能
2. 如果 JD 中没有明确区分必备和加分项，根据描述的重要程度判断
3. responsibilities 是工作内容和职责描述
4. requirements 是任职条件（如学历、经验年限、软技能等）
5. keywords 是用于搜索和匹配的关键词（提取最重要的 5-10 个）
6. 只返回 JSON，不要包含任何其他文本
"""
        
        user_prompt = f"请解析以下岗位需求：\n\n{jd_text}"
        
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
            jd = JobDescription(**data)
            logger.info(f"✅ JD 解析成功: skills_count={len(jd.required_skills)}, keywords_count={len(jd.keywords)}")
            return jd
        except Exception as e:
            logger.error(f"❌ JSON 解析失败: {str(e)}")
            logger.error(f"LLM 响应: {response}")
            raise Exception(f"JD 数据解析失败: {str(e)}")
    
    @staticmethod
    async def _extract_keywords(jd_text: str, jd_data: JobDescription) -> List[str]:
        """
        提取 JD 关键词
        
        结合规则和 LLM
        """
        keywords = set()
        
        # 1. 从结构化数据中提取
        keywords.update(jd_data.required_skills)
        keywords.update(jd_data.preferred_skills[:3])  # 只取前 3 个加分项
        
        # 2. 使用 LLM 提取额外关键词
        system_prompt = """你是关键词提取专家。从岗位需求中提取 5-8 个最重要的关键词。

关键词应该包括：
- 核心技术栈
- 重要能力要求
- 行业术语

只返回关键词列表，用逗号分隔，不要有其他文字。
例如：Python, FastAPI, 数据库, 团队协作, 问题解决能力"""
        
        user_prompt = f"请从以下 JD 中提取关键词：\n\n{jd_text[:1000]}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=100
            )
            
            # 解析关键词
            llm_keywords = [kw.strip() for kw in response.split(',')]
            keywords.update(llm_keywords[:5])
            
        except Exception as e:
            logger.warning(f"⚠️ LLM 关键词提取失败: {str(e)}")
        
        # 去重并限制数量
        keywords_list = list(keywords)[:10]
        logger.info(f"✅ 提取关键词: {keywords_list}")
        
        return keywords_list


# 创建全局服务实例
jd_service = JDService()
