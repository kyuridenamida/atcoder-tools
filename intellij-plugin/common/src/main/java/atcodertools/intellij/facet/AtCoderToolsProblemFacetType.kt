package atcodertools.intellij.facet

import atcodertools.intellij.service.AtCoderToolsApplicationService
import com.intellij.facet.Facet
import com.intellij.facet.FacetType
import com.intellij.openapi.module.Module
import com.intellij.openapi.module.ModuleType

/**
 * Represents a facet type of atcoder tools problem facet.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_model/facet.html">IntelliJ documentation</a>
 */
class AtCoderToolsProblemFacetType :
    FacetType<AtCoderToolsProblemFacet, AtCoderToolsProblemFacetConfiguration>(
        AtCoderToolsProblemFacet.ID,
        TYPE_ID,
        DISPLAY_NAME
    ) {
    companion object {
        const val TYPE_ID = "atcodertools-problem"
        const val DISPLAY_NAME = "AtCoderToolsProblem"
    }

    override fun createFacet(
        module: Module,
        name: String,
        configuration: AtCoderToolsProblemFacetConfiguration,
        underlyingFacet: Facet<*>?
    ) = AtCoderToolsProblemFacet(module, name, configuration)

    override fun createDefaultConfiguration() = AtCoderToolsProblemFacetConfiguration()

    override fun isSuitableModuleType(moduleType: ModuleType<*>?) =
        AtCoderToolsApplicationService.getInstance().isSuitableModuleType(moduleType)

    override fun isOnlyOneFacetAllowed() = false
}