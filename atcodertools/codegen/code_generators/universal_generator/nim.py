#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
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
        # self.allocate_int = ""
        # self.allocate_float = ""
        # self.allocate_string = ""
        self.allocate_seq = "{name} = newSeqWith({length}, {default})"
        self.allocate_2d_seq = "{name} = newSeqWith({length_i}, newSeqWith({length_j}, {default}))"

        # 入力
        self.input_int = "{name} = nextInt()"
        self.input_float = "{name} = nextFloat()"
        self.input_string = "{name} = nextString()"
        self.input_seq = """for i in 0..<{length}:
  {input}"""
        self.input_2d_seq = """for i in 0..<{length_i}:
  for j in 0..<{length_j}:
    {input}"""

        # 引数
        self.arg_int = "{name}:int"
        self.arg_float = "{name}:float"
        self.arg_string = "{name}:string"
        self.arg_seq = "{name}:seq[{type}]"
        self.arg_2d_seq = "{name}:seq[seq[{type}]]"
