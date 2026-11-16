import os
import stat

from atcodertools.client.models.sample import Sample


def _make_text_file(file_path: str, text: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(text)


def create_code(source_code: str, file_path: str) -> None:
    _make_text_file(file_path, source_code)
    if source_code.startswith("#!"):
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)


def create_example(example: Sample, in_example_name: str, out_example_name: str) -> None:
    _make_text_file(in_example_name, example.get_input())
    _make_text_file(out_example_name, example.get_output())


def create_examples(
    examples: list[Sample],
    target_dir_path: str,
    in_example_name_format: str = "in_{}.txt",
    out_example_name_format: str = "out_{}.txt",
) -> None:
    def gen_path(file: str) -> str:
        return os.path.join(target_dir_path, file)

    for index, example in enumerate(examples):
        create_example(
            example,
            gen_path(in_example_name_format.format(index + 1)),
            gen_path(out_example_name_format.format(index + 1)),
        )
