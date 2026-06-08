"""
爬虫服务
封装 BOSS 直聘爬虫调用
"""
import sys
import asyncio
from pathlib import Path
from typing import List, Optional
from loguru import logger

# 添加爬虫项目路径
crawler_path = Path(__file__).parent.parent.parent.parent / "boss-job-crawler"
sys.path.insert(0, str(crawler_path))

try:
    from boss_crawler.controller import CrawlerController
    from boss_crawler.config import CrawlerConfig
    from boss_crawler.models import JobInfo, CrawlResult
    CRAWLER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"爬虫模块导入失败: {e}")
    CRAWLER_AVAILABLE = False
    JobInfo = None
    CrawlResult = None


class CrawlService:
    """爬虫服务类"""
    
    def __init__(self):
        if not CRAWLER_AVAILABLE:
            raise RuntimeError("爬虫模块不可用，请检查 boss-job-crawler 是否存在")
        
        self.config = CrawlerConfig()
        self.controller = None
    
    def _init_controller(self):
        """初始化爬虫控制器"""
        if self.controller is None:
            logger.info("创建爬虫控制器...")
            self.controller = CrawlerController(config=self.config)
            logger.info("爬虫控制器创建完成")
    
    async def crawl_jobs(
        self,
        keyword: str,
        city: str = "全国",
        pages: int = 3,
        fetch_details: bool = True,
        event_handler=None
    ) -> tuple[List[JobInfo], CrawlResult]:
        """
        异步爬取职位数据
        
        Args:
            keyword: 搜索关键词
            city: 城市
            pages: 抓取页数
            fetch_details: 是否抓取职位详情
            event_handler: 可选的事件回调，用于实时进度上报
            
        Returns:
            (职位列表, 爬取结果)
        """
        logger.info(f"开始爬取职位: keyword={keyword}, city={city}, pages={pages}")
        
        # 在线程池中运行同步爬虫
        result = await asyncio.to_thread(
            self._crawl_jobs_sync,
            keyword, city, pages, fetch_details, event_handler
        )
        
        return result
    
    def _crawl_jobs_sync(
        self,
        keyword: str,
        city: str,
        pages: int,
        fetch_details: bool,
        event_handler=None
    ) -> tuple[List[JobInfo], CrawlResult]:
        """
        同步爬取职位（在线程池中运行）
        
        Returns:
            (职位列表, 爬取结果)
        """
        try:
            # 初始化控制器（会启动浏览器）
            self._init_controller()
            
            # 设置城市代码
            self.config.runtime.city_code = self._get_city_code(city)
            
            logger.info(f"开始爬取: keyword={keyword}, city={city}, pages={pages}, fetch_details={fetch_details}")
            logger.info(f"城市代码: {self.config.runtime.city_code}")
            
            # 如果有外部事件回调，临时替换控制器的 event_handler
            original_handler = self.controller.event_handler
            if event_handler:
                self.controller.event_handler = event_handler
            
            try:
                # 开始爬取（不导出 Excel）
                result = self.controller.start(
                    keyword=keyword,
                    max_pages=pages,
                    fetch_details=fetch_details,
                    export_excel=False  # API 调用模式，不导出 Excel
                )
            finally:
                # 恢复原始 event_handler
                self.controller.event_handler = original_handler
            
            if not result.success:
                logger.error(f"爬取失败: {result.error_message}")
                raise Exception(f"爬取失败: {result.error_message}")
            
            # 获取所有职位
            jobs = self.controller.storage.get_all_jobs()
            
            logger.info(f"爬取完成: 共 {len(jobs)} 个职位")
            logger.info(f"爬取结果: total_jobs={result.total_jobs}, unique_jobs={result.unique_jobs}, pages_crawled={result.pages_crawled}")
            
            return jobs, result
            
        except Exception as e:
            logger.error(f"爬取过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        finally:
            # 爬取完成后关闭浏览器，释放资源
            if self.controller and self.controller.browser:
                try:
                    logger.info("正在关闭浏览器...")
                    self.controller.browser.close()
                    logger.info("浏览器已关闭")
                except Exception as e:
                    logger.warning(f"关闭浏览器时出错: {e}")
    
    def _get_city_code(self, city: str) -> str:
        """
        获取城市代码
        
        Args:
            city: 城市名称
            
        Returns:
            城市代码
        """
        # 城市代码映射（部分常用城市）
        city_codes = {
            "全国": "100010000",
            "北京": "101010100",
            "上海": "101020100",
            "深圳": "101280600",
            "广州": "101280100",
            "杭州": "101210100",
            "成都": "101270100",
            "南京": "101190100",
            "武汉": "101200100",
            "西安": "101110100",
        }
        
        return city_codes.get(city, "100010000")  # 默认全国
    
    def check_login_status(self) -> bool:
        """
        检查登录状态
        
        Returns:
            是否已登录
        """
        self._init_controller()
        return self.controller.check_login_status()
    
    def open_login_page(self):
        """打开登录页面"""
        self._init_controller()
        self.controller.open_login_page()


# 创建全局实例
try:
    crawl_service = CrawlService()
except RuntimeError as e:
    logger.error(f"爬虫服务初始化失败: {e}")
    crawl_service = None
