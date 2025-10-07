import asyncio
from httpx import AsyncClient
from app.main import app


def test_health():
    async def inner():
        async with AsyncClient(app=app, base_url="http://test") as ac:
            r = await ac.get("/health")
            assert r.status_code == 200
            assert r.json() == {"status": "ok"}

    asyncio.run(inner())


def test_predict():
    async def inner():
        async with AsyncClient(app=app, base_url="http://test") as ac:
            r = await ac.post("/predict", json={"prompt": "hi"})
            assert r.status_code == 200
            data = r.json()
            assert data["input"] == "hi"
            assert "Echo:" in data["output"]

    asyncio.run(inner())
