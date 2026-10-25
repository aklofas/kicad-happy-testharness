"""Constant scan engine: AST discovery of hardcoded constants in product sources.
The registry and its CLI live in validate/audit_constants.py."""
import ast
import hashlib
import json
from pathlib import Path

from .sources import iter_product_sources


class ConstantInfo:
    """Represents a detected constant from source analysis."""

    __slots__ = (
        "name", "file", "line", "end_line", "scope", "func", "cls",
        "const_type", "value_repr", "entry_count", "content_hash",
        "entries",
    )

    def __init__(self, *, name, file, line, end_line=None, scope="module",
                 func=None, cls=None, const_type="unknown", value_repr=None,
                 entry_count=0, content_hash=None, entries=None):
        self.name = name
        self.file = file
        self.line = line
        self.end_line = end_line or line
        self.scope = scope
        self.func = func
        self.cls = cls
        self.const_type = const_type
        self.value_repr = value_repr
        self.entry_count = entry_count
        self.content_hash = content_hash
        self.entries = entries  # dict for lookup tables

    def to_dict(self):
        d = {
            "name": self.name,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "scope": self.scope,
            "type": self.const_type,
            "entry_count": self.entry_count,
            "content_hash": self.content_hash,
        }
        if self.func:
            d["function"] = self.func
        if self.cls:
            d["class"] = self.cls
        if self.entries is not None:
            d["entries"] = self.entries
        return d


