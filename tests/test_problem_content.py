import unittest

from atcodertools.client.models.problem_content import ProblemContent


class TestProblemContent(unittest.TestCase):

    def test_samples_paired_by_example_number(self):
        # An extra 出力例 section (e.g. an explanatory alternative
        # output) must not abort sample extraction: consistent pairs
        # are still collected.
        html = """
        <html>
          <body>
            <section><h3>入力</h3><pre>N</pre></section>
            <section><h3>入力例 1</h3><pre>1</pre></section>
            <section><h3>出力例 1</h3><pre>one</pre></section>
            <section><h3>出力例 1 (別解)</h3><pre>uno</pre></section>
            <section><h3>入力例 2</h3><pre>2</pre></section>
            <section><h3>出力例 2</h3><pre>two</pre></section>
          </body>
        </html>
        """
        content = ProblemContent.from_html(html)
        samples = content.get_samples()
        self.assertEqual(2, len(samples))
        self.assertEqual("1\n", samples[0].get_input())
        self.assertEqual("one\n", samples[0].get_output())
        self.assertEqual("2\n", samples[1].get_input())
        self.assertEqual("two\n", samples[1].get_output())

    def test_first_pre_is_used_when_example_has_multiple_pres(self):
        # ABC433 E style: a 出力例 section may contain an additional
        # explanatory <pre>; the first one is the actual example.
        html = """
        <html>
          <body>
            <section><h3>入力</h3><pre>N</pre></section>
            <section><h3>入力例 1</h3><pre>1</pre></section>
            <section>
              <h3>出力例 1</h3>
              <pre>one</pre>
              <p>そのほかにも、例えば以下のような出力も正答となります。</p>
              <pre>uno</pre>
            </section>
          </body>
        </html>
        """
        content = ProblemContent.from_html(html)
        samples = content.get_samples()
        self.assertEqual(1, len(samples))
        self.assertEqual("one\n", samples[0].get_output())

    def test_input_generation_method_section_is_not_input_format(self):
        # AHC-style "入力生成方法" must not be mistaken for the
        # input-format section.
        html = """
        <html>
          <body>
            <section><h3>入力</h3><pre>N</pre></section>
            <section><h3>入力生成方法</h3><pre>ignored</pre></section>
          </body>
        </html>
        """
        content = ProblemContent.from_html(html)
        self.assertEqual("N\n", content.get_input_format())
        self.assertEqual([], content.get_samples())

    def test_combined_io_section_supplies_input_format(self):
        html = """
        <html>
          <body>
            <section><h3>問題文</h3></section>
            <section>
              <h3>入出力</h3>
              <pre>N T\nw_0 h_0</pre>
              <pre>n\np_0 r_0</pre>
            </section>
          </body>
        </html>
        """
        content = ProblemContent.from_html(html)
        self.assertEqual("N T\nw_0 h_0\n", content.get_input_format())
        self.assertEqual([], content.get_samples())

    def test_unpaired_example_sections_are_dropped(self):
        html = """
        <html>
          <body>
            <section><h3>入力</h3><pre>N</pre></section>
            <section><h3>入力例 1</h3><pre>1</pre></section>
          </body>
        </html>
        """
        content = ProblemContent.from_html(html)
        self.assertEqual("N\n", content.get_input_format())
        self.assertEqual([], content.get_samples())


if __name__ == '__main__':
    unittest.main()
