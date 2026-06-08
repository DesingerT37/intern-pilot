# 安装 DrissionPage

## 问题

后端日志显示：
```
未安装 DrissionPage，无法启动浏览器。请先执行 `pip install -r requirements.txt`。
```

## 解决方法

### 方法 1: 安装 DrissionPage（推荐）

在后端项目目录中安装 DrissionPage：

```bash
cd intern-pilot-api
pip install DrissionPage
```

### 方法 2: 使用爬虫项目的 requirements.txt

```bash
cd boss-job-crawler
pip install -r requirements.txt
```

### 方法 3: 手动指定版本

```bash
pip install DrissionPage>=4.0.0
```

## 验证安装

安装完成后，验证是否成功：

```bash
python -c "import DrissionPage; print(DrissionPage.__version__)"
```

应该输出类似：`4.x.x`

## 完整依赖列表

后端需要以下依赖：

```bash
# 后端 API 依赖
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib bcrypt loguru openai python-multipart

# 爬虫依赖
pip install DrissionPage beautifulsoup4 openpyxl
```

## 重启后端

安装完成后，重启后端服务：

```bash
cd intern-pilot-api
uvicorn main:app --reload
```

## 测试

安装完成后，运行测试脚本：

```bash
cd intern-pilot-api
python test_full_crawl.py
```

应该能看到浏览器窗口打开并爬取数据。
