
import ast
import hashlib
import math
from dataclasses import dataclass
from typing import Literal

import wasmtime

from .config import Settings
from .errors import CompilationError


ExpressionKind = Literal["number", "bool", "text"]


@dataclass(frozen=True, slots=True)
class CompilationArtifact:
    source_hash: str
    artifact: bytes
    artifact_sha256: str
    wat: str


class _WatBuilder:
    """Collect fixed strings and Wasm instructions without string interpolation risk."""

    def __init__(self, memory_limit_pages: int) -> None:
        self.memory_limit_pages = memory_limit_pages
        self.data_segments: list[tuple[int, bytes]] = []
        self.instructions: list[str] = []
        self.imports: set[str] = set()
        self._next_offset = 0

    def add_text(self, value: str) -> tuple[int, int]:
        raw = value.encode("utf-8")
        offset = self._next_offset
        self.data_segments.append((offset, raw))
        # Aligning offsets keeps individual host reads simple and reproducible.
        self._next_offset += len(raw) + 1
        if self._next_offset > 60_000:
            raise CompilationError(
                "static_data_too_large",
                "The plugin's literal strings exceed the sandbox data budget.",
                422,
            )
        return offset, len(raw)

    @staticmethod
    def _wat_bytes(raw: bytes) -> str:
        # Hex escapes make quotes, backslashes, and non-ASCII text unambiguous WAT data.
        return "".join(f"\\{byte:02x}" for byte in raw)

    def render(self) -> str:
        imports = {
            "input_number": '(import "wasmbox" "input_number" (func $input_number (param i32 i32) (result f64)))',
            "log": '(import "wasmbox" "log" (func $log (param i32 i32)))',
            "emit_number": '(import "wasmbox" "emit_number" (func $emit_number (param i32 f64)))',
            "emit_bool": '(import "wasmbox" "emit_bool" (func $emit_bool (param i32 i32)))',
            "emit_text": '(import "wasmbox" "emit_text" (func $emit_text (param i32 i32 i32 i32)))',
            "write_authorized_record": '(import "wasmbox" "write_authorized_record" (func $write_authorized_record (param i32 i32 i32 i32)))',
        }
        lines = ["(module"]
        lines.extend(f"  {imports[name]}" for name in sorted(self.imports))
        lines.append(f"  (memory (export \"memory\") 1 {self.memory_limit_pages})")
        for offset, raw in self.data_segments:
            lines.append(f'  (data (i32.const {offset}) "{self._wat_bytes(raw)}")')
        lines.append("  (func (export \"run\")")
        lines.extend(f"    {instruction}" for instruction in self.instructions)
        lines.append("  )")
        lines.append(")")
        return "\n".join(lines)


