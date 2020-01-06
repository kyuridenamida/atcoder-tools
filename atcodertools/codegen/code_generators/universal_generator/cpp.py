#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        # タイプ
        self.type_int = "int"
        self.type_float = "double"
        self.type_string = "string"

        # デフォルト値
        self.default_int = "0"
        self.default_float = "0.0"
        self.default_string = "\"\""

        # 宣言
        self.declare_int = "int {name};"
        self.declare_float = "double {name};"
        self.declare_string = "string {name};"
        self.declare_seq = "vector<{type}> {name};"
        self.declare_2d_seq = "vector<vector<{type}>> {name};"

        # 確保
        # self.allocate_int = ""
        # self.allocate_float = ""
        # self.allocate_string = ""
        self.allocate_seq = "{name}.assign({length}, {default});"
        self.allocate_2d_seq = "{name}.assign({length_i}, vector<{type}>({length_j}, {default}));"

        # 入力
        self.input_int = "cin >> {name};"
        self.input_float = "cin >> {name};"
        self.input_string = "cin >> {name};"
        self.input_seq = """for(int i = 0;i < {length};i++)
            {input}"""
        self.input_2d_seq = """for(int i = 0;i <{length_i};i++)
            for(int j = 0;j <{length_j};j++)
                {input}"""

        # 引数
        self.arg_int = "int {name}"
        self.arg_float = "float {name}"
        self.arg_string = "string {name}"
        self.arg_seq = "vector<{type}> {name}"
        self.arg_2d_seq = "vector<vector<{type}> > {name}"
