"""
匹配分析服务
简历与 JD 的智能匹配分析
"""
import json
from typing import List, Tuple
from loguru import logger

from app.services.llm_service import llm_service
from app.models.schemas import Resume, JobDescription, MatchAnalysis, EnhancementSuggestion


class MatchService:
    """匹配分析服务"""
    
    @staticmethod
    async def analyze_match(resume: Resume, jd: JobDescription) -> MatchAnalysis:
        """
        分析简历与 JD 的匹配度
        Args:
            resume: 简历数据
            jd: JD 数据
            
        Returns:
            MatchAnalysis: 匹配分析结果
        """
        logger.info(f"🔍 开始匹配分析: {resume.name} vs JD (skills: {len(jd.required_skills)})")
        
        # 构建分析 Prompt
        system_prompt = """你是一个专业的简历匹配分析专家。你的任务是分析简历与岗位需求的匹配度。

请严格按照以下 JSON Schema 格式返回数据：

{
  "overall_score": 85.5,  // 总体匹配度评分 (0-100)
  "skill_match_score": 80.0,  // 技能匹配度
  "experience_match_score": 85.0,  // 经验匹配度
  "education_match_score": 90.0,  // 学历匹配度
  "matched_skills": ["技能1", "技能2", ...],  // 已命中的技能
  "missing_skills": ["技能3", "技能4", ...],  // 缺失的技能
  "strengths": ["优势1", "优势2", ...],  // 候选人的优势（3-5条）
  "weaknesses": ["劣势1", "劣势2", ...],  // 候选人的劣势（3-5条）
  "suggestions": ["建议1", "建议2", ...]  // 改进建议（3-5条）
}

评分标准：
- 90-100: 高度匹配，技能完全符合
- 75-89: 较好匹配，核心技能符合
- 60-74: 基本匹配，部分技能符合
- 0-59: 匹配度较低，需要提升

只返回 JSON，不要包含任何其他文本。"""
        
        # 构建简历摘要
        resume_summary = f"""
姓名: {resume.name}
目标职位: {resume.target_position or '未指定'}
技能: {', '.join(resume.skills)}
教育背景: {resume.education[0].school if resume.education else '未提供'} - {resume.education[0].major if resume.education else ''}
项目数量: {len(resume.projects)}
工作经历: {len(resume.work_experience)}
"""
        
        # 构建 JD 摘要
        jd_summary = f"""
必备技能: {', '.join(jd.required_skills)}
加分项: {', '.join(jd.preferred_skills)}
工作职责: {'; '.join(jd.responsibilities[:3])}
任职要求: {'; '.join(jd.requirements[:3])}
"""
        
        user_prompt = f"""请分析以下简历与岗位需求的匹配度：

【简历信息】
{resume_summary}

【岗位需求】
{jd_summary}

请给出详细的匹配分析。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 调用 LLM
        response = await llm_service.chat_completion(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # 解析 JSON
        try:
            data = json.loads(response)
            analysis = MatchAnalysis(**data)
            logger.info(f"✅ 匹配分析完成: 总体匹配度 {analysis.overall_score}%")
            return analysis
        except Exception as e:
            logger.error(f"❌ JSON 解析失败: {str(e)}")
            logger.error(f"LLM 响应: {response}")
            raise Exception(f"匹配分析数据解析失败: {str(e)}")
    
    @staticmethod
    async def generate_enhancements(
        resume: Resume, 
        jd: JobDescription, 
        analysis: MatchAnalysis
    ) -> Tuple[List[EnhancementSuggestion], str]:
        """
        生成简历增强建议
        
        Args:
            resume: 简历数据
            jd: JD 数据
            analysis: 匹配分析结果
            
        Returns:
            (enhancements, report_markdown)
        """
        logger.info(f"✨ 开始生成简历增强建议")
        
        # 构建 Prompt
        system_prompt = """你是一个专业的简历优化顾问。你的任务是根据岗位需求，给出具体的简历修改建议。

请严格按照以下 JSON Schema 格式返回数据：

