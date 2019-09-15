package atcodertools.intellij.module

import atcodertools.intellij.command.executeGenCommand
import atcodertools.intellij.facet.AtCoderToolsFacet
import atcodertools.intellij.facet.findAtCoderToolsFacet
import atcodertools.intellij.toolwindow.findAtCoderToolsToolWindow
import com.intellij.facet.FacetManager
import com.intellij.ide.util.projectWizard.ModuleBuilder
import com.intellij.ide.util.projectWizard.ModuleBuilderListener
import com.intellij.ide.util.projectWizard.ModuleWizardStep
import com.intellij.ide.util.projectWizard.WizardContext
import com.intellij.openapi.application.runWriteAction
import com.intellij.openapi.module.Module
import com.intellij.openapi.options.ConfigurationException
import com.intellij.openapi.project.Project
import com.intellij.openapi.roots.ModifiableRootModel
import com.intellij.openapi.roots.ui.configuration.ModulesProvider
import com.intellij.project.stateStore
import kotlinx.coroutines.runBlocking
import javax.swing.JComponent

/**
 * Module builder to construct AtCoderTools module. This is used in new project wizard dialog.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_model/module.html">Intellij Documentation</a>
 */
class AtCoderToolsModuleBuilder : ModuleBuilder(), ModuleBuilderListener {

    init {
        // Register itself so that [moduleCreated] callback is invoked after the module
        // is created.
        // https://www.jetbrains.org/intellij/sdk/docs/reference_guide/project_wizard.html#implementing-module-builder-listener
        addListener(this)
    }

    private val setupView = AtCoderToolsModuleSetupView()

    override fun createProject(name: String, path: String): Project? {
        val project = super.createProject(name, path) ?: return null
        runBlocking {
            project.stateStore.save()
        }
        return project
    }

    override fun getModuleType() = AtCoderToolsModuleType.getInstance()
    override fun createWizardSteps(
        wizardContext: WizardContext,
        modulesProvider: ModulesProvider
    ): Array<ModuleWizardStep> {
        return arrayOf(AtCoderToolsModuleInitializationStep(wizardContext, setupView))
    }

    override fun setupModule(module: Module) {
        super.setupModule(module)
        val facetManager = FacetManager.getInstance(module)
        val modifiableModel = facetManager.createModifiableModel()
        val facet = facetManager.createFacet(AtCoderToolsFacet.getFacetType(), AtCoderToolsFacet.NAME, null)
        facet.configuration.loadState(setupView.atCoderToolsProperties)
        modifiableModel.addFacet(facet)
        modifiableModel.commit()
    }

    override fun setupRootModel(modifiableRootModel: ModifiableRootModel) {
        if (myJdk != null) {
            modifiableRootModel.sdk = myJdk
        } else {
            modifiableRootModel.inheritSdk()
        }
        doAddContentEntry(modifiableRootModel)
    }

    /**
     * Does post-process of the module creation.
     */
    override fun moduleCreated(module: Module) {
        // Automatically starts gen-command.
        module.project.findAtCoderToolsToolWindow()?.show {
            module.project.findAtCoderToolsFacet()?.let {
                executeGenCommand(it)
            }
        }
    }
}

class AtCoderToolsModuleInitializationStep(
    private val wizardContext: WizardContext,
    private val setupView: AtCoderToolsModuleSetupView): ModuleWizardStep() {
    override fun updateDataModel() {
        wizardContext.defaultModuleName = setupView.atCoderToolsProperties.contestId
    }
    override fun getComponent(): JComponent = setupView.component
    override fun getPreferredFocusedComponent(): JComponent = setupView.preferredFocusedComponent
    override fun validate(): Boolean {
        if (setupView.atCoderToolsProperties.contestId.isEmpty()) {
            throw ConfigurationException("Contest ID is a required field")
        }
        return true
    }

    fun setContestId(contestId: String) {
        setupView.setContestId(contestId)
    }
}