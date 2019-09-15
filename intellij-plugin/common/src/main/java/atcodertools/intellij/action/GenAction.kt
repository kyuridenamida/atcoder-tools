package atcodertools.intellij.action

import atcodertools.intellij.command.executeGenCommand
import atcodertools.intellij.facet.findAtCoderToolsFacet
import atcodertools.intellij.toolwindow.findAtCoderToolsToolWindowView
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent

/**
 * Generates initial code using atcoder-tools for a contest specified by [atcodertools.intellij.facet.AtCoderToolsFacet].
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/basics/getting_started/creating_an_action.html">IntelliJ Documentation</a>
 */
class GenAction : AnAction() {
    override fun update(e: AnActionEvent) {
        if (e.project?.findAtCoderToolsFacet()?.configuration?.state?.isContentEnvGenerated == true) {
            e.presentation.isEnabled = false
            e.presentation.isVisible = false
            return
        }
        e.presentation.isVisible = true

        val isRunning = e.project?.findAtCoderToolsToolWindowView()?.isProcessRunning ?: false
        e.presentation.isEnabled = !isRunning
    }

    override fun actionPerformed(e: AnActionEvent) {
        val facet = e.project?.findAtCoderToolsFacet() ?: return
        executeGenCommand(facet)
    }
}