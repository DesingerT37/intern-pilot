"""
LLM 服务模块
统一管理大模型 API 调用
"""
import httpx
from typing import Optional, Dict, Any, List
from loguru import logger

from app.core.config import settings


class LLMService:
    """大模型服务类"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model = settings.OPENAI_MODEL
        self.timeout = 60.0
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        调用 LLM Chat Completion API
        
        Args:
            messages: 消息列表 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数 (0-1)
            max_tokens: 最大 token 数
            response_format: 响应格式 (如 {"type": "json_object"})
            
        Returns:
            LLM 响应文本
        """
        if not self.api_key:
            raise ValueError("LLM API Key 未配置，请在 .env 文件中设置")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        if response_format:
            payload["response_format"] = response_format
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"🤖 调用 LLM API: {self.model}")
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"✅ LLM 响应成功 (tokens: {result.get('usage', {}).get('total_tokens', 'N/A')})")
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ LLM API 请求失败: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LLM API 调用失败: {e.response.text}")
        except Exception as e:
            logger.error(f"❌ LLM 调用异常: {str(e)}")
            raise
    
    async def structured_output(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        调用 LLM 并返回结构化 JSON 输出
        
        Args:
            messages: 消息列表
            schema: JSON Schema 定义
            temperature: 温度参数
            
        Returns:
            结构化 JSON 数据
        """
        import json
        
        # 在 system prompt 中添加 JSON Schema 要求
        system_message = {
            "role": "system",
            "content": f"""你是一个专业的数据提取助手。请严格按照以下 JSON Schema 格式返回数据：

{json.dumps(schema, ensure_ascii=False, indent=2)}

只返回 JSON 数据，不要包含任何其他文本。"""
        }
        
        # 插入到消息列表开头
        full_messages = [system_message] + messages
        
        # 请求 JSON 格式响应
        response = await self.chat_completion(
            messages=full_messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失败: {response}")
            raise Exception(f"LLM 返回的不是有效的 JSON: {str(e)}")


# 创建全局 LLM 服务实例
llm_service = LLMService()
