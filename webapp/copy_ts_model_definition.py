import json


def main():
    with open("./src/models/QualityResult.ts", 'r') as f:
        res = f.read()
        res = res[res.find("interface"):]

    json_str = json.dumps(res, indent=1)
    print("export default {};".format(json_str))


if __name__ == "__main__":
    main()
