import pytest
from core.models import Phase, Status
from core.orchestrator import GraphRunner
from pathlib import Path
import shutil

@pytest.fixture
def clean_workspace():
    # Setup: ensure app_result is clean
    if Path("app_result").exists():
        shutil.rmtree("app_result")
    yield
    # Teardown: could clean up here too

@pytest.mark.asyncio
async def test_greenfield_flow(clean_workspace):
    runner = GraphRunner()
    prompt = "Test app for Jarvis"
    state = await runner.run(prompt)
    
    # Assertions
    assert state["status"] == Status.DONE
    assert state["currentNode"] == "M6"
    assert Path("app_result/PROJECT_MANIFEST.md").exists()
    assert Path("app_result/src/main.py").exists()
    assert Path("app_result/deploy/Dockerfile").exists()
    assert "manifest" in state["artifacts"]
    assert "source" in state["artifacts"]

def test_state_init():
    runner = GraphRunner()
    state = runner.state
    assert state["current_phase"] == Phase.M0_FOUNDATION
    assert state["status"] == Status.PENDING
    assert state["workflow_mode"] == "greenfield"
