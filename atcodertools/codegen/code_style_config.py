INDENT_TYPE_SPACE = 'space'
INDENT_TYPE_TAB = 'tab'


class CodeStyleConfigInitError(Exception):
    pass


class CodeStyleConfig:
    def __init__(self,
                 indent_type: str = INDENT_TYPE_SPACE,
                 indent_width: int = 4,
                 ):

        if indent_type not in [INDENT_TYPE_SPACE, INDENT_TYPE_TAB]:
            raise CodeStyleConfigInitError(
                "indent_type must be 'space' or 'tab'")

        if indent_width < 0:
            raise CodeStyleConfigInitError(
                "indent_width must be a positive integer")

        self.indent_type = indent_type
        self.indent_width = indent_width

    def indent(self, depth):
        if self.indent_type == INDENT_TYPE_SPACE:
            return " " * self.indent_width * depth
        return "\t" * self.indent_width * depth
