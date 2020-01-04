package atcodertools.intellij.idea.module

import atcodertools.intellij.common.facet.findAtCoderToolsFacet
import atcodertools.intellij.common.module.AtCoderToolsModuleInitializationStep
import com.google.common.truth.Truth.assertThat
import com.intellij.ide.projectWizard.NewProjectWizardTestCase
import com.intellij.testFramework.ProjectViewTestUtil

class AtCoderToolsModuleBuilderTest : NewProjectWizardTestCase() {
    override fun setUp() {
        super.setUp()
        configureJdk()
        ProjectViewTestUtil.setupImpl(project, true)
    }

    fun testNewProjectWizard() {
        val project = createProjectFromTemplate("AtCoderTools", null) { step ->
            if (step is AtCoderToolsModuleInitializationStep) {
                step.setContestId("agc029")
            }
        }

        assertThat(project.name).isEqualTo("agc029")
        val facet = requireNotNull(project.findAtCoderToolsFacet())
        assertThat(facet.configuration.state.contestId).isEqualTo("agc029")
        assertThat(facet.configuration.state.isContentEnvGenerated).isFalse()
    }
}
