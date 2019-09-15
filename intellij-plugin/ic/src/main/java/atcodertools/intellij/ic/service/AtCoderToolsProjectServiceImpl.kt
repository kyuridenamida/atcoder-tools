package atcodertools.intellij.ic.service

import atcodertools.intellij.facet.AtCoderToolsFacet
import atcodertools.intellij.facet.AtCoderToolsProblemFacet
import atcodertools.intellij.service.AtCoderToolsProjectService
import atcodertools.intellij.util.ProblemMetadata
import com.intellij.execution.configurations.SimpleJavaParameters
import com.intellij.facet.FacetManager
import com.intellij.ide.highlighter.ModuleFileType
import com.intellij.ide.util.projectWizard.JavaModuleBuilder
import com.intellij.openapi.project.Project
import com.intellij.openapi.projectRoots.JdkUtil
import com.intellij.openapi.roots.ModuleRootManager
import com.intellij.openapi.util.Pair
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.packaging.artifacts.ArtifactManager
import com.intellij.packaging.impl.artifacts.JarFromModulesTemplate
import com.intellij.task.ProjectTaskManager
import org.jetbrains.concurrency.Promise
import java.io.File
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.attribute.PosixFilePermissions

class AtCoderToolsProjectServiceImpl(private val project: Project) : AtCoderToolsProjectService {
    override fun createModuleForProblem(facet: AtCoderToolsFacet, problemDir: VirtualFile, metadata: ProblemMetadata) {
        // problemDir.findChild("main.java")?.rename(/*requester=*/this, "Main.java")

        val builder = JavaModuleBuilder().apply {
            name = problemDir.name
            moduleFilePath =
                problemDir.path + File.separator + problemDir.name + ModuleFileType.DOT_DEFAULT_EXTENSION
            sourcePaths = listOf(Pair(contentEntryPath, ""))
        }
        val problemModule =
            builder.createAndCommitIfNeeded(project, null, /*runFromProjectWizard=*/false)

        val facetManager = FacetManager.getInstance(problemModule)
        val modifiableProblemFacetModel = facetManager.createModifiableModel()
        val problemFacet = facetManager.createFacet(
            AtCoderToolsProblemFacet.getFacetType(), AtCoderToolsProblemFacet.NAME, null
        )
        problemFacet.configuration.state.problemName = problemDir.name
        modifiableProblemFacetModel.addFacet(problemFacet)
        modifiableProblemFacetModel.commit()

        val artifactManager = ArtifactManager.getInstance(project)
        val artifactModel = artifactManager.createModifiableModel()
        val artifactConfig = requireNotNull(
            JarFromModulesTemplate(artifactManager.resolvingContext)
                .doCreateArtifact(
                    arrayOf(problemModule),
                    "Main",
                    problemDir.path,
                    /*extractLibrariesToJar=*/true,
                    /*includeTests=*/false
                )
        )
        artifactModel.addArtifact(
            artifactConfig.artifactName, artifactConfig.artifactType, artifactConfig.rootElement
        )
        artifactModel.commit()
    }

    override fun onAllProblemModuleCreated() {}

    override fun getSolutionExecutablePathForProblem(facet: AtCoderToolsProblemFacet): Promise<Path>? {
        val jarArtifact = ArtifactManager.getInstance(project).findArtifact("${facet.module.name}:jar") ?: return null
        return ProjectTaskManager.getInstance(project).build(jarArtifact).then {
            val solverCommandLine = JdkUtil.setupJVMCommandLine(SimpleJavaParameters().apply {
                jdk = ModuleRootManager.getInstance(facet.module).sdk
                jarPath = jarArtifact.outputFilePath
            })
            val execPath = Files.createTempFile(
                "",
                "",
                PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------"))
            )
            execPath.toFile().writeText("#!/bin/sh\n${solverCommandLine.commandLineString}")
            execPath
        }
    }
}