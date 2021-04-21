package atcodertools.intellij.clion.service

import atcodertools.intellij.common.service.AtCoderToolsApplicationService
import com.intellij.ide.util.projectWizard.ModuleBuilder
import com.intellij.ide.util.projectWizard.ModuleWizardStep
import com.intellij.ide.util.projectWizard.SettingsStep
import com.intellij.openapi.module.ModuleType
import com.jetbrains.cidr.cpp.CPPModuleType

class AtCoderToolsApplicationServiceImpl : AtCoderToolsApplicationService {
    override fun isSuitableModuleType(moduleType: ModuleType<*>?) = moduleType is CPPModuleType

    /**
     * CLion enforces a single module project so this module wizard is never be used.
     */
    override fun createModuleWizardStep(settingsStep: SettingsStep, moduleBuilder: ModuleBuilder): ModuleWizardStep? = null

    override fun programmingLanguage() = "cpp"
}