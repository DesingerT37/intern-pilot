"""
简历优化服务模块
提供基于 AI 的简历优化功能
"""
import re
from typing import List, Optional, AsyncGenerator, Dict, Any
from loguru import logger

from app.services.llm_service import llm_service
from app.models.schemas import ResumeChatMessage


class ResumeOptimizationService:
    """简历优化服务类"""
    
    # System Prompt：指导 AI 返回符合格式的响应
    SYSTEM_PROMPT = """你是一位专业的简历优化顾问，擅长帮助求职者改进简历内容。

**你的任务**：
- 根据用户的要求，对简历的特定部分提供优化建议
- 每次只优化用户指定的部分，不要重写整份简历
- 提供具体、可操作的修改建议

**响应格式要求**：
1. 首先用自然语言解释你的修改思路和理由
2. 然后将修改后的内容放在 ```markdown``` 代码块中
3. 修改后的内容必须是完整的、可直接使用的 Markdown 格式文本

**示例响应格式**：

我建议对你的项目经历进行以下优化：
1. 突出技术栈和具体成果
2. 使用量化数据展示项目影响力
3. 调整描述顺序，先写成果再写技术细节

修改后的内容如下：

```markdown
### 项目经历

#### 智能简历分析系统 (2023.06 - 2023.12)

**技术栈**：Python, FastAPI, Vue 3, PostgreSQL, OpenAI API

**项目描述**：
- 开发了一个基于 AI 的简历分析和优化平台，帮助求职者提升简历质量
- 实现了简历解析、职位匹配、批量分析等核心功能
- 使用 LLM 技术生成个性化的优化建议

**主要成果**：
- 系统上线后服务 500+ 用户，简历优化满意度达 92%
- 平均帮助用户提升 35% 的职位匹配度
- 处理简历数量超过 1000 份，生成优化建议 5000+ 条
```

**重要提示**：
- 修改后的内容必须放在 ```markdown``` 代码块中
- 代码块中的内容应该是完整的、格式正确的 Markdown 文本
- 不要在代码块外包含任何 Markdown 格式的内容
"""

    @staticmethod
    async def chat(
        resume_content: str,
        user_message: str,
        context: List[ResumeChatMessage],
        suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        AI 对话优化简历（非流式）
        
        Args:
            resume_content: 完整简历 Markdown 内容
            user_message: 用户消息
            context: 历史对话上下文（最近 5 轮）
            suggestions: 参考的优化建议列表
            
        Returns:
            包含 AI 响应和提取信息的字典
        """
        # 构建消息列表
        messages = ResumeOptimizationService._build_messages(
            resume_content, user_message, context, suggestions
        )
        
        # 调用 LLM API
        try:
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            logger.info(f"✅ AI 响应成功，长度: {len(response)} 字符")
            
            # 提取 Markdown 代码块
            modified_section = ResumeOptimizationService.extract_markdown_section(response)
            
            # 检测段落类型
            section_type = ResumeOptimizationService.detect_section_type(modified_section)
            
            # 提取修改说明
            explanation = ResumeOptimizationService.extract_explanation(response)
            
            return {
                "message": response,
                "modified_section": modified_section,
                "section_type": section_type,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"❌ AI 对话失败: {str(e)}")
            raise
    
    @staticmethod
    async def chat_stream(
        resume_content: str,
        user_message: str,
        context: List[ResumeChatMessage],
        suggestions: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        AI 对话优化简历（SSE 流式响应）
        
        Args:
            resume_content: 完整简历 Markdown 内容
            user_message: 用户消息
            context: 历史对话上下文（最近 5 轮）
            suggestions: 参考的优化建议列表
            
        Yields:
            SSE 格式的数据流
        """
        # 构建消息列表
        messages = ResumeOptimizationService._build_messages(
            resume_content, user_message, context, suggestions
        )
        
        # 调用 LLM API（流式）
        try:
            import httpx
            import json
            from app.core.config import settings
            
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": settings.OPENAI_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": True
            }
            
            logger.info(f"🤖 开始流式调用 LLM API: {settings.OPENAI_MODEL}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{settings.OPENAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    # 累积完整响应用于后续解析
                    full_response = ""
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        if line.startswith("data: "):
                            data = line[6:]  # 移除 "data: " 前缀
                            
                            if data == "[DONE]":
                                logger.info("✅ 流式响应完成")
                                
                                # 在流结束时，提取并发送元数据
                                modified_section = ResumeOptimizationService.extract_markdown_section(full_response)
                                section_type = ResumeOptimizationService.detect_section_type(modified_section)
                                explanation = ResumeOptimizationService.extract_explanation(full_response)
                                
                                # 发送元数据事件
                                metadata = {
                                    "modified_section": modified_section,
                                    "section_type": section_type,
                                    "explanation": explanation
                                }
                                yield f"data: {json.dumps({'type': 'metadata', 'data': metadata}, ensure_ascii=False)}\n\n"
                                break
                            
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        full_response += content
                                        # 发送内容块
                                        yield f"data: {json.dumps({'type': 'content', 'data': content}, ensure_ascii=False)}\n\n"
                            
                            except json.JSONDecodeError:
                                logger.warning(f"⚠️ 无法解析 JSON: {data}")
                                continue
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ LLM API 请求失败: {e.response.status_code} - {e.response.text}")
            error_msg = f"LLM API 调用失败: {e.response.text}"
            yield f"data: {json.dumps({'type': 'error', 'data': error_msg}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"❌ 流式调用异常: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)}, ensure_ascii=False)}\n\n"
    
    @staticmethod
    def extract_markdown_section(response: str) -> Optional[str]:
        """
        从 AI 响应中提取 Markdown 代码块
        
        Args:
            response: AI 响应文本
            
        Returns:
            提取的 Markdown 内容，如果没有找到返回 None
        """
        # 匹配 ```markdown ... ``` 代码块
        pattern = r'```markdown\s*\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            # 返回第一个匹配的代码块内容
            content = matches[0].strip()
            logger.info(f"✅ 提取到 Markdown 代码块，长度: {len(content)} 字符")
            return content
        
        # 尝试匹配没有语言标识的代码块 ``` ... ```
        pattern_generic = r'```\s*\n(.*?)\n```'
        matches_generic = re.findall(pattern_generic, response, re.DOTALL)
        
        if matches_generic:
            content = matches_generic[0].strip()
            logger.info(f"✅ 提取到通用代码块，长度: {len(content)} 字符")
            return content
        
        logger.warning("⚠️ 未找到 Markdown 代码块")
        return None
    
    @staticmethod
    def detect_section_type(content: Optional[str]) -> Optional[str]:
        """
        检测内容类型（education/work_experience/projects/skills）
        
        Args:
            content: Markdown 内容
            
        Returns:
            段落类型，如果无法检测返回 None
        """
        if not content:
            return None
        
        content_lower = content.lower()
        
        # 检测关键词
        if any(keyword in content_lower for keyword in ['教育经历', '教育背景', 'education', '学历', '毕业', '大学', '本科', '硕士', '博士']):
            logger.info("✅ 检测到段落类型: education")
            return "education"
        
        if any(keyword in content_lower for keyword in ['工作经历', '工作经验', 'work experience', '实习经历', '实习经验', '任职', '就职']):
            logger.info("✅ 检测到段落类型: work_experience")
            return "work_experience"
        
        if any(keyword in content_lower for keyword in ['项目经历', '项目经验', 'project', '项目名称', '项目描述', '技术栈']):
            logger.info("✅ 检测到段落类型: projects")
            return "projects"
        
        if any(keyword in content_lower for keyword in ['技能', 'skill', '专业技能', '技术能力', '掌握', '熟悉', '精通']):
            logger.info("✅ 检测到段落类型: skills")
            return "skills"
        
        logger.info("⚠️ 无法检测段落类型")
        return None
    
    @staticmethod
    def extract_explanation(response: str) -> Optional[str]:
        """
        提取修改说明（代码块之前的文本）
        
        Args:
            response: AI 响应文本
            
        Returns:
            修改说明，如果没有找到返回 None
        """
        # 查找第一个代码块的位置
        code_block_pattern = r'```'
        match = re.search(code_block_pattern, response)
        
        if match:
            # 提取代码块之前的文本
            explanation = response[:match.start()].strip()
            
            if explanation:
                logger.info(f"✅ 提取到修改说明，长度: {len(explanation)} 字符")
                return explanation
        
        # 如果没有代码块，返回整个响应作为说明
        if response.strip():
            logger.info("⚠️ 未找到代码块，返回完整响应作为说明")
            return response.strip()
        
        logger.warning("⚠️ 未找到修改说明")
        return None
    
    @staticmethod
    def _build_messages(
        resume_content: str,
        user_message: str,
        context: List[ResumeChatMessage],
        suggestions: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        构建 LLM API 的消息列表
        
        Args:
            resume_content: 完整简历 Markdown 内容
            user_message: 用户消息
            context: 历史对话上下文（最近 5 轮）
            suggestions: 参考的优化建议列表
            
        Returns:
            消息列表
        """
        messages = []
        
        # 1. System Prompt
        messages.append({
            "role": "system",
            "content": ResumeOptimizationService.SYSTEM_PROMPT
        })
        
        # 2. 简历内容（作为 user 消息）
        resume_message = f"""这是用户的完整简历内容（Markdown 格式）：

```markdown
{resume_content}
```

请基于这份简历内容，为用户提供优化建议。"""
        
        messages.append({
            "role": "user",
            "content": resume_message
        })
        
        # 3. 添加历史对话上下文（最近 5 轮，按时间顺序）
        if context:
            # 只保留最近 5 轮对话
            recent_context = context[-5:] if len(context) > 5 else context
            
            for msg in recent_context:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            logger.info(f"📝 添加了 {len(recent_context)} 轮历史对话")
        
        # 4. 如果有参考建议，添加到用户消息中
        if suggestions and len(suggestions) > 0:
            suggestions_text = "\n".join([f"- {s}" for s in suggestions])
            user_message_with_suggestions = f"""参考以下优化建议：

{suggestions_text}

{user_message}"""
            messages.append({
                "role": "user",
                "content": user_message_with_suggestions
            })
            logger.info(f"📋 添加了 {len(suggestions)} 条参考建议")
        else:
            # 5. 当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })
        
        logger.info(f"📨 构建了 {len(messages)} 条消息")
        return messages


# 创建全局服务实例
resume_optimization_service = ResumeOptimizationService()
