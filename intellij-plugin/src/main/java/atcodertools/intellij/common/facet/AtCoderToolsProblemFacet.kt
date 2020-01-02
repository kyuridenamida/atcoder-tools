package atcodertools.intellij.common.facet

import com.intellij.facet.Facet
import com.intellij.facet.FacetManager
import com.intellij.facet.FacetTypeId
import com.intellij.facet.FacetTypeRegistry
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.module.Module
import com.intellij.openapi.module.ModuleUtil
import com.intellij.openapi.project.Project

/**
 * A facet to associate atcoder-tools specific information to a problem sub-module.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_model/facet.html">IntelliJ documentation</a>
 */
class AtCoderToolsProblemFacet(
    module: Module,
    name: String,
    configuration: AtCoderToolsProblemFacetConfiguration
) : Facet<AtCoderToolsProblemFacetConfiguration>(getFacetType(), module, name, configuration, null) {
    companion object {
        const val NAME = "Properties"
        val ID = FacetTypeId<AtCoderToolsProblemFacet>("atcodertools-problem")

        fun getFacetType() = FacetTypeRegistry.getInstance().findFacetType(ID)
    }
}

fun Project.findSelectedAtCoderToolsProblemFacet() =
    FileEditorManager.getInstance(this).selectedFiles.map { selectedFile ->
        ModuleUtil.findModuleForFile(selectedFile, this)?.findAtCoderToolsProblemFacet(selectedFile.parent.name)
    }.firstOrNull { it != null }

fun Module.findAtCoderToolsProblemFacet(problemName: String) =
    FacetManager.getInstance(this).getFacetsByType(AtCoderToolsProblemFacet.ID).asSequence().filter { facet ->
        facet.configuration.state.problemName == problemName
    }.firstOrNull()
