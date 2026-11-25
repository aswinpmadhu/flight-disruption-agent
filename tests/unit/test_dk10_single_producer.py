"""Static enforcement of the itinerary_key roles (issue B-01a, DK10).

Three rules, applied to every ``*.py`` file under ``flight_agent/`` (``tests/`` is excluded):

1. Producer rule: a call to ``derive_itinerary_key`` may appear only in
   ``flight_agent/domain/models.py`` and ``flight_agent/services/alternatives.py``.
2. Verifier rule: inside ``models.py`` the helper may be called only from a validator method
   of class ``Itinerary``. The helper's own ``def`` is not a call.
3. No-parse rule: nothing may split, partition, slice, index or regex-match a value named
   ``itinerary_key`` or ``<expr>.itinerary_key``, a name assigned from such a value
   (``k = itinerary_key``, ``k: str = self.itinerary_key``), or ``str(...)`` of one.

Imports, comments, docstrings, string constants, annotations and non-call references never fail
rules 1 and 2. A file that does not parse fails.

Stated limits: dynamic indirection (``getattr``, ``globals()``, ``importlib``, assigning the
function to another name, ``functools.partial``) is not detected. The no-parse rule follows only
the name ``itinerary_key``, simple assignments of it and ``str(...)``; a key passed through a
function parameter or other transformation under another name is not detected. Code review covers
both.
"""

import ast
from pathlib import Path

import pytest

HELPER = "derive_itinerary_key"
KEY_NAME = "itinerary_key"
MODELS = "flight_agent/domain/models.py"
ALLOWED_PRODUCERS = {MODELS, "flight_agent/services/alternatives.py"}
VALIDATOR_DECORATORS = {"model_validator", "field_validator", "validator", "root_validator"}
PARSE_METHODS = {"split", "rsplit", "partition", "rpartition", "removeprefix", "removesuffix"}

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE = REPO_ROOT / "flight_agent"


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


class _Checker(ast.NodeVisitor):
    def __init__(self, relpath: str) -> None:
        self.relpath = relpath
        self.violations: list[str] = []
        self.helper_names: set[str] = {HELPER}
        self.re_names: set[str] = {"re"}
        self.stack: list[ast.AST] = []
        self.key_aliases: set[str] = set()

    def _is_key_expr(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id == KEY_NAME or node.id in self.key_aliases
        if isinstance(node, ast.Attribute):
            return node.attr == KEY_NAME
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "str"
            and len(node.args) == 1
        ):
            return self._is_key_expr(node.args[0])
        return False

    def _fail(self, node: ast.AST, message: str) -> None:
        self.violations.append(f"{self.relpath}:{getattr(node, 'lineno', 0)}: {message}")

    # --- alias tracking -------------------------------------------------------------------
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "re":
                self.re_names.add(alias.asname or "re")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == HELPER:
                self.helper_names.add(alias.asname or HELPER)

    # --- scope tracking -------------------------------------------------------------------
    def generic_visit(self, node: ast.AST) -> None:
        self.stack.append(node)
        super().generic_visit(node)
        self.stack.pop()

    def _in_itinerary_validator(self) -> bool:
        for i in range(len(self.stack) - 1, -1, -1):
            func = self.stack[i]
            if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not any(_decorator_name(d) in VALIDATOR_DECORATORS for d in func.decorator_list):
                    return False
                return any(
                    isinstance(parent, ast.ClassDef) and parent.name == "Itinerary"
                    for parent in self.stack[:i]
                )
        return False

    # --- rules ----------------------------------------------------------------------------
    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        is_helper_call = (isinstance(func, ast.Name) and func.id in self.helper_names) or (
            isinstance(func, ast.Attribute) and func.attr == HELPER
        )
        if is_helper_call:
            if self.relpath not in ALLOWED_PRODUCERS:
                self._fail(node, f"{HELPER} may only be called in models.py and services/alternatives.py")
            elif self.relpath == MODELS and not self._in_itinerary_validator():
                self._fail(node, f"in models.py {HELPER} may only be called from the Itinerary validator")
        if isinstance(func, ast.Attribute) and func.attr in PARSE_METHODS and self._is_key_expr(func.value):
            self._fail(node, f"{KEY_NAME} must not be parsed (.{func.attr})")
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id in self.re_names
            and any(self._is_key_expr(arg) for arg in [*node.args, *(k.value for k in node.keywords)])
        ):
            self._fail(node, f"{KEY_NAME} must not be matched with a regular expression")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._is_key_expr(node.value):
            self.key_aliases.update(t.id for t in node.targets if isinstance(t, ast.Name))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None and self._is_key_expr(node.value) and isinstance(node.target, ast.Name):
            self.key_aliases.add(node.target.id)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if self._is_key_expr(node.value):
            self._fail(node, f"{KEY_NAME} must not be indexed or sliced")
        self.generic_visit(node)


