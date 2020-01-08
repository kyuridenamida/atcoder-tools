#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        self.base_indent = 1

        # global変数宣言時の接頭辞
        self.global_prefix = ""

        # ループ
        self.loop_header = "for(int {loop_var} = 0 ; {loop_var} < {length} ; {loop_var}++){{"
        self.loop_footer = "}"

        # タイプ
        self.type_int = "long long"
        self.type_float = "long double"
        self.type_string = "std::string"

        # デフォルト値
        self.default_int = "0"
        self.default_float = "0.0"
        self.default_string = "\"\""

        # 宣言
        self.declare_int = "long long {name};"
        self.declare_float = "long double {name};"
        self.declare_string = "std::string {name};"
        self.declare_seq = "std::std::vector<{type}> {name};"
        self.declare_2d_seq = "std::vector<std::vector<{type}>> {name};"

        # 確保
        self.allocate_seq = "{name}.assign({length}, {default});"
        self.allocate_2d_seq = "{name}.assign({length_i}, std::vector<{type}>({length_j}));"

        # 宣言と確保
        self.declare_and_allocate_seq = "std::vector<{type}> {name}({length});"
        self.declare_and_allocate_2d_seq = "std::vector<std::vector<{type}>> {name}({length_i}, std::vector<{type}>({length_j}));"

        # 入力
        self.input_int = "std::cin >> {name};"
        self.input_float = "std::cin >> {name};"
        self.input_string = "std::cin >> {name};"

        # 引数
        self.arg_int = "long long {name}"
        self.arg_float = "double {name}"
        self.arg_string = "std::string {name}"
        self.arg_seq = "std::vector<{type}> {name}"
        self.arg_2d_seq = "std::vector<std::vector<{type}>> {name}"

        # 引数への渡し方
        self.actual_argument_1d = "std::move({name})"
        self.actual_argument_2d = "std::move({name})"

        # 配列アクセス
        self.access_1d = "{name}[i]"
        self.access_2d = "{name}[i][j]"