def _hash_value(obj):
    """Compute SHA-256 of a canonical JSON representation."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _node_hash(node):
    """Structural hash of a non-literal value: the AST without positions, so a line shift
    leaves it unchanged and any edit to the expression changes it (TH-065)."""
    dump = ast.dump(node, include_attributes=False)
    return "sha256:node_" + hashlib.sha256(dump.encode()).hexdigest()[:16]


def _extract_literal(node):
    """Try to extract a Python literal value from an AST node.

    Returns the value or None if the node is not a pure literal.
    """
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return None


def _node_end_line(node):
    """Get end_lineno from a node, falling back to lineno."""
    return getattr(node, "end_lineno", None) or node.lineno


def _is_upper_case_name(name):
    """Check if a name looks like a constant (UPPER_CASE or _UPPER_CASE)."""
    stripped = name.lstrip("_")
    if not stripped:
        return False
    return (stripped == stripped.upper()) and ("_" in stripped or stripped.isupper())


def _count_string_literals(node):
    """Count string literal elements in a tuple/list/set AST node."""
    count = 0
    for elt in getattr(node, "elts", []):
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            count += 1
    return count


class ConstantVisitor(ast.NodeVisitor):
    """Walk AST to find hardcoded constants."""

    def __init__(self, filename):
        self.filename = filename
        self.constants = []
        self._scope_stack = []  # list of (kind, name) tuples
        self._inline_counts = {}  # scope -> inline keyword sets seen so far

    @property
    def _current_func(self):
        for kind, name in reversed(self._scope_stack):
            if kind == "func":
                return name
        return None

    @property
    def _current_cls(self):
        for kind, name in reversed(self._scope_stack):
            if kind == "class":
                return name
        return None

    @property
    def _scope(self):
        if self._scope_stack:
            parts = []
            for kind, name in self._scope_stack:
                parts.append(name)
            return ".".join(parts)
        return "module"

    def visit_FunctionDef(self, node):
        self._scope_stack.append(("func", node.name))
        self.generic_visit(node)
        self._scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self._scope_stack.append(("class", node.name))
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_Assign(self, node):
        """Detect named constant assignments."""
        # Get the target name
        names = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.append(target.id)

        for name in names:
            self._check_assignment(name, node.value, node.lineno)

        # Continue walking into the value to find nested constructs
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Detect annotated assignments like _REGULATOR_VREF: dict[str, float] = {...}."""
        if node.value and isinstance(node.target, ast.Name):
            self._check_assignment(node.target.id, node.value, node.lineno)
        self.generic_visit(node)

    # Names that are clearly local result-builder variables, not constants.
    # Only skip these inside functions — module-level assignments still detected.
    _RESULT_BUILDER_NAMES = frozenset({
        "result", "results", "entry", "item", "record", "row",
        "output", "data", "info", "details", "response",
        "comp", "component", "circuit", "pin", "net",
        "merged", "combined",
    })

    def _check_assignment(self, name, value_node, lineno):
        """Check if an assignment looks like a constant definition."""
        # Skip generic result-builder names inside functions
        if self._current_func and name in self._RESULT_BUILDER_NAMES:
            return

        # Dict with 3+ entries
        if isinstance(value_node, ast.Dict) and len(value_node.keys) >= 3:
            literal = _extract_literal(value_node)
            entries = None
            if literal and isinstance(literal, dict):
                # For dicts with numeric values, extract entries
                if all(isinstance(v, (int, float)) for v in literal.values()):
                    entries = {str(k): {"value": v} for k, v in literal.items()}
                content_hash = _hash_value(literal)
            else:
                content_hash = _node_hash(value_node)
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="lookup_table",
                entry_count=len(value_node.keys),
                content_hash=content_hash,
                entries=entries,
            ))
            return

        # Tuple/List of 3+ string literals
        if isinstance(value_node, (ast.Tuple, ast.List)):
            str_count = _count_string_literals(value_node)
            if str_count >= 3:
                literal = _extract_literal(value_node)
                if literal:
                    content_hash = _hash_value(list(literal) if isinstance(literal, tuple) else literal)
                else:
                    content_hash = _node_hash(value_node)
                self.constants.append(ConstantInfo(
                    name=name, file=self.filename, line=lineno,
                    end_line=_node_end_line(value_node),
                    scope=self._scope, func=self._current_func, cls=self._current_cls,
                    const_type="keyword_list",
                    entry_count=len(value_node.elts),
                    content_hash=content_hash,
                ))
                return

        # List/Tuple of 3+ tuple entries (e.g., lookup tables like _CAP_ESR_TABLE)
        if isinstance(value_node, (ast.Tuple, ast.List)):
            tuple_count = sum(1 for elt in value_node.elts
                              if isinstance(elt, ast.Tuple))
            if tuple_count >= 3:
                literal = _extract_literal(value_node)
                if literal:
                    content_hash = _hash_value([list(t) if isinstance(t, tuple) else t for t in literal])
                else:
                    content_hash = _node_hash(value_node)
                self.constants.append(ConstantInfo(
                    name=name, file=self.filename, line=lineno,
                    end_line=_node_end_line(value_node),
                    scope=self._scope, func=self._current_func, cls=self._current_cls,
                    const_type="tuple_table",
                    entry_count=tuple_count,
                    content_hash=content_hash,
                ))
                return

        # Set literal or frozenset() call with 3+ string entries
        if isinstance(value_node, ast.Set) and _count_string_literals(value_node) >= 3:
            literal = _extract_literal(value_node)
            content_hash = _hash_value(sorted(literal)) if literal else _node_hash(value_node)
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="keyword_set",
                entry_count=len(value_node.elts),
                content_hash=content_hash,
            ))
            return

        # frozenset({...}) call
        if (isinstance(value_node, ast.Call)
                and isinstance(value_node.func, ast.Name)
                and value_node.func.id == "frozenset"
                and value_node.args):
            inner = value_node.args[0]
            if isinstance(inner, ast.Set) and _count_string_literals(inner) >= 3:
                literal = _extract_literal(inner)
                content_hash = _hash_value(sorted(literal)) if literal else _node_hash(value_node)
                self.constants.append(ConstantInfo(
                    name=name, file=self.filename, line=lineno,
                    end_line=_node_end_line(value_node),
                    scope=self._scope, func=self._current_func, cls=self._current_cls,
                    const_type="keyword_set",
                    entry_count=len(inner.elts),
                    content_hash=content_hash,
                ))
                return

        # Numeric constant with UPPER_CASE name
        if (isinstance(value_node, ast.Constant)
                and isinstance(value_node.value, (int, float))
                and _is_upper_case_name(name)):
            content_hash = _hash_value(value_node.value)
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="threshold",
                entry_count=1,
                content_hash=content_hash,
            ))
            return

        # re.compile() call
        if self._is_re_compile(value_node):
            pattern = self._extract_re_pattern(value_node)
            content_hash = _hash_value(pattern) if pattern else _node_hash(value_node)
            self.constants.append(ConstantInfo(
                name=name, file=self.filename, line=lineno,
                end_line=_node_end_line(value_node),
                scope=self._scope, func=self._current_func, cls=self._current_cls,
                const_type="regex_pattern",
                entry_count=1,
                content_hash=content_hash,
            ))
            return

    def visit_Call(self, node):
        """Detect inline keyword tuples in any()/all() calls."""
        if (isinstance(node.func, ast.Name)
                and node.func.id in ("any", "all")
                and node.args):
            self._check_inline_keywords(node)
        self.generic_visit(node)

    def _check_inline_keywords(self, call_node):
        """Check for any(x in val for x in ("kw1", "kw2", ...)) patterns."""
        arg = call_node.args[0]
        if not isinstance(arg, ast.GeneratorExp):
            return
        # Look for the iterable in the generator's comprehension
        for comp in arg.generators:
            iter_node = comp.iter
            if isinstance(iter_node, (ast.Tuple, ast.List)):
                str_count = _count_string_literals(iter_node)
                if str_count >= 3:
                    # Synthetic name: function plus the set's ordinal within it (a line
                    # number here renamed the constant on every shift, TH-065)
                    func = self._current_func or "module"
                    ordinal = self._inline_counts.get(self._scope, 0) + 1
                    self._inline_counts[self._scope] = ordinal
                    name = f"{func}:kw{ordinal}"
                    literal = _extract_literal(iter_node)
                    if literal:
                        content_hash = _hash_value(list(literal) if isinstance(literal, tuple) else literal)
                    else:
                        content_hash = _node_hash(iter_node)
                    self.constants.append(ConstantInfo(
                        name=name, file=self.filename, line=call_node.lineno,
                        end_line=_node_end_line(call_node),
                        scope=self._scope, func=self._current_func,
                        cls=self._current_cls,
                        const_type="inline_keywords",
                        entry_count=len(iter_node.elts),
                        content_hash=content_hash,
                    ))

    @staticmethod
    def _is_re_compile(node):
        """Check if node is a re.compile(...) call."""
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "compile":
            if isinstance(func.value, ast.Name) and func.value.id == "re":
                return True
        return False

    @staticmethod
    def _extract_re_pattern(node):
        """Extract the pattern string from re.compile(pattern)."""
        if node.args:
            first = node.args[0]
            # Handle raw strings and joined strings
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                return first.value
            if isinstance(first, ast.JoinedStr):
                return None  # f-string, can't extract statically
        return None


