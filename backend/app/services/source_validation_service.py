import ast


MAX_SOURCE_LENGTH = 50_000


class SourceValidationService:
    """Validate Python source required by the WasmBox component interface."""

    def validate(self, source_code: str) -> tuple[bool, str | None]:
        if not source_code or not source_code.strip():
            return False, "Code cannot be empty."

        if len(source_code) > MAX_SOURCE_LENGTH:
            return False, "Code exceeds the maximum allowed length."

        try:
            tree = ast.parse(source_code)
        except SyntaxError as error:
            return False, f"Syntax error: {error}"

        has_wit_world = False
        has_greet_method = False

        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or node.name != "WitWorld":
                continue

            has_wit_world = True

            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if child.name == "greet":
                        has_greet_method = True

        if not has_wit_world:
            return False, "Required class 'WitWorld' was not found."

        if not has_greet_method:
            return False, "Required method 'greet' was not found in 'WitWorld'."

        return True, None


source_validation_service = SourceValidationService()
