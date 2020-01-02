package atcodertools.intellij.common.facet

import com.intellij.facet.Facet
import com.intellij.facet.FacetManager
import com.intellij.facet.FacetTypeId
import com.intellij.facet.FacetTypeRegistry
import com.intellij.openapi.module.Module
import com.intellij.openapi.module.ModuleManager
import com.intellij.openapi.project.Project

/**
 * A facet to associate atcoder-tools specific information to a module.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_model/facet.html">IntelliJ documentation</a>
 */
class AtCoderToolsFacet(
    module: Module,
    name: String,
    configuration: AtCoderToolsFacetConfiguration
) : Facet<AtCoderToolsFacetConfiguration>(getFacetType(), module, name, configuration, null) {
    companion object {
        const val NAME = "Properties"
        val ID = FacetTypeId<AtCoderToolsFacet>("atcodertools")

        fun getFacetType() = FacetTypeRegistry.getInstance().findFacetType(ID)
    }
}

fun Project.findAtCoderToolsFacet() = ModuleManager.getInstance(this).modules.map { module ->
    module.findAtCoderToolsFacet()
}.firstOrNull { it != null }

fun Module.findAtCoderToolsFacet() = FacetManager.getInstance(this).getFacetByType(AtCoderToolsFacet.ID)