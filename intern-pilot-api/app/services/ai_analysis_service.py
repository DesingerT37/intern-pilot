"""
AI 聚合分析服务
处理批量 JD 的聚合分析和简历优化建议生成
"""
import json
from typing import List, Dict, Any, Tuple
from collections import Counter
from loguru import logger
from openai import AsyncOpenAI

from app.models.schemas import (
    BossJobInfo, AggregatedJDAnalysis, EnhancementSuggestion,
    Resume
)
from app.core.config import settings


class AIAnalysisService:
    """AI 分析服务类"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    async def aggregate_jds(self, jobs: List[BossJobInfo], keyword: str) -> AggregatedJDAnalysis:
        """
        聚合分析多个 JD
        
        Args:
            jobs: 职位列表
            keyword: 搜索关键词
            
        Returns:
            聚合分析结果
        """
        logger.info(f"开始聚合分析 {len(jobs)} 个职位")
        
        # 1. 统计技能要求
        top_skills = self._extract_top_skills(jobs)
        
        # 2. 统计学历分布
        education_dist = self._calculate_education_distribution(jobs)
        
        # 3. 统计经验分布
        experience_dist = self._calculate_experience_distribution(jobs)
        
        # 4. 统计薪资范围
        salary_stats = self._calculate_salary_stats(jobs)
        
        # 5. 使用 LLM 提取共性要求和职责
        common_requirements, common_responsibilities = await self._extract_common_patterns(
            jobs, keyword
        )
        
        result = AggregatedJDAnalysis(
            total_jobs=len(jobs),
            top_skills=top_skills,
            education_distribution=education_dist,
            experience_distribution=experience_dist,
            salary_stats=salary_stats,
            common_requirements=common_requirements,
            common_responsibilities=common_responsibilities
        )
        
        logger.info(f"聚合分析完成: {len(top_skills)} 个技能, {len(common_requirements)} 个共性要求")
        return result
    
    def _extract_top_skills(self, jobs: List[BossJobInfo], top_n: int = 10) -> List[Tuple[str, int]]:
        """
        提取高频技能
        
        Args:
            jobs: 职位列表
            top_n: 返回前 N 个技能
            
        Returns:
            [(技能, 出现次数), ...]
        """
        # 常见技能关键词库
        skill_keywords = [
            # 编程语言
            'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'C++', 'C#', 'PHP', 'Ruby', 'Rust',
            # 前端
            'Vue', 'React', 'Angular', 'HTML', 'CSS', 'Webpack', 'Vite', 'Node.js', 'Next.js',
            # 后端框架
            'Django', 'Flask', 'FastAPI', 'Spring', 'SpringBoot', 'Express', 'Gin', 'Beego',
            # 数据库
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server',
            # 云服务
            'AWS', 'Azure', 'GCP', '阿里云', '腾讯云', 'Docker', 'Kubernetes', 'K8s',
            # 消息队列
            'Kafka', 'RabbitMQ', 'RocketMQ', 'Pulsar',
            # 大数据
            'Spark', 'Hadoop', 'Flink', 'Hive', 'HBase',
            # AI/ML
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'LangChain', 'LLM',
            # 其他
            'Git', 'Linux', 'Nginx', 'RESTful', 'GraphQL', 'gRPC', 'Microservices', '微服务',
            'CI/CD', 'Agile', '敏捷开发', 'Scrum'
        ]
        
        skill_counter = Counter()
        
        for job in jobs:
            # 从职位描述中提取技能
            text = f"{job.job_name} {job.job_description or ''} {' '.join(job.job_tags)}"
            text_lower = text.lower()
            
            for skill in skill_keywords:
                if skill.lower() in text_lower:
                    skill_counter[skill] += 1
        
        return skill_counter.most_common(top_n)
    
    def _calculate_education_distribution(self, jobs: List[BossJobInfo]) -> Dict[str, int]:
        """
        计算学历分布
        
        Args:
            jobs: 职位列表
            
        Returns:
            {"本科": 20, "硕士": 10, ...}
        """
        education_counter = Counter()
        
        for job in jobs:
            edu = job.education or "不限"
            
            # 标准化学历名称
            if "本科" in edu:
                education_counter["本科"] += 1
            elif "硕士" in edu or "研究生" in edu:
                education_counter["硕士"] += 1
            elif "博士" in edu:
                education_counter["博士"] += 1
            elif "大专" in edu or "专科" in edu:
                education_counter["大专"] += 1
            else:
                education_counter["不限"] += 1
        
        return dict(education_counter)
    
    def _calculate_experience_distribution(self, jobs: List[BossJobInfo]) -> Dict[str, int]:
        """
        计算经验分布
        
        Args:
            jobs: 职位列表
            
        Returns:
            {"应届": 5, "1-3年": 15, ...}
        """
        experience_counter = Counter()
        
        for job in jobs:
            exp = job.experience or "不限"
            
            # 标准化经验名称
            if "应届" in exp or "在校" in exp:
                experience_counter["应届"] += 1
            elif "1年" in exp or "1-3" in exp or "3年以下" in exp:
                experience_counter["1-3年"] += 1
            elif "3-5" in exp or "3年" in exp or "5年以下" in exp:
                experience_counter["3-5年"] += 1
            elif "5年" in exp or "5-10" in exp or "10年" in exp:
                experience_counter["5年以上"] += 1
            else:
                experience_counter["不限"] += 1
        
        return dict(experience_counter)
    
    def _calculate_salary_stats(self, jobs: List[BossJobInfo]) -> Dict[str, Any]:
        """
        计算薪资统计
        
        Args:
            jobs: 职位列表
            
        Returns:
            {"min": 15, "max": 30, "avg": 22, "median": 20}
        """
        salaries = []
        
        for job in jobs:
            if not job.salary_range:
                continue
            
            # 解析薪资范围，如 "15-25K"
            try:
                salary_str = job.salary_range.replace('K', '').replace('k', '').replace('·', '-')
                
                if '-' in salary_str:
                    parts = salary_str.split('-')
                    min_salary = float(parts[0].strip())
                    max_salary = float(parts[1].strip())
                    avg_salary = (min_salary + max_salary) / 2
                    salaries.append(avg_salary)
            except Exception as e:
                logger.warning(f"解析薪资失败: {job.salary_range}, error={e}")
                continue
        
        if not salaries:
            return {
                "min": 0,
                "max": 0,
                "avg": 0,
                "median": 0,
                "count": 0
            }
        
        salaries.sort()
        
        return {
            "min": round(min(salaries), 1),
            "max": round(max(salaries), 1),
            "avg": round(sum(salaries) / len(salaries), 1),
            "median": round(salaries[len(salaries) // 2], 1),
            "count": len(salaries)
        }
    
    async def _extract_common_patterns(
        self,
        jobs: List[BossJobInfo],
        keyword: str
    ) -> Tuple[List[str], List[str]]:
        """
        使用 LLM 提取共性任职要求和工作职责
        
        Args:
            jobs: 职位列表
            keyword: 搜索关键词
            
        Returns:
            (共性要求列表, 共性职责列表)
        """
        # 采样职位描述（最多取20个，避免 token 过多）
        sample_jobs = jobs[:20]
        
        jd_texts = []
        for i, job in enumerate(sample_jobs, 1):
            jd_texts.append(f"【职位{i}】{job.job_name} - {job.company_name}\n{job.job_description or '无描述'}")
        
        prompt = f"""你是一位资深的招聘数据分析师。我提供了 {len(sample_jobs)} 个"{keyword}"相关职位的 JD。

