#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        self.base_indent = 2
        self.global_base_indent = 1

        # global変数宣言時の接頭辞
        self.global_prefix = ""

        # ループ
        self.loop_header = \
            "for(int {loop_var} = 0;{loop_var} < {length};{loop_var}++){{"
        self.loop_footer = "}"

        # タイプ
        self.type_int = "long"
        self.type_float = "double"
        self.type_string = "string"

        # デフォルト値
        self.default_int = "long()"
        self.default_float = "double()"
        self.default_string = "string()"

        # 宣言
        self.declare_int = "long {name};"
        self.declare_float = "double {name};"
        self.declare_string = "string {name};"
        self.declare_seq = "{type}[] {name};"
        self.declare_2d_seq = "{type}[,] {name};"

        # 確保
        self.allocate_seq = "{name} = new {type}[{length}];"
        self.allocate_2d_seq = "{name} = new {type}[{length_i},{length_j}];"

        # 宣言と確保
        self.declare_and_allocate_seq = "{type}[] " + self.allocate_seq
        self.declare_and_allocate_2d_seq = "{type}[,] " + self.allocate_2d_seq

        # 入力関数
        self.input_func_int = "cin.ReadLong;"
        self.input_func_float = "cin.ReadDouble;"
        self.input_func_string = "cin.Read;"

        # 入力
        self.input_int = "{name} = " + self.input_func_int
        self.input_float = "{name} = " + self.input_func_float
        self.input_string = "{name} = " + self.input_func_string

        # 引数
        self.arg_int = "long {name}"
        self.arg_float = "double {name}"
        self.arg_string = "string {name}"
        self.arg_seq = "{type}[] {name}"
        self.arg_2d_seq = "{type}[,] {name}"

        # 配列アクセス
        self.access_1d = "{name}[i]"
        self.access_2d = "{name}[i,j]"
