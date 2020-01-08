#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        self.base_indent = 2
        self.insert_space_around_operators = False

        # global変数宣言時の接頭辞
        self.global_prefix = "static "

        # ループ
        self.loop_header = "for(int {loop_var} = 0 ; {loop_var} < {length} ; {loop_var}++){{"
        self.loop_footer = "}"

        # タイプ
        self.type_int = "long"
        self.type_float = "double"
        self.type_string = "String"

        # デフォルト値
        self.default_int = "0"
        self.default_float = "0.0"
        self.default_string = "\"\""

        # 宣言
        self.declare_int = "long {name};"
        self.declare_float = "double {name};"
        self.declare_string = "String {name};"
        self.declare_seq = "{type} {name}[];"
        self.declare_2d_seq = "{type} {name}[][];"

        # 確保
        self.allocate_seq = "{name} = new {type}[{length}];"
        self.allocate_2d_seq = "{name} = new {type}[{length_i}][{length_j}];"

        # 宣言と確保
        self.declare_and_allocate_seq = "{type}[] {name} = new {type}[(int)({length})];"
        self.declare_and_allocate_2d_seq = "{type}[][] {name} = new {type}[(int)({length_i})][(int)({length_j})];"

        # 入力
        self.input_int = "{name} = sc.nextLong();"
        self.input_float = "{name} = sc.nextDouble();"
        self.input_string = "{name} = sc.next();"
        self.input_seq = """for(int i = 0;i < {length};i++)
    {input}"""
        self.input_2d_seq = """for(int i = 0;i <{length_i};i++)
    for(int j = 0;j <{length_j};j++)
        {input}"""

        # 引数
        self.arg_int = "long {name}"
        self.arg_float = "double {name}"
        self.arg_string = "String {name}"
        self.arg_seq = "{type}[] {name}"
        self.arg_2d_seq = "{type}[][] {name}"

        # 配列アクセス
        self.access_1d = "{name}[i]"
        self.access_2d = "{name}[i][j]"