请分析并提取：
1. **共性任职要求**（Top 5）：高频出现的任职要求，如学历、技能、经验等
2. **共性工作职责**（Top 5）：高频出现的工作职责，如开发、测试、维护等

请以 JSON 格式返回：
{{
    "common_requirements": ["要求1", "要求2", ...],
    "common_responsibilities": ["职责1", "职责2", ...]
}}

JD 数据：
{chr(10).join(jd_texts[:10])}  # 只取前10个避免太长
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的招聘数据分析师，擅长从大量 JD 中提取共性模式。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return (
                result.get("common_requirements", [])[:5],
                result.get("common_responsibilities", [])[:5]
            )
        
        except Exception as e:
            logger.error(f"LLM 提取共性模式失败: {e}")
            return (
                ["提取失败，请稍后重试"],
                ["提取失败，请稍后重试"]
            )
    
    async def generate_suggestions(
        self,
        resume: Resume,
        aggregated: AggregatedJDAnalysis,
        keyword: str
    ) -> List[EnhancementSuggestion]:
        """
        生成简历优化建议
        
        Args:
            resume: 简历数据
            aggregated: 聚合分析结果
            keyword: 目标职位关键词
            
        Returns:
            优化建议列表
        """
        logger.info(f"开始生成简历优化建议: keyword={keyword}")
        
        # 构建 Prompt
        prompt = f"""你是一位专业的简历优化顾问。基于市场需求分析，为求职者提供针对性的简历优化建议。

**目标职位**：{keyword}
**分析的职位数量**：{aggregated.total_jobs}

**市场需求分析**：
- 高频技能（Top 10）：{', '.join([f"{skill}({count}次)" for skill, count in aggregated.top_skills])}
- 学历分布：{aggregated.education_distribution}
- 经验分布：{aggregated.experience_distribution}
- 薪资范围：{aggregated.salary_stats.get('min', 0)}-{aggregated.salary_stats.get('max', 0)}K（平均{aggregated.salary_stats.get('avg', 0)}K）
- 共性要求：{', '.join(aggregated.common_requirements)}
- 共性职责：{', '.join(aggregated.common_responsibilities)}

**求职者简历**：
- 姓名：{resume.name}
- 目标职位：{resume.target_position}
- 技能：{', '.join(resume.skills)}
- 教育背景：{[f"{edu.school} {edu.degree} {edu.major}" for edu in resume.education]}
- 项目经历：{len(resume.projects)} 个项目
- 工作经历：{len(resume.work_experience)} 段经历

请提供 5-8 条优化建议，按优先级排序（priority: 1-5，1 最高）。

建议类别：
- skill：技能补充（缺失的关键技能）
- project：项目优化（项目描述改进）
- experience：经验强化（工作经历优化）
- keyword：关键词优化（简历关键词调整）
- format：格式调整（简历结构优化）

请以 JSON 格式返回：
{{
    "suggestions": [
        {{
            "priority": 1,
            "category": "skill",
            "title": "补充 XXX 技能",
            "description": "详细说明为什么需要这个技能，以及如何学习",
            "example": "具体示例（可选）"
        }},
        ...
    ]
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的简历优化顾问，擅长根据市场需求提供针对性建议。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            suggestions = []
            
            for item in result.get("suggestions", []):
                suggestions.append(EnhancementSuggestion(
                    priority=item.get("priority", 3),
                    category=item.get("category", "general"),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    example=item.get("example")
                ))
            
            logger.info(f"生成了 {len(suggestions)} 条优化建议")
            return suggestions
        
        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            return [
                EnhancementSuggestion(
                    priority=1,
                    category="error",
                    title="生成建议失败",
                    description=f"抱歉，生成建议时出现错误：{str(e)}",
                    example=None
                )
            ]
    
    async def generate_markdown_report(
        self,
        keyword: str,
        aggregated: AggregatedJDAnalysis,
        suggestions: List[EnhancementSuggestion],
        match_score: float
    ) -> str:
        """
        生成 Markdown 格式的分析报告
        
        Args:
            keyword: 目标职位关键词
            aggregated: 聚合分析结果
            suggestions: 优化建议
            match_score: 匹配度评分
            
        Returns:
            Markdown 报告
        """
        report = f"""# 📊 批量职位分析报告

