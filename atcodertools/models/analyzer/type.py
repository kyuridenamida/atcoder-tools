from enum import Enum


class TypeIntersectionError(Exception):
    pass


class Type(Enum):
    int = 'int'
    float = 'float'
    str = 'str'

    def intersect(self, target_type):
        try:
            return TYPE_INTERSECTION_TABLE[self][target_type]
        except KeyError:
            return TypeIntersectionError

    @classmethod
    def from_py_type(cls, py_type: type):
        if py_type == int:
            return Type.int
        if py_type == float:
            return Type.float
        if py_type == str:
            return Type.str
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
