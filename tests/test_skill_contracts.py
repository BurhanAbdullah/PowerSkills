"""Contract checks for the PowerSkills software and engineering instructions.

These tests intentionally inspect only repository-local files and declared
PowerMCP interfaces: they do not require PSCAD, vendor software, or network
access. Optional PowerMCP source checkout can be supplied through
POWER_MCP_REPO for signature conformance checks.
"""
from __future__ import annotations

import ast
import importlib.util
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_SKILLS = ROOT / "powerskills-tool" / "skills"
ENGINEERING_SKILLS = ROOT / "powerskills-engineering" / "skills"
POWER_MCP_REPO = Path(os.environ["POWER_MCP_REPO"]) if os.environ.get("POWER_MCP_REPO") else None

EXPECTED_TOOL_SKILLS = {
    "andes", "egret", "ltspice", "opendss", "pslf", "psse",
    "powerworld", "pypsa", "pandapower", "potpourri", "surge",
}
EXPECTED_ENGINEERING_SKILLS = {
    "voltage-violation-mitigation", "thermal-overload-mitigation",
    "contingency-mitigation", "dynamic-stability-mitigation",
    "operations-planning-mitigation", "convergence-failure-mitigation",
    "short-circuit-mitigation", "frequency-response-mitigation",
    "interconnection-impact-mitigation", "der-hosting-capacity-mitigation",
}
TOOL_CALL = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def skill_files(base: Path) -> list[Path]:
    return sorted(base.glob("*/SKILL.md"))


def body_without_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            return text[end + 4:]
    return text


def referenced_local_assets(skill_dir: Path, body: str) -> list[str]:
    refs = set()
    for raw in re.findall(r"`((?:scripts|references|assets|evals)/[^'`\s)]+)`", body):
        raw = raw.rstrip(".,;:")
        refs.add(raw)
    # Explicit root-level data files are local assets too.
    for raw in re.findall(r"`([A-Za-z0-9_.-]+\.(?:py|sh|yaml|yml|md|txt|json|nc|csv|dss|xlsx|sav|raw|dyr))`", body):
        refs.add(raw)
    missing = []
    for ref in sorted(refs):
        if not (skill_dir / ref).exists():
            missing.append(ref)
    return missing


def python_callables(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


def mcp_tool_signatures(repo: Path) -> set[str]:
    """Extract names actually registered as MCP tools in a local PowerMCP checkout."""
    signatures: set[str] = set()
    if not repo.exists():
        return signatures
    for source in repo.rglob("*.py"):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in source.parts):
            continue
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        functions = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # Handles mcp.tool()(load_case) and decorators mcp.tool()(fn).
            if isinstance(node.func, ast.Call) and isinstance(node.func.func, ast.Attribute) and node.func.func.attr == "tool":
                for arg in node.args:
                    if isinstance(arg, ast.Name) and arg.id in functions:
                        signatures.add(arg.id)
            # Also recognize decorator form @mcp.tool() above declarations.
            if isinstance(node.func, ast.Attribute) and node.func.attr == "tool":
                parent_func = None
                if node.args and isinstance(node.args[0], ast.Name):
                    parent_func = node.args[0].id
                if parent_func:
                    signatures.add(parent_func)
    return signatures


CONTRACT_VALIDATOR_PATH = ROOT / "skill-creator" / "scripts" / "contract_validate.py"
CONTRACT_SPEC = importlib.util.spec_from_file_location("contract_validate", CONTRACT_VALIDATOR_PATH)
assert CONTRACT_SPEC is not None and CONTRACT_SPEC.loader is not None
contract_validate = importlib.util.module_from_spec(CONTRACT_SPEC)
CONTRACT_SPEC.loader.exec_module(contract_validate)


