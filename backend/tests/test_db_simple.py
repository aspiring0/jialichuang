"""
数据库测试 - 诊断fixture问题
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.database import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.mark.asyncio
async def test_db_connection():
    """测试数据库连接"""
    # 创建表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 插入并查询
    async with test_session_maker() as session:
        from app.models.session import Session
        from datetime import datetime
        
        new_session = Session(
            title="Test",
            status="active",
            created_at=datetime.utcnow()
        )
        session.add(new_session)
        await session.commit()
        
        result = await session.execute("SELECT COUNT(*) FROM sessions")
        count = result.scalar()
        assert count == 1
    
    # 清理
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)