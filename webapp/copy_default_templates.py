from atcodertools.common.language import ALL_LANGUAGES
import json


def main():
    res = {}
    for lang in ALL_LANGUAGES:
        res[lang.name] = {}

        with open(lang.default_template_path, 'r') as f:
            code = f.read()
            res[lang.name]["template"] = code

        gen_py_file = "{}.py".format(lang.name)
        with open("../atcodertools/codegen/code_generators/{}".format(gen_py_file), 'r') as f:
            generator_code = f.read()
            res[lang.name]["generator"] = generator_code
            res[lang.name]["generator_url"] = "https://github.com/kyuridenamida/atcoder-tools/blob/master" \
                                              "/atcodertools/codegen/code_generators/{}".format(
                                                  gen_py_file)

    json_str = json.dumps(res, indent=1)
    print("export default {};".format(json_str))


if __name__ == "__main__":
    main()