class SafeSubsetCompiler:
    """Validate source and compile the safe subset into a minimal Wasm module."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def compile(self, source: str) -> CompilationArtifact:
        if len(source.encode("utf-8")) > self._settings.max_source_bytes:
            raise CompilationError("source_too_large", "Plugin source exceeds the 32 KB limit.", 422)
        try:
            tree = ast.parse(source, mode="exec")
        except SyntaxError as exc:
            location = f"line {exc.lineno}" if exc.lineno else "the source"
            raise CompilationError("syntax_error", f"Python syntax error in {location}: {exc.msg}", 422) from exc

        function = self._validate_module(tree)
        self._reject_forbidden_capabilities(function)
        builder = _WatBuilder(self._settings.memory_limit_pages)
        saw_return = False
        for statement in function.body:
            if isinstance(statement, ast.Expr):
                self._compile_effect(statement.value, builder)
            elif isinstance(statement, ast.Return):
                if saw_return:
                    raise self._unsupported(statement, "Only one return statement is allowed.")
                self._compile_return(statement.value, builder)
                saw_return = True
            else:
                self._raise_forbidden_statement(statement)

        if not saw_return:
            raise CompilationError(
                "missing_return",
                "A WasmBox plugin must finish with `return { ... }`.",
                422,
            )

        wat = builder.render()
        try:
            artifact = bytes(wasmtime.wat2wasm(wat))
        except wasmtime.WasmtimeError as exc:
            # This is a compiler bug or a malformed lowering, never user-provided WAT.
            raise CompilationError("wasm_lowering_failed", "The safe-subset compiler could not create Wasm.", 500) from exc
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        return CompilationArtifact(
            source_hash=source_hash,
            artifact=artifact,
            artifact_sha256=hashlib.sha256(artifact).hexdigest(),
            wat=wat,
        )

    def _validate_module(self, tree: ast.Module) -> ast.FunctionDef:
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
            # Point out high-value dangerous constructs rather than hiding them behind a generic error.
            for statement in tree.body:
                self._raise_forbidden_statement(statement)
            raise CompilationError(
                "invalid_plugin_shape",
                "The source must contain exactly one `def transform(input):` function.",
                422,
            )
        function = tree.body[0]
        if function.name != "transform":
            raise CompilationError("invalid_entrypoint", "The plugin entry point must be `transform(input)`.", 422)
        if function.decorator_list or function.returns or getattr(function, "type_params", []):
            raise CompilationError("unsupported_function_definition", "Decorators, annotations, and generics are not allowed.", 422)
        args = function.args
        if (
            len(args.args) != 1
            or args.args[0].arg != "input"
            or args.posonlyargs
            or args.kwonlyargs
            or args.vararg
            or args.kwarg
            or args.defaults
        ):
            raise CompilationError(
                "invalid_entrypoint_signature",
                "Use exactly `def transform(input):` with no optional parameters.",
                422,
            )
        if not function.body:
            raise CompilationError("empty_plugin", "The transform function cannot be empty.", 422)
        return function

    @staticmethod
    def _reject_forbidden_capabilities(function: ast.FunctionDef) -> None:
        """Give explicit security errors even when a forbidden call is nested.

        For example, print(open("/etc/passwd").read()) should report that the
        filesystem capability is absent, rather than merely that print needs a
        literal argument.
        """

        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                if node.func.id == "open":
                    raise CompilationError(
                        "filesystem_capability_unavailable",
                        "`open` is denied because the Wasm sandbox has no filesystem capability.",
                        422,
                    )
                if node.func.id in {"eval", "exec", "compile", "__import__"}:
                    raise CompilationError(
                        "dynamic_execution_forbidden",
                        f"`{node.func.id}` is not available in WasmBox plugins.",
                        422,
                    )
                if node.func.id in {"socket", "requests", "http", "urllib"}:
                    raise CompilationError(
                        "network_capability_unavailable",
                        "Network access is unavailable: no network host function is linked into the Wasm sandbox.",
                        422,
                    )
            elif isinstance(node.func, ast.Attribute):
                current: ast.expr = node.func.value
                while isinstance(current, ast.Attribute):
                    current = current.value
                if isinstance(current, ast.Name) and current.id in {"socket", "requests", "http", "urllib"}:
                    raise CompilationError(
                        "network_capability_unavailable",
                        "Network access is unavailable: no network host function is linked into the Wasm sandbox.",
                        422,
                    )

    def _raise_forbidden_statement(self, statement: ast.stmt) -> None:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            imported = [alias.name for alias in statement.names]
            if any(name == "socket" or name.startswith("socket.") for name in imported):
                raise CompilationError(
                    "network_capability_unavailable",
                    "Network imports are unavailable: the Wasm sandbox exposes no socket or HTTP capability.",
                    422,
                )
            raise CompilationError(
                "imports_forbidden",
                "Imports are forbidden: the Wasm sandbox exposes no Python packages, filesystem, or network.",
                422,
            )
        if isinstance(statement, (ast.While, ast.For, ast.AsyncFor, ast.comprehension)):
            raise CompilationError(
                "loops_forbidden",
                "Loops are not part of the safe subset. The runtime also enforces fuel and a 50 ms deadline.",
                422,
            )
        if isinstance(statement, (ast.With, ast.AsyncWith)):
            raise CompilationError(
                "filesystem_capability_unavailable",
                "File contexts are unavailable: the Wasm sandbox has no filesystem capability.",
                422,
            )
        raise self._unsupported(statement, "Only print(...), write_authorized_record(...), and return {...} are allowed.")

    @staticmethod
    def _unsupported(node: ast.AST, message: str) -> CompilationError:
        line = getattr(node, "lineno", None)
        prefix = f"Line {line}: " if line else ""
        return CompilationError("unsupported_syntax", prefix + message, 422)

    def _compile_effect(self, expression: ast.expr, builder: _WatBuilder) -> None:
        if not isinstance(expression, ast.Call) or not isinstance(expression.func, ast.Name):
            raise self._unsupported(expression, "Only approved host-capability calls may be used as statements.")
        name = expression.func.id
        if name == "open":
            raise CompilationError(
                "filesystem_capability_unavailable",
                "`open` is denied because the Wasm sandbox has no filesystem capability.",
                422,
            )
        if name in {"eval", "exec", "compile", "__import__"}:
            raise CompilationError("dynamic_execution_forbidden", f"`{name}` is not available in WasmBox plugins.", 422)
        if name == "print":
            if len(expression.args) != 1 or expression.keywords:
                raise self._unsupported(expression, "print accepts exactly one literal value.")
            value = self._literal_string(expression.args[0])
            pointer, length = builder.add_text(value)
            builder.imports.add("log")
            builder.instructions.append(f"(call $log (i32.const {pointer}) (i32.const {length}))")
            return
        if name == "write_authorized_record":
            if len(expression.args) != 2 or expression.keywords:
                raise self._unsupported(
                    expression, "write_authorized_record accepts exactly a literal key and literal value."
                )
            key = self._literal_string(expression.args[0])
            value = self._literal_string(expression.args[1])
            if not key.replace("_", "").replace("-", "").isalnum() or len(key) > 64:
                raise CompilationError("invalid_authorized_record_key", "Record keys must be short alphanumeric names.", 422)
            key_pointer, key_length = builder.add_text(key)
            value_pointer, value_length = builder.add_text(value)
            builder.imports.add("write_authorized_record")
            builder.instructions.append(
                "(call $write_authorized_record "
                f"(i32.const {key_pointer}) (i32.const {key_length}) "
                f"(i32.const {value_pointer}) (i32.const {value_length}))"
            )
            return
        if name in {"socket", "requests", "http", "urllib"}:
            raise CompilationError(
                "network_capability_unavailable",
                "Network access is unavailable: no network host function is linked into the Wasm sandbox.",
                422,
            )
        raise self._unsupported(expression, f"`{name}` is not an approved WasmBox host capability.")

    def _compile_return(self, expression: ast.expr | None, builder: _WatBuilder) -> None:
        if not isinstance(expression, ast.Dict):
            raise self._unsupported(expression or ast.Pass(), "Return a dictionary literal, for example `return {\"total\": input[\"amount\"] * 1.18}`.")
        if len(expression.keys) != len(expression.values) or not expression.keys:
            raise CompilationError("invalid_return", "Return a non-empty dictionary with literal string keys.", 422)
        if len(expression.keys) > self._settings.max_output_fields:
            raise CompilationError("too_many_output_fields", "The result has too many fields for this sandbox.", 422)
        seen_keys: set[str] = set()
        for key_node, value_node in zip(expression.keys, expression.values, strict=True):
            if key_node is None:
                raise self._unsupported(expression, "Dictionary unpacking is not allowed.")
            key = self._literal_string(key_node)
            if key in seen_keys:
                raise CompilationError("duplicate_output_key", f"The result key `{key}` appears more than once.", 422)
            seen_keys.add(key)
            if len(key) > 64:
                raise CompilationError("output_key_too_long", "Output keys must be at most 64 characters.", 422)
            key_pointer, key_length = builder.add_text(key)
            kind = self._expression_kind(value_node)
            if kind == "number":
                builder.imports.update({"input_number", "emit_number"})
                builder.instructions.append(
                    f"(call $emit_number (i32.const {key_pointer}) {self._compile_number(value_node, builder)})"
                )
            elif kind == "bool":
                builder.imports.update({"input_number", "emit_bool"})
                builder.instructions.append(
                    f"(call $emit_bool (i32.const {key_pointer}) {self._compile_bool(value_node, builder)})"
                )
            else:
                value = self._literal_string(value_node)
                value_pointer, value_length = builder.add_text(value)
                builder.imports.add("emit_text")
                builder.instructions.append(
                    "(call $emit_text "
                    f"(i32.const {key_pointer}) (i32.const {key_length}) "
                    f"(i32.const {value_pointer}) (i32.const {value_length}))"
                )

    def _expression_kind(self, expression: ast.expr) -> ExpressionKind:
        if isinstance(expression, ast.Constant):
            if isinstance(expression.value, bool):
                return "bool"
            if isinstance(expression.value, (int, float)) and not isinstance(expression.value, bool):
                self._finite_number(expression.value, expression)
                return "number"
            if isinstance(expression.value, str):
                return "text"
        if isinstance(expression, ast.BinOp):
            self._expression_kind(expression.left)
            self._expression_kind(expression.right)
            if not isinstance(expression.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                raise self._unsupported(expression, "Only +, -, *, and / numeric operations are allowed.")
            return "number"
        if isinstance(expression, ast.UnaryOp) and isinstance(expression.op, (ast.USub, ast.UAdd)):
            self._expression_kind(expression.operand)
            return "number"
        if isinstance(expression, ast.Subscript):
            self._validate_input_access(expression)
            return "number"
        if isinstance(expression, ast.Compare):
            if len(expression.ops) != 1 or len(expression.comparators) != 1:
                raise self._unsupported(expression, "Chained comparisons are not allowed.")
            if not isinstance(expression.ops[0], (ast.Eq, ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE)):
                raise self._unsupported(expression, "Only basic numeric comparisons are allowed.")
            self._expression_kind(expression.left)
            self._expression_kind(expression.comparators[0])
            return "bool"
        if isinstance(expression, ast.UnaryOp) and isinstance(expression.op, ast.Not):
            if self._expression_kind(expression.operand) != "bool":
                raise self._unsupported(expression, "`not` can only be applied to a boolean comparison.")
            return "bool"
        if isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name) and expression.func.id == "open":
            raise CompilationError(
                "filesystem_capability_unavailable",
                "`open` is denied because the Wasm sandbox has no filesystem capability.",
                422,
            )
        raise self._unsupported(expression, "This expression is outside the numeric, boolean, or literal-text safe subset.")

    @staticmethod
    def _finite_number(value: int | float, node: ast.AST) -> None:
        if not math.isfinite(float(value)):
            raise SafeSubsetCompiler._unsupported(node, "Numbers must be finite.")

    def _validate_input_access(self, expression: ast.Subscript) -> str:
        if not isinstance(expression.value, ast.Name) or expression.value.id != "input":
            raise self._unsupported(expression, "Only input[\"numeric_field\"] may be read.")
        key_node = expression.slice
        if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
            raise self._unsupported(expression, "Input fields must use literal string keys.")
        key = key_node.value
        if not key or len(key) > 64:
            raise CompilationError("invalid_input_key", "Input field keys must be 1–64 characters.", 422)
        return key

    def _compile_number(self, expression: ast.expr, builder: _WatBuilder) -> str:
        kind = self._expression_kind(expression)
        if kind != "number":
            raise self._unsupported(expression, "A numeric expression was required here.")
        if isinstance(expression, ast.Constant):
            return f"(f64.const {float(expression.value):.17g})"
        if isinstance(expression, ast.Subscript):
            key = self._validate_input_access(expression)
            pointer, length = builder.add_text(key)
            return f"(call $input_number (i32.const {pointer}) (i32.const {length}))"
        if isinstance(expression, ast.UnaryOp):
            operand = self._compile_number(expression.operand, builder)
            return operand if isinstance(expression.op, ast.UAdd) else f"(f64.neg {operand})"
        if isinstance(expression, ast.BinOp):
            operations = {ast.Add: "f64.add", ast.Sub: "f64.sub", ast.Mult: "f64.mul", ast.Div: "f64.div"}
            operation = operations[type(expression.op)]
            return f"({operation} {self._compile_number(expression.left, builder)} {self._compile_number(expression.right, builder)})"
        raise self._unsupported(expression, "A numeric expression was required here.")

    def _compile_bool(self, expression: ast.expr, builder: _WatBuilder) -> str:
        kind = self._expression_kind(expression)
        if kind != "bool":
            raise self._unsupported(expression, "A boolean expression was required here.")
        if isinstance(expression, ast.Constant):
            return "(i32.const 1)" if expression.value else "(i32.const 0)"
        if isinstance(expression, ast.UnaryOp):
            return f"(i32.eqz {self._compile_bool(expression.operand, builder)})"
        if isinstance(expression, ast.Compare):
            operations = {
                ast.Eq: "f64.eq",
                ast.NotEq: "f64.ne",
                ast.Gt: "f64.gt",
                ast.GtE: "f64.ge",
                ast.Lt: "f64.lt",
                ast.LtE: "f64.le",
            }
            operation = operations[type(expression.ops[0])]
            return f"({operation} {self._compile_number(expression.left, builder)} {self._compile_number(expression.comparators[0], builder)})"
        raise self._unsupported(expression, "A boolean expression was required here.")

    def _literal_string(self, expression: ast.expr) -> str:
        if not isinstance(expression, ast.Constant):
            raise self._unsupported(expression, "This value must be a literal.")
        value = expression.value
        if isinstance(value, str):
            if len(value.encode("utf-8")) > 4_096:
                raise CompilationError("literal_too_large", "Literal strings are limited to 4 KB.", 422)
            return value
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            self._finite_number(value, expression)
            return str(value)
        raise self._unsupported(expression, "Only string, number, or boolean literals are allowed here.")