{
  "enhancements": [
    {
      "priority": 1,  // 优先级 (1-5, 1最高)
      "category": "技能",  // 类别：技能/项目/描述/格式
      "title": "建议标题",
      "description": "详细说明，要具体可操作",
      "example": "示例（可选）"
    }
  ]
}

建议要求：
1. 具体可操作，不要泛泛而谈
2. 针对岗位需求，有的放矢
3. 优先级合理，重要的放前面
4. 至少 5 条，最多 10 条

只返回 JSON，不要包含任何其他文本。"""
        
        # 构建上下文
        context = f"""
【简历信息】
姓名: {resume.name}
技能: {', '.join(resume.skills)}
项目: {len(resume.projects)} 个

【岗位需求】
必备技能: {', '.join(jd.required_skills)}
加分项: {', '.join(jd.preferred_skills)}

【匹配分析】
匹配度: {analysis.overall_score}%
已命中技能: {', '.join(analysis.matched_skills)}
缺失技能: {', '.join(analysis.missing_skills)}
"""
        
        user_prompt = f"""请根据以下信息，生成简历增强建议：

{context}

请给出具体、可操作的修改建议。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 调用 LLM
        response = await llm_service.chat_completion(
            messages=messages,
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        # 解析 JSON
        try:
            data = json.loads(response)
            enhancements = [EnhancementSuggestion(**item) for item in data.get("enhancements", [])]
            logger.info(f"✅ 生成 {len(enhancements)} 条增强建议")
        except Exception as e:
            logger.error(f"❌ JSON 解析失败: {str(e)}")
            enhancements = []
        
        # 生成 Markdown 报告
        report = MatchService._generate_markdown_report(resume, jd, analysis, enhancements)
        
        return enhancements, report
    
    @staticmethod
    def _generate_markdown_report(
        resume: Resume,
        jd: JobDescription,
        analysis: MatchAnalysis,
        enhancements: List[EnhancementSuggestion]
    ) -> str:
        """
        生成 Markdown 格式的分析报告
        """
        report = f"""# 简历匹配分析报告

## 基本信息

- **候选人**: {resume.name}
- **目标职位**: {resume.target_position or '未指定'}
- **总体匹配度**: {analysis.overall_score}%
- **技能匹配度**: {analysis.skill_match_score or 0}%
- **经验匹配度**: {analysis.experience_match_score or 0}%
- **学历匹配度**: {analysis.education_match_score or 0}%

---

## 匹配度分析

### ✅ 已命中技能

{chr(10).join([f'- {skill}' for skill in analysis.matched_skills])}

### ❌ 缺失技能

{chr(10).join([f'- {skill}' for skill in analysis.missing_skills])}

---

## 优势分析

{chr(10).join([f'{i+1}. {strength}' for i, strength in enumerate(analysis.strengths)])}

---

## 劣势分析

{chr(10).join([f'{i+1}. {weakness}' for i, weakness in enumerate(analysis.weaknesses)])}

---

## 简历增强建议

"""
        
        # 按优先级分组
        priority_groups = {}
        for enhancement in enhancements:
            if enhancement.priority not in priority_groups:
                priority_groups[enhancement.priority] = []
            priority_groups[enhancement.priority].append(enhancement)
        
        # 按优先级输出
        for priority in sorted(priority_groups.keys()):
            items = priority_groups[priority]
            priority_label = ["🔴 高优先级", "🟡 中优先级", "🟢 低优先级"][min(priority-1, 2)]
            
            report += f"\n### {priority_label}\n\n"
            
            for item in items:
                report += f"#### {item.title}\n\n"
                report += f"**类别**: {item.category}\n\n"
                report += f"{item.description}\n\n"
                
                if item.example:
                    report += f"**示例**: {item.example}\n\n"
                
                report += "---\n\n"
        
        report += f"""
## 总体建议

{chr(10).join([f'- {suggestion}' for suggestion in analysis.suggestions])}

---

*报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report


# 创建全局服务实例
match_service = MatchService()