## 🎯 分析概览

- **目标职位**：{keyword}
- **分析职位数**：{aggregated.total_jobs} 个
- **简历匹配度**：{match_score:.1f}/100

---

## 💼 市场需求分析

### 1. 高频技能要求（Top 10）

"""
        
        for i, (skill, count) in enumerate(aggregated.top_skills, 1):
            percentage = (count / aggregated.total_jobs) * 100
            report += f"{i}. **{skill}** - 出现 {count} 次（{percentage:.1f}%）\n"
        
        report += f"""

### 2. 学历要求分布

"""
        
        for edu, count in aggregated.education_distribution.items():
            percentage = (count / aggregated.total_jobs) * 100
            report += f"- {edu}：{count} 个职位（{percentage:.1f}%）\n"
        
        report += f"""

### 3. 工作经验要求分布

"""
        
        for exp, count in aggregated.experience_distribution.items():
            percentage = (count / aggregated.total_jobs) * 100
            report += f"- {exp}：{count} 个职位（{percentage:.1f}%）\n"
        
        salary_stats = aggregated.salary_stats
        report += f"""

### 4. 薪资范围统计

- **最低薪资**：{salary_stats.get('min', 0)}K/月
- **最高薪资**：{salary_stats.get('max', 0)}K/月
- **平均薪资**：{salary_stats.get('avg', 0)}K/月
- **中位数薪资**：{salary_stats.get('median', 0)}K/月
- **有效样本数**：{salary_stats.get('count', 0)} 个

