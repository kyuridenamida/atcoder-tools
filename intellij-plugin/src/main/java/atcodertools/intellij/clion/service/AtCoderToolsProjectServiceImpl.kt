package atcodertools.intellij.clion.service

import atcodertools.intellij.common.facet.AtCoderToolsFacet
import atcodertools.intellij.common.facet.AtCoderToolsProblemFacet
import atcodertools.intellij.common.service.AtCoderToolsProjectService
import atcodertools.intellij.common.util.ProblemMetadata
import com.intellij.facet.FacetManager
import com.intellij.openapi.actionSystem.ActionPlaces
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.command.WriteCommandAction
import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.LocalFileSystem
import com.intellij.openapi.vfs.VirtualFile
import com.jetbrains.cidr.cpp.cmake.actions.ReloadCMakeProjectAction
import com.jetbrains.cidr.cpp.cmake.model.CMakeConfiguration
import com.jetbrains.cidr.cpp.execution.CMakeAppRunConfiguration
import com.jetbrains.cidr.cpp.execution.build.CLionBuildConfigurationProvider
import com.jetbrains.cidr.cpp.execution.build.CMakeBuild
import com.jetbrains.cidr.cpp.execution.build.CMakeBuildConfigurationProvider
import org.jetbrains.concurrency.Promise
import org.jetbrains.concurrency.runAsync
import java.nio.file.Path

class AtCoderToolsProjectServiceImpl(private val project: Project) : AtCoderToolsProjectService {
    override fun createModuleForProblem(facet: AtCoderToolsFacet, problemDir: VirtualFile, metadata: ProblemMetadata) {
        // This looks weird but necessary because we need to change CMakeLists.txt which has a
        // PSI element.
        // https://intellij-support.jetbrains.com/hc/en-us/community/posts/360000140664
        ApplicationManager.getApplication().invokeLater {
            WriteCommandAction.runWriteCommandAction(project) {
                val projectBasePath = project.basePath ?: return@runWriteCommandAction
                val projectBaseDir = LocalFileSystem.getInstance().findFileByPath(projectBasePath) ?: return@runWriteCommandAction
                val cmakeFile = projectBaseDir.findChild("CMakeLists.txt") ?: return@runWriteCommandAction
                val document = FileDocumentManager.getInstance().getDocument(cmakeFile) ?: return@runWriteCommandAction
                document.insertString(
                    document.textLength,
                    "add_executable(${problemDir.name} ${facet.configuration.state.contestId}/${problemDir.name}/main.cpp)\n"
                )
            }
        }

        // Add problem-facet to the main module directly because CLion is a single module project.
        val facetManager = FacetManager.getInstance(facet.module)
        val modifiableProblemFacetModel = facetManager.createModifiableModel()
        val problemFacet = facetManager.createFacet(
            AtCoderToolsProblemFacet.getFacetType(), AtCoderToolsProblemFacet.NAME, null
        )
        problemFacet.configuration.state.problemName = problemDir.name
        modifiableProblemFacetModel.addFacet(problemFacet)
        modifiableProblemFacetModel.commit()
    }

    override fun onAllProblemModuleCreated() {
        val emptyEventWithProject = AnActionEvent.createFromDataContext(
            ActionPlaces.UNKNOWN, /*presentation=*/null) { dataId: String? -> when(dataId) {
            CommonDataKeys.PROJECT.name -> project
            else -> null
        } }
        ReloadCMakeProjectAction().actionPerformed(emptyEventWithProject)
    }

    override fun getSolutionExecutablePathForProblem(facet: AtCoderToolsProblemFacet): Promise<Path>? {
        val buildConfigProvider = CLionBuildConfigurationProvider.EP_NAME.findExtensionOrFail(
            CMakeBuildConfigurationProvider::class.java)
        val config = buildConfigProvider.getBuildableConfigurations(project).map {
            it as? CMakeConfiguration
        }.firstOrNull {
            it?.target?.name == facet.configuration.state.problemName
        } ?: return null

        return runAsync {
            val result = CMakeBuild.build(project, CMakeAppRunConfiguration.BuildAndRunConfigurations(config)).get()
            require(result.succeeded) {
                result.message
            }
            requireNotNull(config.productFile?.toPath())
        }
    }
}