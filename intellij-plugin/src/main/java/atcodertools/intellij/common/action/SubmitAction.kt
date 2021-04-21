package atcodertools.intellij.common.action

import atcodertools.intellij.common.command.executeSubmitCommand
import atcodertools.intellij.common.facet.findAtCoderToolsFacet
import atcodertools.intellij.common.facet.findSelectedAtCoderToolsProblemFacet
import atcodertools.intellij.common.toolwindow.findAtCoderToolsToolWindowView
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAware

/**
 * Submit code which a user is currently opening using atcoder-tools. If there are multiple open files (such as
 * in split editor tab), the most recently interacted one is going to be submitted after all sample tests pass.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/basics/getting_started/creating_an_action.html">IntelliJ Documentation</a>
 */
class SubmitAction : AnAction(), DumbAware {
    override fun update(e: AnActionEvent) {
        val project = e.project
        if (project == null || project.findAtCoderToolsFacet()?.configuration?.state?.isContentEnvGenerated == false) {
            e.presentation.isEnabled = false
            e.presentation.isVisible = false
            return
        }
        e.presentation.isVisible = true

        if (project.findAtCoderToolsToolWindowView()?.isProcessRunning == true) {
            e.presentation.isEnabled = false
            return
        }

        val isSolutionFileSelected = project.findSelectedAtCoderToolsProblemFacet() != null
        e.presentation.isEnabled = isSolutionFileSelected
    }

    override fun actionPerformed(e: AnActionEvent) {
        val facet = e.project?.findSelectedAtCoderToolsProblemFacet() ?: return
        executeSubmitCommand(facet)
    }
}