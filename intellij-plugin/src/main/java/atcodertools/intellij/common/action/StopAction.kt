package atcodertools.intellij.common.action

import atcodertools.intellij.common.command.stopExecution
import atcodertools.intellij.common.facet.findAtCoderToolsFacet
import atcodertools.intellij.common.toolwindow.findAtCoderToolsToolWindowView
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent

/**
 * Terminate running atcoder-tools program execution.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/basics/getting_started/creating_an_action.html">IntelliJ Documentation</a>
 */
class StopAction : AnAction() {
    override fun update(e: AnActionEvent) {
        e.presentation.isEnabled = e.project?.findAtCoderToolsToolWindowView()?.isProcessRunning ?: false
    }

    override fun actionPerformed(e: AnActionEvent) {
        val facet = e.project?.findAtCoderToolsFacet() ?: return
        stopExecution(facet)
    }
}