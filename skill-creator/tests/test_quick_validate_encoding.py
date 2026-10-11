from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


VALIDATOR_PATH = Path(__file__).parents[1] / "scripts" / "quick_validate.py"
SPEC = importlib.util.spec_from_file_location("quick_validate", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
quick_validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quick_validate)


def test_validate_skill_reads_utf8_independent_of_locale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skill_dir = tmp_path / "example-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: example-skill\ndescription: Café power-system workflow\n---\n",
        encoding="utf-8",
    )

    original_read_text = Path.read_text
    observed_encodings: list[str | None] = []

    def locale_sensitive_read_text(
        path: Path, encoding: str | None = None, errors: str | None = None
    ) -> str:
        observed_encodings.append(encoding)
        if encoding != "utf-8":
            raise UnicodeDecodeError("ascii", b"\\x80", 0, 1, "non-ASCII byte")
        return original_read_text(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", locale_sensitive_read_text)

    valid, message = quick_validate.validate_skill(skill_dir)

    assert valid, message
    assert observed_encodings == ["utf-8"]
