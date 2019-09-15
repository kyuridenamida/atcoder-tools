package atcodertools.intellij.facet

import atcodertools.intellij.module.AtCoderToolsModuleType
import com.intellij.facet.Facet
import com.intellij.facet.FacetType
import com.intellij.openapi.module.Module
import com.intellij.openapi.module.ModuleType

/**
 * Represents atcoder-tools facet type.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_model/facet.html">IntelliJ documentation</a>
 */
class AtCoderToolsFacetType :
    FacetType<AtCoderToolsFacet, AtCoderToolsFacetConfiguration>(AtCoderToolsFacet.ID, TYPE_ID, DISPLAY_NAME) {
    companion object {
        const val TYPE_ID = "atcodertools"
        const val DISPLAY_NAME = "AtCoderTools"
        val SUPPORTED_MODULE_TYPE_IDS = setOf(
            AtCoderToolsModuleType.ID,
            // CLion project enforces a single module project whose type is CPP_MODULE.
            "CPP_MODULE"
        )
    }

    override fun createFacet(
        module: Module,
        name: String,
        configuration: AtCoderToolsFacetConfiguration,
        underlyingFacet: Facet<*>?
    ) = AtCoderToolsFacet(module, name, configuration)

    override fun createDefaultConfiguration() = AtCoderToolsFacetConfiguration()

    override fun isSuitableModuleType(moduleType: ModuleType<*>?) =
        SUPPORTED_MODULE_TYPE_IDS.contains(moduleType?.id ?: "")
}