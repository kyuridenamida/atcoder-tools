class Sample:
    def __init__(self, input_text: str, output_text: str) -> None:
        self.input_text = input_text
        self.output_text = output_text

    def get_output(self) -> str:
        return self.output_text

    def get_input(self) -> str:
        return self.input_text
