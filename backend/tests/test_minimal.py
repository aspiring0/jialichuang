"""
最小化测试 - 逐步调试
"""
import pytest

def test_simple():
    """最简单的同步测试"""
    assert 1 + 1 == 2

@pytest.mark.asyncio
async def test_async_simple():
    """简单的异步测试"""
    import asyncio
    await asyncio.sleep(0.1)
    assert True