package atcodertools.intellij.clion.wizard

import atcodertools.intellij.common.command.executeGenCommand
import atcodertools.intellij.common.facet.AtCoderToolsFacet
import atcodertools.intellij.common.module.AtCoderToolsModuleSetupView
import atcodertools.intellij.common.toolwindow.findAtCoderToolsToolWindow
import com.google.common.io.Resources
import com.intellij.facet.FacetManager
import com.intellij.facet.ui.ValidationResult
import com.intellij.icons.AllIcons
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.application.runInEdt
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.module.Module
import com.intellij.openapi.project.Project
import com.intellij.openapi.util.Computable
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.project.stateStore
import com.intellij.ui.components.panels.VerticalBox
import com.jetbrains.cidr.cpp.cmake.projectWizard.CLionProjectWizardUtils
import com.jetbrains.cidr.cpp.cmake.projectWizard.generators.CMakeCPPProjectGenerator
import com.jetbrains.cidr.cpp.cmake.projectWizard.generators.settings.CMakeProjectSettings
import kotlinx.coroutines.runBlocking
import java.awt.Dimension
import javax.swing.Box
import javax.swing.JComponent


/**
 * A project template generator for AtCoder Tools based project.
 * This generator is registered to CLion by plugin.xml in the resource file and "AtCoder Tools" project
 * option will be available in the new project wizard dialog.
 */
class AtCoderToolsProjectGenerator : CMakeCPPProjectGenerator() {
    private val atcoderSetupView = AtCoderToolsModuleSetupView()
    private val settingPanel = VerticalBox().apply {
        super.getSettingsPanel()?.let {
            add(it)
            // Add vertical spacer to make UI look nice.
            add(Box.createRigidArea(Dimension(0, 5)))
        }
        add(atcoderSetupView.component)
        atcoderSetupView.setListener {
            // TODO: Call ProjectSettingsStepBase#checkValid() somehow from here to reevaluate the input
            //       and re-enable the OK button in the wizard. This is usually done by calling checkValid
            //       runnable passed into ProjectGeneratorPeer#getComponent. But unfortunately, CLion
            //       customizes this behavior and disables it by overriding
            //       CLionProjectSettingsStep#createAdvancedSettings(). So currently there is no way to
            //       call checkValid() from here. We need either a fix in the upstream or do some black magic
            //       here to workaround.
        }
    }

    /**
     * Returns the name of this project type. Displayed in the new project wizard dialog.
     */
    override fun getName() = "AtCoderTools"

    /**
     * Returns the icon of this project type. Displayed in the new project wizard dialog.
     */
    override fun getLogo() = AllIcons.General.Information

    /**
     * Returns [JComponent] to be displayed in the new project wizard dialog.
     */
    override fun getSettingsPanel() = settingPanel

    /**
     * Checks if a user input sufficient information to create a new project in the UI.
     */
    override fun validate(baseDirPath: String): ValidationResult {
        val result = super.validate(baseDirPath)
        if (!result.isOk) {
            return result
        }
        if (atcoderSetupView.atCoderToolsProperties.contestId.isEmpty()) {
            return ValidationResult("Contest ID is a required field")
        }
        return ValidationResult.OK
    }

    /**
     * Returns [VirtualFile]s to be added as the source file of the project.
     */
    override fun createSourceFiles(projectName: String, projectRootDir: VirtualFile): Array<VirtualFile> {
        // Generates a copy of bits/stdc++.h so that it can be used with clang.
        val bitsDirectory = ApplicationManager.getApplication().runWriteAction(object: Computable<VirtualFile> {
            override fun compute(): VirtualFile {
                return projectRootDir.createChildDirectory(this, "include").createChildDirectory(this, "bits")
            }
        })
        return arrayOf(createProjectFileWithContent(
            bitsDirectory,
            "stdc++.h",
            Resources.toString(Resources.getResource(javaClass, "/include/bits/stdc++.h"), Charsets.UTF_8)))
    }

    /**
     * Returns an initial content of the project CMake file.
     */
    override fun getCMakeFileContent(projectName: String): String {
        val builder = StringBuffer()
        builder.append(CLionProjectWizardUtils.getCMakeFileHeader(projectName, this.cMakeProjectSettings))
        builder.append("\n")
        builder.append("include_directories(include)\n")
        return builder.toString()
    }

    override fun generateProject(
        project: Project,
        baseDir: VirtualFile,
        settings: CMakeProjectSettings,
        module: Module
    ) {
        super.generateProject(project, baseDir, settings, module)

        ApplicationManager.getApplication().runWriteAction {
            val facetManager = FacetManager.getInstance(module)
            val modifiableModel = facetManager.createModifiableModel()
            val facet = facetManager.createFacet(AtCoderToolsFacet.getFacetType(), AtCoderToolsFacet.NAME, null)
            facet.configuration.loadState(atcoderSetupView.atCoderToolsProperties)
            modifiableModel.addFacet(facet)
            modifiableModel.commit()

            runBlocking {
                project.stateStore.save()
            }

            runInEdt {
                // We don't want to show CMakeFile and other template header files in the editor
                // after you create a project, so we close everything before we generate source
                // code by AtCoder tools.
                val editorManager = FileEditorManager.getInstance(project)
                editorManager.openFiles.forEach {
                    editorManager.closeFile(it)
                }

                project.findAtCoderToolsToolWindow()?.show {
                    executeGenCommand(facet)
                }
            }
        }
    }
}