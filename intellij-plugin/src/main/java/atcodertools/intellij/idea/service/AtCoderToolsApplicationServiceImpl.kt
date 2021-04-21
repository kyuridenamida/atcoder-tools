package atcodertools.intellij.idea.service

import atcodertools.intellij.common.service.AtCoderToolsApplicationService
import com.intellij.ide.util.projectWizard.ModuleBuilder
import com.intellij.ide.util.projectWizard.ModuleWizardStep
import com.intellij.ide.util.projectWizard.ProjectWizardStepFactory
import com.intellij.ide.util.projectWizard.SettingsStep
import com.intellij.openapi.module.JavaModuleType
import com.intellij.openapi.module.ModuleType

class AtCoderToolsApplicationServiceImpl : AtCoderToolsApplicationService {
    override fun isSuitableModuleType(moduleType: ModuleType<*>?) = moduleType is JavaModuleType

    override fun createModuleWizardStep(settingsStep: SettingsStep, moduleBuilder: ModuleBuilder): ModuleWizardStep? {
        return ProjectWizardStepFactory.getInstance().createJavaSettingsStep(settingsStep, moduleBuilder) {
            moduleBuilder.isSuitableSdkType(it)
        }
    }

    override fun programmingLanguage() = "java"
}