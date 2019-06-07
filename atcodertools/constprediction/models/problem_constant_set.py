from typing import NamedTuple, Optional


ProblemConstantSet = NamedTuple('ProblemConstantSet', [(
    'mod', Optional[int]), ('yes_str', Optional[str]), ('no_str', Optional[str])])

# This is a workaround; newer Python (3.6 ~) has a feature to set defaults values
ProblemConstantSet.__new__.__defaults__ = (
    None, ) * len(ProblemConstantSet._fields)
