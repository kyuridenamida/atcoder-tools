#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        self.base_indent = 1
        self.insert_space_around_operators = True

        # global変数宣言時の接頭辞
        self.global_prefix = ""

        # ループ
        self.loop_header = "for {loop_var} in range({length}):"
        self.loop_footer = ""

        # タイプ
        self.type_int = "int"
        self.type_float = "float"
        self.type_string = "str"

        # デフォルト値
        self.default_int = "int()"
        self.default_float = "float()"
        self.default_string = "str()"

        # 宣言
        self.declare_int = ""
        self.declare_float = ""
        self.declare_string = ""
        self.declare_seq = ""
        self.declare_2d_seq = ""

        # 確保
        self.allocate_seq = "{name} = [{default}] * ({length})"
        self.allocate_2d_seq = "{name} = [[{default}] * ({length_j}) for _ in {length_i}]"

        # 宣言と確保
        self.declare_and_allocate_seq = self.allocate_seq + \
            "  # type: \"List[{type}]\""
        self.declare_and_allocate_2d_seq = self.allocate_2d_seq + \
            "  # type: \"List[List[{type}]]\""

        # 入力関数
        self.input_func_int = "int(next(tokens))"
        self.input_func_float = "float(next(tokens))"
        self.input_func_string = "next(tokens)"

        # 入力
        self.input_int = "{name} = " + self.input_func_int
        self.input_float = "{name} = " + self.input_func_float
        self.input_string = "{name} = " + self.input_func_string

        # 宣言と入力
        self.declare_and_input_int = self.input_int + "  # type: int"
        self.declare_and_input_float = self.input_float + "  # type: float"
        self.declare_and_input_string = self.input_string + "  # type: str"

        # 確保と入力
        self.allocate_and_input_seq = "{name} = [{input_func} for _ in range({length})]"
        self.allocate_and_input_2d_seq = "{name} = [[{input_func} for _ in range({length_j})] for _ in range({length_i})]"

        # 宣言と確保と入力
        self.declare_and_allocate_and_input_seq = self.allocate_and_input_seq + \
            "  # type: \"List[{type}]\""
        self.declare_and_allocate_and_input_2d_seq = self.allocate_and_input_2d_seq + \
            "  # type: \"List[List[{type}]]\""

        # 引数
        self.arg_int = "{name}: int"
        self.arg_float = "{name}: float"
        self.arg_string = "{name}: str"
        self.arg_seq = "{name}: \"List[{type}]\""
        self.arg_2d_seq = "{name}: \"List[List[{type}]]\""

        # 配列アクセス
        self.access_1d = "{name}[i]"
        self.access_2d = "{name}[i][j]"
