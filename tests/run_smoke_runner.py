import sys
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


async def run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health")
        if r.status_code != 200 or r.json() != {"status": "ok"}:
            print("health check failed", r.status_code, r.text)
            return 1

        r = await ac.post("/predict", json={"prompt": "hi"})
        if r.status_code != 200:
            print("predict returned non-200", r.status_code, r.text)
            return 2
        data = r.json()
        if data.get("input") != "hi" or "Echo:" not in data.get("output", ""):
            print("predict returned unexpected payload", data)
            return 3

    print("All smoke checks passed")
    return 0


if __name__ == '__main__':
    code = asyncio.run(run())
    sys.exit(code)
