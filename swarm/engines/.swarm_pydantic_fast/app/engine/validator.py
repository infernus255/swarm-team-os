from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.models.contracts import CONTRACTS
from app.models.state import SwarmState


class ValidationResult:
    def __init__(self, valid: bool, errors: Optional[List[str]] = None):
        self.valid = valid
        self.errors = errors or []

    def __bool__(self) -> bool:
        return self.valid


class ContractValidator:
    def validate_artifacts(self, agent_id: str, state: SwarmState) -> ValidationResult:
        contract = CONTRACTS.get(agent_id)
        if not contract:
            return ValidationResult(False, [f"No contract found for {agent_id}"])

        errors: List[str] = []
        for path_str in contract.output_paths:
            full_path = settings.result_dir / path_str
            if not full_path.exists():
                errors.append(f"Required artifact not found: {path_str}")

        if not errors:
            for path_str in contract.output_paths:
                state.artifacts[agent_id] = str(settings.result_dir / path_str)

        return ValidationResult(not bool(errors), errors)

    def validate_agent_path(self, agent_id: str, target_path: str) -> bool:
        contract = CONTRACTS.get(agent_id)
        if not contract:
            return False
        allowed_prefixes = [settings.result_dir / p for p in contract.output_paths]
        resolved = Path(target_path).resolve()
        for prefix in allowed_prefixes:
            try:
                resolved.relative_to(prefix.resolve())
                return True
            except ValueError:
                continue
        resolved_result = settings.result_dir.resolve()
        try:
            resolved.relative_to(resolved_result)
            return True
        except ValueError:
            return False


validator = ContractValidator()
