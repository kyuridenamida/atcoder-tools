#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        self.base_indent = 1

        # global変数宣言時の接頭辞
        self.global_prefix = ""

        # ループ
        self.loop_header = "for {loop_var} in 0..<{length}:"
        self.loop_footer = ""

        # タイプ
        self.type_int = "int"
        self.type_float = "float"
        self.type_string = "string"

        # デフォルト値
        self.default_int = "0"
        self.default_float = "0.0"
        self.default_string = "\"\""

        # 宣言
        self.declare_int = "var {name}:int"
        self.declare_float = "var {name}:float"
        self.declare_string = "var {name}:string"
        self.declare_seq = "var {name}:seq[{type}]"
        self.declare_2d_seq = "var {name}:seq[seq[{type}]]"

        # 確保
        self.allocate_seq = "{name} = newSeqWith({length}, {default})"
        self.allocate_2d_seq = "{name} = newSeqWith({length_i}, newSeqWith({length_j}, {default}))"

        # 宣言と確保
        self.declare_and_allocate_seq = "var " + self.allocate_seq
        self.declare_and_allocate_2d_seq = "var " + self.allocate_2d_seq

        # 入力関数
        self.input_func_int = "nextInt()"
        self.input_func_float = "nextFloat()"
        self.input_func_string = "nextString()"

        # 入力
        self.input_int = "{name} = " + self.input_func_int
        self.input_float = "{name} = " + self.input_func_float
        self.input_string = "{name} = " + self.input_func_string

        # 確保と入力
        self.allocate_and_input_seq = "{name} = newSeqWith({length}, {input_func})"
        self.allocate_and_input_2d_seq = "{name} = newSeqWith({length_i}, newSeqWith({length_j}, {input_func}))"

        # 宣言と確保と入力
        self.declare_and_allocate_and_input_seq = "var " + self.allocate_and_input_seq
        self.declare_and_allocate_and_input_2d_seq = "var " + self.allocate_and_input_2d_seq

        # 引数
        self.arg_int = "{name}:int"
        self.arg_float = "{name}:float"
        self.arg_string = "{name}:string"
        self.arg_seq = "{name}:seq[{type}]"
        self.arg_2d_seq = "{name}:seq[seq[{type}]]"

        # 配列アクセス
        self.access_1d = "{name}[i]"
        self.access_2d = "{name}[i][j]"
