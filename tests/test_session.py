import asyncio
import threading

import pytest

from qqmusic_api import Session, get_session


# 测试协程内上下文管理器的正确嵌套
@pytest.mark.asyncio
async def test_nested_context():
    session = get_session()
    async with Session() as outer_session:
        assert get_session() is outer_session

        async with Session() as inner_session:
            assert get_session() is inner_session

        assert get_session() is outer_session

    assert get_session() is session


# 测试并发协程使用独立Session实例
@pytest.mark.asyncio
async def test_concurrent_independent_sessions():
    async def use_session(session: Session):
        async with session:
            assert get_session() is session
            await asyncio.sleep(0.1)  # 模拟IO操作

    # 创建10个独立Session实例
    sessions = [Session() for _ in range(10)]
    tasks = [use_session(session) for session in sessions]
    await asyncio.gather(*tasks)


# 测试不同事件循环使用全局
def test_same_thread_different_loops():
    global_session = get_session()

    async def use_session(session):
        assert global_session == session
        await session.get("https://m.baidu.com/")

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(use_session(global_session))
    finally:
        loop.close()

    # 第二次运行,预期会抛出 RuntimeError
    with pytest.raises(RuntimeError):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(use_session(get_session()))


# 测试多线程环境下的Session隔离性
def test_thread_isolation():
    results = []

    def thread_target():
        try:
            # 在每个线程中创建新Session
            session = get_session()
            results.append({"session": session, "qimei": session.qimei if session else None})
        except Exception as e:
            results.append(e)

    # 创建5个测试线程
    threads = [threading.Thread(target=thread_target) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 验证每个线程都创建了独立的Session实例
    sessions = [r["session"] for r in results if isinstance(r, dict)]
    qimeis = [r["qimei"] for r in results if isinstance(r, dict)]
    assert len(sessions) == 5
    assert all(isinstance(s, Session) for s in sessions)
    assert len(qimeis) == 5  # 每个Session应有唯一的qimei


# 测试重复进入上下文管理器
@pytest.mark.asyncio
async def test_double_enter():
    session = Session()
    async with session:
        pass

    async with session:
        with pytest.raises(RuntimeError):
            await session.get("")
