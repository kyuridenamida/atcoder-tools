#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

from core.AtCoder import AtCoder
import core.FormatPredictor as FP


class NoPatternFoundError(Exception):
    pass


if __name__ == "__main__":
    atcoder = AtCoder()
    succ = fail = 0

    print("|問題名|結果|エラーの型|")
    print("|-:|:-:|:-|")
    for cid in atcoder.get_all_contestids():
        plist = atcoder.get_problem_list(cid)
        result_md = ""
        error = ""
        for k, v in plist.items():
            try:
                informat, samples = atcoder.get_all(v)
                result = FP.format_predictor(informat, samples)
                if result:
                    pass
                else:
                    raise NoPatternFoundError
                result_md = "○"
                error = ""
            except KeyboardInterrupt:
                sys.exit(-1)
            except Exception as e:
                # print("fail,",v)
                result_md = "×"
                error = str(type(e))[1:-1]

            print("|[%s(%s)](%s)|%s|%s|" % (cid, k, v, result_md, error))
            print("|[%s(%s)](%s)|%s|%s|" %
                  (cid, k, v, result_md, error), file=sys.stderr)
