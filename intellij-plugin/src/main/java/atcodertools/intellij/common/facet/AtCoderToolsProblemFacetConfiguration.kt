package atcodertools.intellij.common.facet

import atcodertools.intellij.common.model.AtCoderToolsProblemProperties
import com.intellij.facet.FacetConfiguration
import com.intellij.facet.ui.FacetEditorContext
import com.intellij.facet.ui.FacetValidatorsManager
import com.intellij.openapi.components.PersistentStateComponent
import com.intellij.openapi.components.State
import com.intellij.openapi.components.Storage
import com.intellij.util.xmlb.XmlSerializerUtil

/**
 * A data holder class for [AtCoderToolsProblemFacet].
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_model/facet.html">IntelliJ documentation</a>
 */
@State(
    name = "AtCoderToolsProblemFacetConfiguration",
    storages = [Storage("atcodertoolsProblemFacetConfiguration.xml")]
)
class AtCoderToolsProblemFacetConfiguration : FacetConfiguration,
    PersistentStateComponent<AtCoderToolsProblemProperties> {

    private val state = AtCoderToolsProblemProperties()

    override fun getState() = state

    override fun loadState(state: AtCoderToolsProblemProperties) {
        XmlSerializerUtil.copyBean(state, this.state)
    }

    override fun createEditorTabs(
        editorContext: FacetEditorContext?,
        validatorsManager: FacetValidatorsManager?
    ) = arrayOf(AtCoderToolsProblemFacetEditorTab(state))

}