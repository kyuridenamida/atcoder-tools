package atcodertools.intellij.common.service

import com.intellij.ide.util.projectWizard.ModuleBuilder
import com.intellij.ide.util.projectWizard.ModuleWizardStep
import com.intellij.ide.util.projectWizard.SettingsStep
import com.intellij.openapi.components.ServiceManager
import com.intellij.openapi.module.ModuleType

/**
 * An application level service. Each language specific AtCoder plugin must implement and provide this service
 * to perform the language specific setup.
 */
interface AtCoderToolsApplicationService {
    companion object {
        /**
         * Returns a registered implementation of this service.
         */
        fun getInstance() = requireNotNull(ServiceManager.getService(AtCoderToolsApplicationService::class.java))
    }

    /**
     * Returns true if a given [moduleType] is supported by this plugin.
     */
    fun isSuitableModuleType(moduleType: ModuleType<*>?): Boolean

    /**
     * Returns a [ModuleWizardStep] to be displayed in the module setup wizard. You can return null if your
     * language doesn't support multi-module project (e.g. CLion).
     */
    fun createModuleWizardStep(settingsStep: SettingsStep, moduleBuilder: ModuleBuilder): ModuleWizardStep?

    /**
     * Returns a programming language code to be passed into atcoder-tools. (e.g. cpp, java, etc).
     */
    fun programmingLanguage(): String
}