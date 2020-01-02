AtCoderTools IntelliJ Plugin
====
IntelliJ Platformで動作するIDEからAtCoder Toolsを使用するためのPluginです。

`atcoder-tools`で生成したファイルを元にプロジェクトモジュールを作成し、IDEの環境を自動で整えることを目的としています。

C++ (CLion), Java (IntelliJ IDEA)に対応しています。

# Development
- To run IntelliJ IDEA with the plugin built locally, run `./gradlew runIde`.
- To run CLion with the plugin built locally, run `./gradlew runIde -Didea.atcodertools.intellij.runInCLion=true`.

## Test
- To run tests with IntelliJ IDEA, run `./gradlew check`.
- To run tests with CLion, run `./gradlew check -Didea.atcodertools.intellij.runInCLion=true`.
