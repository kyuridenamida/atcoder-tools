import toml

INDENT_TYPE_SPACE = 'space'
INDENT_TYPE_TAB = 'tab'


def _verify_indent_type(indent_type: str):
    # indent_type must be 'space' or 'tab'
    assert indent_type in [INDENT_TYPE_SPACE, INDENT_TYPE_TAB]
    return indent_type


class CodeGenConfig:
    def __init__(self,
                 indent_type: str = INDENT_TYPE_SPACE,
                 indent_width: int = 4,
                 ):
        self.indent_type = _verify_indent_type(indent_type)
        self.indent_width = indent_width

    def indent(self, depth):
        if self.indent_type == INDENT_TYPE_SPACE:
            return " " * self.indent_width * depth
        return "\t" * self.indent_width * depth

    @classmethod
    def load(cls, config_file_path):
        with open(config_file_path) as f:
            kwargs = toml.load(f).get("codegen")
            return CodeGenConfig(**kwargs)
