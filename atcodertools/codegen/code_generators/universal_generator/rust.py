#!/usr/bin/python3
# -*- coding: utf-8 -*-


class CodeGeneratorInfo:
    def __init__(self):
        self.base_indent = 1

        # global変数宣言時の接頭辞
        self.global_prefix = ""

        # ループ
        self.loop_header = "for {loop_var} in 0..({length}) as usize {{"
        self.loop_footer = "}"

        # タイプ
        self.type_int = "i64"
        self.type_float = "f64"
        self.type_string = "String"

        # デフォルト値
        self.default_int = "0i64"
        self.default_float = "0f64"
        self.default_string = "String::new()"

        # 宣言
        self.declare_int = "let mut {name}: i64;"
        self.declare_float = "let mut {name}: f64;"
        self.declare_string = "let mut {name}: String;"
        self.declare_seq = "let mut {name}: Vec<{type}>;"
        self.declare_2d_seq = "let mut {name}: Vec<Vec<{type}>>;"

        # 確保
        self.allocate_seq = "{name} = vec![{default}; ({length}) as usize];"
        self.allocate_2d_seq = "{name} = vec![vec![{default}; ({length_j}) as usize]; ({length_j}) as usize];"

        # 宣言と確保
        self.declare_and_allocate_seq = "let mut {name}: Vec<{type}> = vec![{default}; ({length}) as usize];"
        self.declare_and_allocate_2d_seq = "let mut {name}: Vec<Vec<{type}>> = vec![vec![{default}; ({length_j}) as usize]; ({length_i}) as usize];"

        # 入力
        self.input_int = "{name} = scanner.next();"
        self.input_float = "{name} = scanner.next();"
        self.input_string = "{name} = scanner.next();"

        # 引数
        self.arg_int = "{name}: i64"
        self.arg_float = "{name}: f64"
        self.arg_string = "{name}: String"
        self.arg_seq = "{name}: Vec<{type}>"
        self.arg_2d_seq = "{name}: Vec<Vec<{type}>>"

        # 配列アクセス
        self.access_1d = "{name}[i]"
        self.access_2d = "{name}[i][j]"

