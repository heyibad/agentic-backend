import subprocess
import time
import requests
import pytest

@pytest.fixture(scope="module")
def start_server():
    """Fixture to start the FastAPI server."""
    # Start the FastAPI server in a subprocess
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait for the server to start
    time.sleep(5)
    yield process
    # Terminate the server after the test
    process.terminate()
    process.wait()

def test_server_health(start_server):
    """Test to ensure the server is running and responds with HTTP 200."""
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Health check failed: {e}")

def test_server_predict(start_server):
    """Test the /predict endpoint with a sample prompt."""
    try:
        response = requests.post("http://127.0.0.1:8000/predict", json={"prompt": "hi"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["input"] == "hi"
        assert "Echo:" in data["output"]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Predict endpoint failed: {e}")
