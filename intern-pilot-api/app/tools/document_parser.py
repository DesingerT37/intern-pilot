"""
文档解析工具
支持 PDF、Word、Markdown 格式
"""
import os
from pathlib import Path
from typing import Optional
from loguru import logger


class DocumentParser:
    """文档解析器"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        解析 PDF 文件为 Markdown
        
        优先使用 PyMuPDF4LLM（快速），失败时降级到 pdfplumber
        """
        try:
            # 方案 1: PyMuPDF4LLM (推荐)
            try:
                import pymupdf4llm
                md_text = pymupdf4llm.to_markdown(file_path)
                
                # 验证输出质量
                if len(md_text) > 100:
                    logger.info(f"✅ PyMuPDF4LLM 解析成功: {len(md_text)} 字符")
                    return md_text
            except Exception as e:
                logger.warning(f"PyMuPDF4LLM 解析失败: {e}")
            
            # 方案 2: pdfplumber (备用)
            import pdfplumber
            text_parts = []
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            md_text = "\n\n".join(text_parts)
            logger.info(f"✅ pdfplumber 解析成功: {len(md_text)} 字符")
            return md_text
            
        except Exception as e:
            logger.error(f"❌ PDF 解析失败: {str(e)}")
            raise Exception(f"PDF 解析失败: {str(e)}")
    
    @staticmethod
    def parse_word(file_path: str) -> str:
        """
        解析 Word 文件为 Markdown
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            md_text = "\n\n".join(text_parts)
            logger.info(f"✅ Word 解析成功: {len(md_text)} 字符")
            return md_text
            
        except Exception as e:
            logger.error(f"❌ Word 解析失败: {str(e)}")
            raise Exception(f"Word 解析失败: {str(e)}")
    
    @staticmethod
    def parse_markdown(file_path: str) -> str:
        """
        读取 Markdown 文件
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
            
            logger.info(f"✅ Markdown 读取成功: {len(md_text)} 字符")
            return md_text
            
        except Exception as e:
            logger.error(f"❌ Markdown 读取失败: {str(e)}")
            raise Exception(f"Markdown 读取失败: {str(e)}")
    
    @classmethod
    def parse(cls, file_path: str) -> str:
        """
        自动识别文件类型并解析
        
        Args:
            file_path: 文件路径
            
        Returns:
            Markdown 格式的文本
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return cls.parse_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return cls.parse_word(file_path)
        elif file_ext in ['.md', '.markdown']:
            return cls.parse_markdown(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")


def validate_markdown_quality(md_text: str) -> bool:
    """
    验证 Markdown 文本质量
    
    Args:
        md_text: Markdown 文本
        
    Returns:
        是否通过质量检查
    """
    # 基本长度检查
    if len(md_text) < 100:
        return False
    
    # 检查是否包含常见简历关键词
    keywords = ['教育', '经历', '项目', '技能', 'education', 'experience', 'project', 'skill']
    has_keyword = any(keyword in md_text.lower() for keyword in keywords)
    
    return has_keyword
