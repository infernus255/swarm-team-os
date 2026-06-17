import pytest
from memory.sga_client import sga_client

def test_sga_push_and_query():
    """Verify that the SGA client can successfully push to Neon DB and query via vector similarity."""
    print("[TEST] Testing SGA push_memory...")
    project_id = "INTEGRATION_TEST"
    phase = "VERIFICATION"
    content = "This is a direct verification memory for testing Neon DB integration and HNSW vector similarity search."
    
    # Push memory
    success = sga_client.push_memory(
        project_id=project_id,
        phase=phase,
        content=content,
        metadata={"test": True, "runner": "pytest"}
    )
    assert success, "Failed to push memory to Neon DB"

    print("[TEST] Testing SGA query_global_memory...")
    # Query memory
    query_text = "Neon DB integration"
    results = sga_client.query_global_memory(query=query_text, limit=1)
    
    assert results != "No global memory context available.", "SGA query returned no context"
    assert "direct verification memory" in results.lower(), f"Expected query result to contain test content, but got: {results}"
    print("[TEST] SGA push and query verification succeeded!")