def check_source(source: str, relpath: str) -> list[str]:
    """Return the violations of the three rules for one file's source text."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"{relpath}: does not parse ({exc.msg})"]
    checker = _Checker(relpath)
    checker.visit(tree)
    return checker.violations


# ---- the real check ----------------------------------------------------------------------


def test_dk10_single_producer() -> None:
    files = sorted(PACKAGE.rglob("*.py"))
    assert files, "no source files found under flight_agent/"
    violations: list[str] = []
    for path in files:
        relpath = path.relative_to(REPO_ROOT).as_posix()
        violations += check_source(path.read_text(encoding="utf-8"), relpath)
    assert not violations, "\n".join(violations)


# ---- self-tests of the checker --------------------------------------------------------------

CALL = "from flight_agent.domain.models import derive_itinerary_key\nkey = derive_itinerary_key(segments)\n"


def test_dk10_single_producer_selftest_call_in_alternatives_passes() -> None:
    assert check_source(CALL, "flight_agent/services/alternatives.py") == []


@pytest.mark.parametrize(
    "relpath",
    [
        "flight_agent/agent/handlers_search.py",
        "flight_agent/services/rebooking.py",
        "flight_agent/approval/manager.py",
        "flight_agent/evaluation/checks.py",
    ],
)
def test_dk10_single_producer_selftest_call_elsewhere_fails(relpath: str) -> None:
    assert check_source(CALL, relpath)


def test_dk10_single_producer_selftest_aliased_call_elsewhere_fails() -> None:
    source = "from flight_agent.domain.models import derive_itinerary_key as k\nx = k(segments)\n"
    assert check_source(source, "flight_agent/services/rebooking.py")


def test_dk10_single_producer_selftest_module_attribute_call_fails() -> None:
    source = "import flight_agent.domain.models as m\nx = m.derive_itinerary_key(segments)\n"
    assert check_source(source, "flight_agent/agent/handlers_read.py")


def test_dk10_single_producer_selftest_import_without_call_passes() -> None:
    source = "from flight_agent.domain.models import derive_itinerary_key\n__all__ = ['derive_itinerary_key']\nref = derive_itinerary_key\n"
    assert check_source(source, "flight_agent/services/rebooking.py") == []


def test_dk10_single_producer_selftest_docstring_and_comment_mentions_pass() -> None:
    source = '"""Mentions derive_itinerary_key(segments) in prose."""\n# derive_itinerary_key(segments)\ntext = "derive_itinerary_key(x)"\n'
    assert check_source(source, "flight_agent/agent/handlers_read.py") == []


def test_dk10_single_producer_selftest_non_validator_call_in_models_fails() -> None:
    source = "def helper2(s):\n    return derive_itinerary_key(s)\n"
    assert check_source(source, MODELS)
    in_other_class = "class Other:\n    @model_validator(mode='after')\n    def v(self):\n        return derive_itinerary_key(self.s)\n"
    assert check_source(in_other_class, MODELS)
    undecorated = "class Itinerary:\n    def v(self):\n        return derive_itinerary_key(self.s)\n"
    assert check_source(undecorated, MODELS)


def test_dk10_single_producer_selftest_validator_call_in_models_passes() -> None:
    source = (
        "def derive_itinerary_key(segments):\n    return ''\n"
        "class Itinerary:\n"
        "    @model_validator(mode='after')\n"
        "    def _verify(self):\n"
        "        return self.itinerary_key == derive_itinerary_key(self.segments)\n"
    )
    assert check_source(source, MODELS) == []


@pytest.mark.parametrize(
    "snippet",
    [
        'parts = itinerary_key.split("+")',
        'parts = option.itinerary_key.rsplit("+", 1)',
        "first = itinerary_key[:5]",
        'a, b, c = self.itinerary_key.partition(":")',
        'rest = itinerary_key.removeprefix("MD")',
        'import re\nm = re.match(r"MD", itinerary_key)',
        'import re as regex\nm = regex.search("x", string=itinerary_key)',
        'k = itinerary_key\nparts = k.split("+")',
        'k: str = self.itinerary_key\nfirst = k[:5]',
        'parts = str(itinerary_key).split("+")',
        'a = itinerary_key\nb = a\nparts = b.partition(":")',
    ],
)
def test_dk10_single_producer_selftest_parsing_a_key_fails(snippet: str) -> None:
    assert check_source(snippet + "\n", "flight_agent/services/rebooking.py")


def test_dk10_single_producer_selftest_exact_comparison_passes() -> None:
    source = "def same(approval, itinerary_key):\n    return approval.itinerary_key == itinerary_key\n"
    assert check_source(source, "flight_agent/services/rebooking.py") == []


def test_dk10_single_producer_selftest_unparsable_file_fails() -> None:
    assert check_source("def broken(:\n", "flight_agent/services/rebooking.py")
