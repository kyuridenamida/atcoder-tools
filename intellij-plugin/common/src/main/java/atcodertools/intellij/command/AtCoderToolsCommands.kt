package atcodertools.intellij.command

import atcodertools.intellij.facet.AtCoderToolsFacet
import atcodertools.intellij.facet.AtCoderToolsProblemFacet
import atcodertools.intellij.facet.findAtCoderToolsFacet
import atcodertools.intellij.service.AtCoderToolsApplicationService
import atcodertools.intellij.service.AtCoderToolsProjectService
import atcodertools.intellij.toolwindow.findAtCoderToolsToolWindow
import atcodertools.intellij.toolwindow.findAtCoderToolsToolWindowView
import atcodertools.intellij.util.getProblemMetadataForProblem
import com.intellij.execution.RunManagerEx
import com.intellij.execution.configurations.GeneralCommandLine
import com.intellij.execution.process.KillableColoredProcessHandler
import com.intellij.execution.process.ProcessAdapter
import com.intellij.execution.process.ProcessEvent
import com.intellij.openapi.Disposable
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.application.runInEdt
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.rootManager
import com.intellij.openapi.roots.ModuleRootManager
import com.intellij.openapi.util.Disposer
import com.intellij.openapi.vfs.CharsetToolkit
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.vfs.VirtualFileManager

/**
 * Executes "atcoder-tools gen" command. After successful execution, it creates sub-module for each problem and
 * add [AtCoderToolsProblemFacet] to each of them.
 */
fun executeGenCommand(facet: AtCoderToolsFacet) {
    val project = facet.module.project
    val view = project.findAtCoderToolsToolWindowView() ?: return
    val service = AtCoderToolsProjectService.getInstance(project)

    val command = GeneralCommandLine("atcoder-tools", "gen").apply {
        withCharset(CharsetToolkit.UTF8_CHARSET)
        setWorkDirectory(project.basePath)
        addParameters("--workspace", project.basePath!!)
        addParameters("--lang", AtCoderToolsApplicationService.getInstance().programmingLanguage())
        if (System.getProperty("atcodertools.intellij.command.noLogin", "false").toBoolean()) {
            addParameter("--without-login")
        }
        addParameter(facet.configuration.state.contestId)
    }
    val handler = KillableColoredProcessHandler(command)
    view.setProcessHandler(handler)
    handler.addProcessListener(object : ProcessAdapter() {
        override fun processTerminated(event: ProcessEvent) {
            if (event.exitCode != 0) {
                return
            }
            VirtualFileManager.getInstance().asyncRefresh {
                ApplicationManager.getApplication().runWriteAction {
                    var solutionForFirstProblem: VirtualFile? = null
                    ModuleRootManager.getInstance(facet.module).contentRoots.forEach { root ->
                        root.findChild(facet.configuration.state.contestId)?.children?.forEach { problemDir ->
                            val problemMetadata = getProblemMetadataForProblem(problemDir)
                            service.createModuleForProblem(facet, problemDir, problemMetadata)

                            // Opens generated source files in the editor.
                            runInEdt {
                                FileEditorManager.getInstance(project).openFile(
                                    requireNotNull(problemDir.findChild(problemMetadata.solutionSourceFileName)),
                                    false
                                )
                            }

                            if (solutionForFirstProblem == null) {
                                solutionForFirstProblem =
                                    requireNotNull(problemDir.findChild(problemMetadata.solutionSourceFileName))
                            }
                        }
                    }

                    // Opens the solution file for the first problem with focus so that a user can
                    // start coding immediately.
                    runInEdt {
                        solutionForFirstProblem?.let {
                            FileEditorManager.getInstance(project).openFile(it, /*focusEditor=*/true)
                        }
                    }

                    // Update facet and mark this module is fully initialized.
                    facet.configuration.state.isContentEnvGenerated = true

                    VirtualFileManager.getInstance().asyncRefresh {
                        service.onAllProblemModuleCreated()
                    }
                }
            }
        }
    }, project)
    handler.startNotify()

    Disposer.register(project, Disposable {
        handler.destroyProcess()
    })
}

/**
 * Terminates currently running "atcoder-tools" execution if any.
 */
fun stopExecution(facet: AtCoderToolsFacet) {
    val view = facet.module.project.findAtCoderToolsToolWindowView() ?: return
    view.setProcessHandler(null)
}

/**
 * Executes "atcoder-tools test" command if [submitOnTestPass] is false. If true, "atcoder-tools submit" command
 * is executed instead.
 */
fun executeTestCommand(facet: AtCoderToolsProblemFacet, submitOnTestPass: Boolean = false) {
    val project = facet.module.project
    val view = project.findAtCoderToolsToolWindowView() ?: return
    val service = AtCoderToolsProjectService.getInstance(project)

    // Change the target run configuration if there is one for this problem.
    // Note: Clion only builds executable for the selected run configuration so this
    // update is necessary.
    RunManagerEx.getInstanceEx(project).apply {
        findConfigurationByName(facet.configuration.state.problemName)?.let {
            selectedConfiguration = it
        }
    }

    service.getSolutionExecutablePathForProblem(facet)?.onSuccess { execPath ->
        val command = GeneralCommandLine("atcoder-tools").apply {
            withCharset(CharsetToolkit.UTF8_CHARSET)
            setWorkDirectory(facet.module.rootManager.contentRoots.first().path)
            if (submitOnTestPass) {
                addParameters("submit", "--unlock-safety")
            } else {
                addParameter("test")
            }
            addParameters("--exec", execPath.toString())
            addParameters(
                "--dir",
                "${project.basePath}" +
                        "/${project.findAtCoderToolsFacet()?.configuration?.state?.contestId}" +
                        "/${facet.configuration.state.problemName}")
        }

        val handler = KillableColoredProcessHandler(command)
        view.setProcessHandler(handler)
        handler.startNotify()
        Disposer.register(project, Disposable {
            handler.destroyProcess()
        })

        // Show AtCoderTools tool-window again. During the build, messages tool-window might steal
        // our focus.
        ApplicationManager.getApplication().invokeLater {
            project.findAtCoderToolsToolWindow()?.show(null)
        }
    }
}

/**
 * Executes "atcoder-tools submit" command.
 */
fun executeSubmitCommand(facet: AtCoderToolsProblemFacet) = executeTestCommand(facet, submitOnTestPass = true)