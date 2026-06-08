"""
简历优化 API 集成测试
"""
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# 确保可导入 app 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.api.auth import get_current_user
from app.core.database import Base, SessionLocal, engine, get_db
from app.models.database import Resume, User


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def clear_export_rate_limit():
    from app.api import resume_optimization as ro

    ro._export_timestamps.clear()
    yield
    ro._export_timestamps.clear()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "testuser"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # 确保测试用户与简历存在
    user = db_session.query(User).filter(User.id == 1).first()
    if not user:
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

    resume = db_session.query(Resume).filter(Resume.resume_id == "test-resume-001").first()
    if not resume:
        resume = Resume(
            resume_id="test-resume-001",
            user_id=1,
            filename="test.pdf",
            file_size=100,
            file_type="pdf",
            name="测试用户",
            target_position="后端开发",
            markdown_text="# 测试简历\n\n## 技能\n- Python",
            parsed=True,
        )
        db_session.add(resume)
        db_session.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


class TestResumeManagement:
    def test_get_resumes(self, client):
        r = client.get("/api/resume-optimization/resumes")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert any(item["resume_id"] == "test-resume-001" for item in data)

    def test_get_resume_content(self, client):
        r = client.get("/api/resume-optimization/resumes/test-resume-001")
        assert r.status_code == 200
        assert "markdown_text" in r.json()

    def test_get_resume_not_found(self, client):
        r = client.get("/api/resume-optimization/resumes/nonexistent-id")
        assert r.status_code == 404

    def test_update_resume(self, client):
        r = client.put(
            "/api/resume-optimization/resumes/test-resume-001",
            json={"markdown_text": "# 更新后的简历"},
        )
        assert r.status_code == 200
        assert r.json()["message"]

    def test_create_version(self, client):
        r = client.post(
            "/api/resume-optimization/resumes/test-resume-001/versions",
            json={"description": "测试版本"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["version_id"]
        assert body["content"]


class TestChat:
    @patch("app.api.resume_optimization.resume_optimization_service.chat", new_callable=AsyncMock)
    def test_chat(self, mock_chat, client):
        mock_chat.return_value = {
            "message": "已优化",
            "modified_section": "### 技能\n- Python",
            "section_type": "skills",
            "explanation": "优化说明",
        }
        r = client.post(
            "/api/resume-optimization/chat",
            json={
                "resume_id": "test-resume-001",
                "resume_content": "# 简历",
                "message": "优化技能部分",
                "context": [],
            },
        )
        assert r.status_code == 200
        assert r.json()["message"] == "已优化"


class TestSuggestions:
    def test_match_suggestions_not_found(self, client):
        r = client.get("/api/resume-optimization/suggestions/match/nonexistent")
        assert r.status_code == 404

    def test_batch_suggestions_not_found(self, client):
        r = client.get("/api/resume-optimization/suggestions/batch/nonexistent")
        assert r.status_code == 404


class TestExport:
    def test_export_docx(self, client):
        r = client.post(
            "/api/resume-optimization/export/docx",
            json={
                "resume_id": "test-resume-001",
                "markdown_content": "# 导出测试\n\n- 项目A",
                "format": "docx",
                "style": "default",
            },
        )
        assert r.status_code == 200
        assert "wordprocessingml" in r.headers.get("content-type", "")

    def test_export_rate_limit(self, client):
        payload = {
            "resume_id": "test-resume-001",
            "markdown_content": "# test",
            "format": "docx",
            "style": "default",
        }
        for _ in range(5):
            client.post("/api/resume-optimization/export/docx", json=payload)
        r = client.post("/api/resume-optimization/export/docx", json=payload)
        assert r.status_code == 429
