"""
API Endpoint Tests
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    @pytest.mark.asyncio
    async def test_liveness(self, client: AsyncClient):
        """Test liveness endpoint"""
        response = await client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestSessionEndpoints:
    """Tests for session management endpoints"""

    @pytest.mark.asyncio
    async def test_create_session(self, client: AsyncClient):
        """Test session creation"""
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Test Session"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Session"
        assert data["status"] == "active"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_sessions(self, client: AsyncClient):
        """Test session listing"""
        # Create a session first
        await client.post("/api/v1/sessions", json={"title": "Session 1"})

        response = await client.get("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_session(self, client: AsyncClient):
        """Test getting a specific session"""
        # Create a session
        create_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Test Get"},
        )
        session_id = create_response.json()["id"]

        # Get the session
        response = await client.get(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["title"] == "Test Get"

    @pytest.mark.asyncio
    async def test_update_session(self, client: AsyncClient):
        """Test updating a session"""
        # Create a session
        create_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Original Title"},
        )
        session_id = create_response.json()["id"]

        # Update the session
        response = await client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_session(self, client: AsyncClient):
        """Test deleting a session"""
        # Create a session
        create_response = await client.post(
            "/api/v1/sessions",
            json={"title": "To Delete"},
        )
        session_id = create_response.json()["id"]

        # Delete the session
        response = await client.delete(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 204


class TestTaskEndpoints:
    """Tests for task management endpoints"""

    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient):
        """Test task creation"""
        # Create a session first
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Task Test Session"},
        )
        session_id = session_response.json()["id"]

        # Create a task
        response = await client.post(
            "/api/v1/tasks",
            json={
                "session_id": session_id,
                "type": "data_parsing",
                "priority": 5,
                "input_data": {"file_path": "test.csv"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["session_id"] == session_id
        assert data["type"] == "data_parsing"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_tasks(self, client: AsyncClient):
        """Test task listing"""
        # Create session and task
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Task List Session"},
        )
        session_id = session_response.json()["id"]

        await client.post(
            "/api/v1/tasks",
            json={
                "session_id": session_id,
                "type": "analysis",
            },
        )

        response = await client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_update_task_status(self, client: AsyncClient):
        """Test updating task status"""
        # Create session and task
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Task Update Session"},
        )
        session_id = session_response.json()["id"]

        task_response = await client.post(
            "/api/v1/tasks",
            json={
                "session_id": session_id,
                "type": "visualization",
            },
        )
        task_id = task_response.json()["id"]

        # Update task status
        response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"status": "running"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"