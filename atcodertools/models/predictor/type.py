from enum import Enum


class Type(Enum):
    int = 'int'
    float = 'float'
    str = 'str'

    def intersect(self, target_type):
        try:
            return TYPE_INTERSECTION_TABLE[self][target_type]
        except KeyError:
            raise NotImplementedError

    @classmethod
    def from_py_type(cls, py_type: type):
        if py_type == int:
            return Type.int
        elif py_type == float:
            return Type.float
        elif py_type == str:
            return Type.str
        raise NotImplementedError

    def to_py_type(self):
        if self == Type.int:
            return int
        elif self == Type.str:
            return str
        elif self == Type.float:
            return float
        raise NotImplementedError


TYPE_INTERSECTION_TABLE = {
    Type.int: {
        Type.int: Type.int,
        Type.str: Type.str,
        Type.float: Type.float,
    },
    Type.str: {
        Type.int: Type.str,
        Type.str: Type.str,
        Type.float: Type.str,
    },
    Type.float: {
        Type.int: Type.float,
        Type.str: Type.str,
        Type.float: Type.float,
    }
}