### 5. 共性任职要求

"""
        
        for i, req in enumerate(aggregated.common_requirements, 1):
            report += f"{i}. {req}\n"
        
        report += f"""

### 6. 共性工作职责

"""
        
        for i, resp in enumerate(aggregated.common_responsibilities, 1):
            report += f"{i}. {resp}\n"
        
        report += f"""

---

## 🚀 简历优化建议

"""
        
        # 按优先级分组（使用 defaultdict 避免 KeyError）
        from collections import defaultdict
        priority_groups = defaultdict(list)
        for suggestion in suggestions:
            # 将优先级限制在 1-5 范围内
            priority = max(1, min(5, suggestion.priority))
            priority_groups[priority].append(suggestion)
        
        priority_labels = {
            1: "🔴 高优先级",
            2: "🟠 较高优先级",
            3: "🟡 中等优先级",
            4: "🟢 较低优先级",
            5: "🔵 低优先级"
        }
        
        for priority in [1, 2, 3, 4, 5]:
            items = priority_groups[priority]
            if not items:
                continue
            
            report += f"\n### {priority_labels[priority]}\n\n"
            
            for suggestion in items:
                category_emoji = {
                    "skill": "💡",
                    "project": "📁",
                    "experience": "💼",
                    "keyword": "🔑",
                    "format": "📝"
                }.get(suggestion.category, "📌")
                
                report += f"#### {category_emoji} {suggestion.title}\n\n"
                report += f"{suggestion.description}\n\n"
                
                if suggestion.example:
                    report += f"**示例**：\n```\n{suggestion.example}\n```\n\n"
        
        report += f"""

---

## 📈 总结

根据对 {aggregated.total_jobs} 个"{keyword}"相关职位的分析，我们为您提供了以上优化建议。

**下一步行动**：
1. 优先完成高优先级建议
2. 补充市场需求的高频技能
3. 优化项目描述，突出相关经验
4. 调整简历关键词，提高匹配度

祝您求职顺利！🎉
"""
        
        return report


# 全局实例 - 使用延迟初始化避免导入时的环境变量问题
_ai_analysis_service_instance = None

def get_ai_analysis_service() -> AIAnalysisService:
    """获取 AI 分析服务单例"""
    global _ai_analysis_service_instance
    if _ai_analysis_service_instance is None:
        _ai_analysis_service_instance = AIAnalysisService()
    return _ai_analysis_service_instance

# 为了向后兼容，保留原来的变量名（但使用属性访问）
class _AIAnalysisServiceProxy:
    """代理类，延迟初始化真实的服务实例"""
    def __getattr__(self, name):
        return getattr(get_ai_analysis_service(), name)

ai_analysis_service = _AIAnalysisServiceProxy()
