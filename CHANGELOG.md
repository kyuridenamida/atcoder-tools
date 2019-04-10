# Change Log

## 1.1.4 / 2019-04-11
- [#138](https://github.com/kyuridenamida/atcoder-tools/pull/138) Fix a bug that generated main.py is not executable by making source files executable when their codes have shebang
    - Thanks for [@kmyk](https://github.com/kmyk/)'s contribution!
- [#132](https://github.com/kyuridenamida/atcoder-tools/pull/132) By default, stop showing example details on test command when getting AC but with stderr
    - Thanks for [@blue-jam](https://github.com/blue-jam/)'s contribution!
- [#131](https://github.com/kyuridenamida/atcoder-tools/pull/131) Support coloring functionality on Windows
    - Thanks for [@kotamanegi](https://github.com/kotamanegi/)'s contribution!
- [#128](https://github.com/kyuridenamida/atcoder-tools/pull/128) Show new AtCoder URL to the submission page
    - Thanks for [@kotamanegi](https://github.com/kotamanegi/)'s contribution again!

## 1.1.3 / 2019-03-06
- [#122](https://github.com/kyuridenamida/atcoder-tools/pull/122) Support pip installation on Windows (cmd.exe)
    - Thanks for [@kotamanegi](https://github.com/kotamanegi/)'s contribution!
- [#115](https://github.com/kyuridenamida/atcoder-tools/pull/115) Userscript to see generated code by atcoder-tools for archived contests
    - Thanks for [@kmyk](https://github.com/kmyk/)'s contribution!
- [#117](https://github.com/kyuridenamida/atcoder-tools/pull/117) Add tool advertisement on the default codes
    - Thanks for [@kmyk](https://github.com/kmyk/)'s contribution again!

## 1.1.2 / 2019-02-21 
- [#98](https://github.com/kyuridenamida/atcoder-tools/pull/98) Add "codegen" sub command to simply generate the input part for a specific problem without preparing other files. 
    - Thanks for [@kmyk](https://github.com/kmyk/)'s contribution!
- [#97](https://github.com/kyuridenamida/atcoder-tools/pull/97) Support Python 3
    - Thanks for [@kmyk](https://github.com/kmyk/)'s contribution again!


## 1.1.1 / 2019-02-14 
- Add an explicit disclaimer on README.md
- [#84](https://github.com/kyuridenamida/atcoder-tools/pull/84) Output stdout even when getting RE or TLE.
- [#86](https://github.com/kyuridenamida/atcoder-tools/pull/86) Support Rust
    - Thanks for [@fukatani](https://github.com/fukatani/)'s contribution and [@koba-e964](https://github.com/koba-e964/)'s code review!
- [#88](https://github.com/kyuridenamida/atcoder-tools/pull/88) Fix a bug you can't specify a code to submit by --code for submit command.
- [#92](https://github.com/kyuridenamida/atcoder-tools/pull/92) Add unit tests to check if the default templates / code generators are correct, including a bug fix of Java code generator about two-dimensional input.


## 1.1.0 / 2019-01-18 
This version includes a breaking change. Deleting --replacement parameter requires some changes in your template. See [#79](https://github.com/kyuridenamida/atcoder-tools/pull/79).
- [#80](https://github.com/kyuridenamida/atcoder-tools/pull/80) Anything configurable from command line is configurable from toml
- [#79](https://github.com/kyuridenamida/atcoder-tools/pull/79) Delete --replacement and use template for both failure and success instead 
- [#78](https://github.com/kyuridenamida/atcoder-tools/pull/78) Better default C++ template with move semantics

## 1.0.6.1 / 2019-01-13
- [#76](https://github.com/kyuridenamida/atcoder-tools/pull/76) Fix a bug the default templates are wrong. 

## 1.0.6 / 2019-01-13
- [#68](https://github.com/kyuridenamida/atcoder-tools/pull/68) Support custom code generator specification.
- [#69](https://github.com/kyuridenamida/atcoder-tools/pull/69) Support template file specification in toml.
- [#65](https://github.com/kyuridenamida/atcoder-tools/pull/65) Ignore exception while checking version.
- [#64](https://github.com/kyuridenamida/atcoder-tools/pull/64) Increase recall of input format prediction, supporting tex formula.
- [#71](https://github.com/kyuridenamida/atcoder-tools/pull/71) Minor speeding up of prediction.
- [#73](https://github.com/kyuridenamida/atcoder-tools/pull/73) Colorful messages in gen / tester / submit.
- Fix a bug that the color never goes back when you get a message saying "the latest version is available".


## 1.0.5 / 2019-01-06
- [#59](https://github.com/kyuridenamida/atcoder-tools/pull/59) Support user-defined postprocessor commands after code generation.
- [#54](https://github.com/kyuridenamida/atcoder-tools/pull/54) Support constants (MOD/YES/NO) prediction so you can use them in your template.
- [#52](https://github.com/kyuridenamida/atcoder-tools/pull/52) Support codestyle configuration.
- [#50](https://github.com/kyuridenamida/atcoder-tools/pull/50) Add version checker to notify new versions to users.
- [#49](https://github.com/kyuridenamida/atcoder-tools/pull/49) Support "atcoder-tools submit" command.

## 1.0.4 / 2018-12-30
- Fix a bug that requirements.txt is not found during package installation.
- [#44](https://github.com/kyuridenamida/atcoder-tools/pull/44) Implement more parameters for the test script (See PR for details)


## 1.0.3 / 2018-12-27
- [#41](https://github.com/kyuridenamida/atcoder-tools/pull/41) Cleaner input code generation ([Difference](https://github.com/kyuridenamida/atcoder-tools/commit/34cc603a73c3d455fe95f0fa7669f791c207f927#diff-a7157845521bbb208641f228d4f55aa9))

## 1.0.2 / 2018-12-26
- No history