class TestSkillRepositoryContracts(unittest.TestCase):
    def test_missing_root_level_python_asset_is_reported(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "example-skill"
            skill_dir.mkdir()
            skill = skill_dir / "SKILL.md"
            skill.write_text(
                "---\nname: example-skill\ndescription: test skill\n---\n"
                "## Preferred action order\nInspect the case first.\n"
                "## Deliver\nReport the result.\n"
                "The workflow references `missing_runtime_file.py`.\n",
                encoding="utf-8",
            )
            _, issues = contract_validate.parse_skill(skill)
            self.assertIn("missing bundled asset: missing_runtime_file.py", issues)

    def test_expected_skill_catalog_is_present(self):
        self.assertEqual({p.parent.name for p in skill_files(TOOL_SKILLS)}, EXPECTED_TOOL_SKILLS)
        self.assertEqual({p.parent.name for p in skill_files(ENGINEERING_SKILLS)}, EXPECTED_ENGINEERING_SKILLS)

    def test_every_skill_has_required_procedure_and_escalation_contract(self):
        for path in skill_files(TOOL_SKILLS):
            with self.subTest(skill=path.parent.name):
                body = body_without_frontmatter(path.read_text(encoding="utf-8")).lower()
                self.assertRegex(body, r"(?m)^#{1,3}\s+(default tool ladder|default ladder|preferred action order)")
                self.assertIn("escalation triggers", body)
                self.assertRegex(body, r"(?m)^#{1,3}\s+deliver")
                # First listed workflow step must be a base-case/load/inspect action,
                # not an advanced study such as contingencies or optimization.
                ladder = re.search(
                    r"(?is)#{1,3}\s+(?:default tool ladder|default ladder)\s*\n(.*?)(?=\n#{1,3}\s|\Z)",
                    body,
                )
                if ladder:
                    first_step = next((line.strip(" \t-*0123456789.)") for line in ladder.group(1).splitlines() if line.strip()), "")
                    self.assertNotRegex(first_step, r"contingenc|eigenvalue|time.domain|optimi[sz]e|harmonic|unit.commitment")

    def test_all_referenced_bundled_assets_exist(self):
        for path in skill_files(TOOL_SKILLS) + skill_files(ENGINEERING_SKILLS):
            with self.subTest(skill=path.parent.name):
                body = body_without_frontmatter(path.read_text(encoding="utf-8"))
                missing = referenced_local_assets(path.parent, body)
                self.assertEqual(missing, [], f"Missing local asset(s): {missing}")

    def test_tool_skill_examples_use_declared_or_bundled_command_names(self):
        # Commands are collected from the workflow headings/examples. For skills
        # backed by PowerMCP, compare against MCP-registered function names when a
        # checkout is supplied. potpourri is intentionally script/API-driven.
        signatures = mcp_tool_signatures(POWER_MCP_REPO) if POWER_MCP_REPO else set()
        for path in skill_files(TOOL_SKILLS):
            if path.parent.name == "potpourri":
                continue
            with self.subTest(skill=path.parent.name):
                body = body_without_frontmatter(path.read_text(encoding="utf-8"))
                readme = (ROOT / "README.md").read_text(encoding="utf-8")
                catalog_names = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", readme))
                command_names = set(TOOL_CALL.findall(body))
                documented = command_names & catalog_names
                self.assertTrue(documented, "No catalogued tool calls found in skill text")
                if signatures and path.parent.name in {
                    "andes", "egret", "ltspice", "opendss", "pslf", "psse", "powerworld", "pypsa", "pandapower", "surge"
                }:
                    unknown = sorted(cmd for cmd in documented if cmd not in signatures)
                    self.assertEqual(unknown, [], f"Skill references not registered by PowerMCP: {unknown}")

    def test_escalation_targets_resolve_to_engineering_skill_directories(self):
        existing = {p.parent.name for p in skill_files(ENGINEERING_SKILLS)}
        for path in skill_files(TOOL_SKILLS):
            body = body_without_frontmatter(path.read_text(encoding="utf-8"))
            for target in re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)*-mitigation)`", body):
                with self.subTest(skill=path.parent.name, target=target):
                    self.assertIn(target, existing, f"Escalation target {target!r} is not bundled")

    def test_supported_tool_skill_types_match_repository_readme_catalog(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for name in sorted(EXPECTED_TOOL_SKILLS):
            with self.subTest(skill=name):
                self.assertRegex(readme, rf"(?i)\b{re.escape(name)}\b")
        for name in sorted(EXPECTED_ENGINEERING_SKILLS):
            with self.subTest(skill=name):
                self.assertIn(name, readme)

    def test_cli_examples_reference_known_bundled_scripts(self):
        for path in skill_files(TOOL_SKILLS):
            body = body_without_frontmatter(path.read_text(encoding="utf-8"))
            for script in re.findall(r"`(scripts/[A-Za-z0-9_.-]+\.py)`", body):
                with self.subTest(skill=path.parent.name, script=script):
                    self.assertTrue((path.parent / script).is_file(), f"Missing documented script: {script}")


if __name__ == "__main__":
    unittest.main()
