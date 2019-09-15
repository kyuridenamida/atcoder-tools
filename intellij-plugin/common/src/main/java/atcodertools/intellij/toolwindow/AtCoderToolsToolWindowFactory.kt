package atcodertools.intellij.toolwindow

import com.intellij.openapi.project.DumbAware
import com.intellij.openapi.project.Project
import com.intellij.openapi.util.Key
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.openapi.wm.ex.ToolWindowManagerEx

/**
 * A factory to construct tool window for AtCoderTools module.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/user_interface_components/tool_windows.html">Intellij Documentation</a>
 */
class AtCoderToolsToolWindowFactory : ToolWindowFactory, DumbAware {
    companion object {
        internal val ATCODER_TOOLS_TOOL_WINDOW_VIEW_KEY =
            Key<AtCoderToolsToolWindowView>("ATCODER_TOOLS_TOOL_WINDOW_VIEW_KEY")
    }

    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val view = AtCoderToolsToolWindowView(project)
        val content = toolWindow.contentManager.factory.createContent(
            view.component, "Console", true
        )
        content.putUserData(ATCODER_TOOLS_TOOL_WINDOW_VIEW_KEY, view)
        toolWindow.contentManager.addContent(content)
    }
}

fun Project.findAtCoderToolsToolWindow(): ToolWindow? =
    ToolWindowManagerEx.getInstanceEx(this).getToolWindow("AtCoderTools")

fun Project.findAtCoderToolsToolWindowView(): AtCoderToolsToolWindowView? =
    findAtCoderToolsToolWindow()
    ?.contentManager
    ?.findContent("Console")
    ?.getUserData(AtCoderToolsToolWindowFactory.ATCODER_TOOLS_TOOL_WINDOW_VIEW_KEY)