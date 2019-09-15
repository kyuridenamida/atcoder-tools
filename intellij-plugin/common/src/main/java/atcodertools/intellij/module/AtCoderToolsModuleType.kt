package atcodertools.intellij.module

import atcodertools.intellij.service.AtCoderToolsApplicationService
import com.intellij.icons.AllIcons
import com.intellij.ide.util.projectWizard.ModuleBuilder
import com.intellij.ide.util.projectWizard.ModuleWizardStep
import com.intellij.ide.util.projectWizard.SettingsStep
import com.intellij.openapi.module.ModuleType
import com.intellij.openapi.module.ModuleTypeManager
import javax.swing.Icon

/**
 * Represents AtCoderTools module type.
 */
class AtCoderToolsModuleType : ModuleType<AtCoderToolsModuleBuilder>(ID) {
    companion object {
        const val ID = "ATCODER_TOOLS_MODULE"
        fun getInstance(): AtCoderToolsModuleType =
            ModuleTypeManager.getInstance().findByID(ID) as AtCoderToolsModuleType
    }

    override fun createModuleBuilder() = AtCoderToolsModuleBuilder()

    override fun getName() = "AtCoderTools Module"

    override fun getDescription() = "AtCoderTools Module"

    override fun getNodeIcon(isOpened: Boolean): Icon = AllIcons.General.Information

    override fun modifyProjectTypeStep(settingsStep: SettingsStep, moduleBuilder: ModuleBuilder): ModuleWizardStep? {
        return AtCoderToolsApplicationService.getInstance().createModuleWizardStep(settingsStep, moduleBuilder)
    }

    override fun modifySettingsStep(settingsStep: SettingsStep, moduleBuilder: ModuleBuilder): ModuleWizardStep? {
        settingsStep.moduleNameLocationSettings?.moduleName = settingsStep.context.defaultModuleName
        return null
    }
}