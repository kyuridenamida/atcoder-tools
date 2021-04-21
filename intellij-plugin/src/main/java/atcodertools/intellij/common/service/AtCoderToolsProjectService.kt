package atcodertools.intellij.common.service

import atcodertools.intellij.common.facet.AtCoderToolsFacet
import atcodertools.intellij.common.facet.AtCoderToolsProblemFacet
import atcodertools.intellij.common.util.ProblemMetadata
import com.intellij.openapi.components.ServiceManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import org.jetbrains.concurrency.Promise
import java.nio.file.Path


/**
 * A project level service. Each language specific AtCoder plugin must implement and provide this service
 * to perform the language specific setup.
 */
interface AtCoderToolsProjectService {
    companion object {
        /**
         * Returns a registered implementation of this service.
         */
        fun getInstance(project: Project) = requireNotNull(
            ServiceManager.getService(project, AtCoderToolsProjectService::class.java))
    }

    /**
     * Creates a module (or modify your root module if it is a single module project) for a given
     * problem. The generated template code by atcoder-tools are located in [problemDir]. You also
     * have to create [AtCoderToolsProblemFacet] and add it to the new module.
     */
    fun createModuleForProblem(facet: AtCoderToolsFacet, problemDir: VirtualFile, metadata: ProblemMetadata)

    /**
     * Invoked after problem module creation finishes.
     */
    fun onAllProblemModuleCreated()

    /**
     * Returns a [Path] of a solution executable file for a given problem to be passed into
     * atcoder-tools. You can return null if there is a build error.
     */
    fun getSolutionExecutablePathForProblem(facet: AtCoderToolsProblemFacet): Promise<Path>?
}