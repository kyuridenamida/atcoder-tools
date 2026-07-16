import unittest
from pathlib import Path

import toml

from atcodertools.codegen.ragged_row_contract import (
    RaggedCodegenContract,
    RaggedCodegenContractNotFoundError,
)


ROOT = Path(__file__).resolve().parents[1]

BUILTIN_ROOT = (
    ROOT
    / "atcodertools"
    / "codegen"
    / "code_generators"
    / "universal_generator"
)

BUILTINS = (
    "cpp",
    "cs",
    "d",
    "go",
    "java",
    "julia",
    "nim",
    "python",
    "rust",
    "swift",
)


def load_contract(language):
    payload = toml.load(
        BUILTIN_ROOT
        / "{}.toml".format(language)
    )

    return (
        RaggedCodegenContract.from_mapping(
            payload
        )
    )


class TestRaggedRowLanguageContracts(
    unittest.TestCase
):
    def render_kwargs(self):
        return {
            "name": "a",
            "type_": "long",
            "default": "0",
            "length_i": "N",
            "length_j": "K[i]",
            "index_i": "i",
            "index_j": "j",
        }

    def test_all_ten_builtin_contracts_render(
        self,
    ):
        self.assertEqual(
            10,
            len(BUILTINS),
        )

        for language in BUILTINS:
            with self.subTest(
                language=language
            ):
                contract = load_contract(
                    language
                )

                container_type = (
                    contract
                    .render_container_type(
                        type_="long"
                    )
                )

                self.assertTrue(
                    container_type
                )

                rendered = (
                    contract
                    .render_declare(
                        **self.render_kwargs()
                    ),
                    contract
                    .render_allocate_outer(
                        **self.render_kwargs()
                    ),
                    (
                        contract
                        .render_declare_and_allocate_outer(
                            **self.render_kwargs()
                        )
                    ),
                    contract
                    .render_allocate_inner(
                        **self.render_kwargs()
                    ),
                    contract
                    .render_access(
                        **self.render_kwargs()
                    ),
                )

                for value in rendered:
                    self.assertNotIn(
                        "{type}",
                        value,
                    )

                    self.assertNotIn(
                        "{name}",
                        value,
                    )

                    self.assertNotIn(
                        "{length_i}",
                        value,
                    )

                    self.assertNotIn(
                        "{length_j}",
                        value,
                    )

    def test_csharp_uses_jagged_array(
        self,
    ):
        contract = load_contract("cs")

        self.assertEqual(
            "long[][]",
            contract.render_container_type(
                type_="long"
            ),
        )

        self.assertEqual(
            "a[i][j]",
            contract.render_access(
                **self.render_kwargs()
            ),
        )

        self.assertNotIn(
            "[,]",
            contract.render_container_type(
                type_="long"
            ),
        )

    def test_julia_uses_vector_of_vectors(
        self,
    ):
        contract = load_contract(
            "julia"
        )

        self.assertEqual(
            "Vector{Vector{long}}",
            contract.render_container_type(
                type_="long"
            ),
        )

        self.assertEqual(
            "a[i][j]",
            contract.render_access(
                **self.render_kwargs()
            ),
        )

        self.assertNotIn(
            "Matrix",
            contract.render_container_type(
                type_="long"
            ),
        )

    def test_python_and_nim_do_not_need_loop_footer(
        self,
    ):
        for language in (
            "python",
            "nim",
        ):
            with self.subTest(
                language=language
            ):
                payload = toml.load(
                    BUILTIN_ROOT
                    / "{}.toml".format(
                        language
                    )
                )

                self.assertIn(
                    "ragged",
                    payload,
                )

                self.assertEqual(
                    "",
                    payload["loop"]["footer"],
                )

                load_contract(language)

    def test_custom_contract_is_explicitly_required(
        self,
    ):
        path = (
            ROOT
            / "tests"
            / "resources"
            / "test_config"
            / "test_custom_codegen_toml"
            / "nim_custom.toml"
        )

        payload = toml.load(path)

        with self.assertRaises(
            RaggedCodegenContractNotFoundError
        ):
            (
                RaggedCodegenContract
                .from_mapping(payload)
            )


if __name__ == "__main__":
    unittest.main()
