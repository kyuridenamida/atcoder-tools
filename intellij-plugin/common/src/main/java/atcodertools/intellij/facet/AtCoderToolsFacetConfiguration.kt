package atcodertools.intellij.facet

import atcodertools.intellij.model.AtCoderToolsProperties
import com.intellij.facet.FacetConfiguration
import com.intellij.facet.ui.FacetEditorContext
import com.intellij.facet.ui.FacetValidatorsManager
import com.intellij.openapi.components.PersistentStateComponent
import com.intellij.openapi.components.State
import com.intellij.openapi.components.Storage
import com.intellij.util.xmlb.XmlSerializerUtil

/**
 * A data holder class for [AtCoderToolsFacet].
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_model/facet.html">IntelliJ documentation</a>
 */
@State(name = "AtCoderToolsFacetConfiguration", storages = [Storage("atcodertoolsFacetConfiguration.xml")])
class AtCoderToolsFacetConfiguration : FacetConfiguration, PersistentStateComponent<AtCoderToolsProperties> {

    private val state = AtCoderToolsProperties()

    override fun getState() = state

    override fun loadState(state: AtCoderToolsProperties) {
        XmlSerializerUtil.copyBean(state, this.state)
    }

    override fun createEditorTabs(
        editorContext: FacetEditorContext?,
        validatorsManager: FacetValidatorsManager?
    ) = arrayOf(AtCoderToolsFacetEditorTab(state))

}