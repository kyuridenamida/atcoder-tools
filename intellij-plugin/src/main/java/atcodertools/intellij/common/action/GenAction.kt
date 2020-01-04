package atcodertools.intellij.common.action

import atcodertools.intellij.common.command.executeGenCommand
import atcodertools.intellij.common.facet.findAtCoderToolsFacet
import atcodertools.intellij.common.toolwindow.findAtCoderToolsToolWindowView
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAware

/**
 * Generates initial code using atcoder-tools for a contest specified by [atcodertools.intellij.common.facet.AtCoderToolsFacet].
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/basics/getting_started/creating_an_action.html">IntelliJ Documentation</a>
 */
class GenAction : AnAction(), DumbAware {
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