class ScanError(Exception):
    """A source file could not be read or parsed: the scan must not save (it would drop that
    file's registry entries and their verification evidence)."""


def scan_file(filepath, product_root=None):
    """Scan one Python file. `file` is root-relative when product_root is given."""
    try:
        source = filepath.read_bytes()
    except OSError as e:
        raise ScanError(f"could not read {filepath}: {e}") from None
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        raise ScanError(f"syntax error in {filepath}: {e}") from None
    label = (filepath.resolve().relative_to(Path(product_root).resolve()).as_posix()
             if product_root else filepath.name)
    visitor = ConstantVisitor(label)
    visitor.visit(tree)
    return visitor.constants


def iter_source_files(product_root):
    """Every *.py under skills/**/scripts/** — the shared walker's file set."""
    return iter_product_sources(product_root)


def iter_constant_records(product_root):
    """Plain-dict projection for other tools (source_scan coverage snapshot)."""
    out = []
    for info in scan_all_quiet(product_root):
        out.append({"file": info.file, "scope": info.scope, "name": info.name,
                    "line": info.line, "type": info.const_type,
                    "value": info.value_repr if info.value_repr is not None
                             else f"{info.const_type}[{info.entry_count}]"})
    return out


def scan_all_quiet(product_root):
    all_constants = []
    for fpath in iter_source_files(product_root):
        all_constants.extend(scan_file(fpath, product_root))
    return all_constants
