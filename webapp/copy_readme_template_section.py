import re


def main():
    with open("../README.md", 'r') as f:
        readme = f.read()
    m = re.search(r"^(テンプレートエンジンの仕様については.*?)```.*$",
                  readme, flags=re.MULTILINE | re.DOTALL)
    print(m.group(1))


if __name__ == "__main__":
    main()
