import pytest
import os
import json
from app_result.jarvis_node_cli.core import NodeCollector

def test_system_info_keys():
    collector = NodeCollector()
    info = collector.get_system_info()
    expected_keys = ["hostname", "os", "os_version", "architecture", "processor", "python_version", "is_container"]
    for key in expected_keys:
        assert key in info

def test_collect_all_structure():
    collector = NodeCollector()
    data = collector.collect_all()
    assert "timestamp" in data
    assert "system" in data
    assert "git" in data
    assert "dependencies" in data

def test_save_to_ledger(tmp_path):
    collector = NodeCollector()
    output_file = tmp_path / "test_ledger.json"
    path = collector.save_to_ledger(str(output_file))
    
    assert os.path.exists(path)
    with open(path, "r") as f:
        data = json.load(f)
        assert "timestamp" in data
        assert data["system"]["hostname"] is not None
