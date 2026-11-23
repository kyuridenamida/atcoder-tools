import unittest
from pathlib import Path

from atcodertools.common.language import ALL_LANGUAGES

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_updater_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "update_readme_languages",
        REPO_ROOT / "dev-tools" / "update_readme_languages.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestReadmeLanguages(unittest.TestCase):

    def test_languages_table_is_up_to_date(self):
        module = _load_updater_module()
        readme_text = (
            REPO_ROOT / "README.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            readme_text,
            module.render_readme(readme_text),
            "README.md languages table is out of date. "
            "Run `python dev-tools/update_readme_languages.py`.",
        )

    def test_table_lists_all_languages(self):
        module = _load_updater_module()
        table = module.generate_languages_table()

        for lang in ALL_LANGUAGES:
            info = module.README_LANG_INFO.get(lang.name)
            label = (
                info["label"] if info else lang.display_name
            )
            self.assertIn("|{}|".format(label), table)


if __name__ == "__main__":
    unittest.main()
