#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        self.base_indent = 1

        # global変数宣言時の接頭辞
        self.global_prefix = ""

        # ループ
        self.loop_header = "foreach ({loop_var}; 0 .. cast(size_t) ({length})) {{"
        self.loop_footer = "}"

        # タイプ
        self.type_int = "long"
        self.type_float = "double"
        self.type_string = "string"

        # デフォルト値
        self.default_int = "0"
        self.default_float = "0.0"
        self.default_string = "\"\""

        # 宣言
        self.declare_int = "long {name};"
        self.declare_float = "double {name};"
        self.declare_string = "string {name};"
        self.declare_seq = "{type}[] {name};"
        self.declare_2d_seq = "{type}[][] {name};"

        # 確保
        self.allocate_seq = "{name} = new {type}[](cast(size_t) ({length}));"
        self.allocate_2d_seq = "{name} = new {type}[][](cast(size_t) ({length_i}), cast(size_t) ({length_j}));"

        # 宣言と確保
        self.declare_and_allocate_seq = "{type}[] {name} = new {type}[](cast(size_t) ({length}));"
        self.declare_and_allocate_2d_seq = \
            "{type}[][] {name} = new {type}[][](cast(size_t) ({length_i}), cast(size_t) ({length_j}));"

        # 入力
        self.input_int = "{name} = input.front.to!long;\ninput.popFront;"
        self.input_float = "{name} = input.front.to!double;\ninput.popFront;"
        self.input_string = "{name} = input.front.to!string;\ninput.popFront;"

        # 引数
        self.arg_int = "long {name}"
        self.arg_float = "double {name}"
        self.arg_string = "string {name}"
        self.arg_seq = "{type}[] {name}"
        self.arg_2d_seq = "{type}[][] {name}"

        # 配列アクセス
        self.access_1d = "{name}[i]"
        self.access_2d = "{name}[i][j]"
