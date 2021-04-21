package atcodertools.intellij.common.toolwindow

import atcodertools.intellij.common.facet.findAtCoderToolsFacet
import com.intellij.openapi.project.Project
import com.intellij.openapi.util.Condition

/**
 * A predicate to determine if a module is compatible with AtCoderTools tool window.
 *
 * @see <a href="https://www.jetbrains.org/intellij/sdk/docs/user_interface_components/tool_windows.html">Intellij Documentation</a>
 */
class AtCoderToolsToolWindowFactoryCondition : Condition<Project> {
    override fun value(project: Project) = project.findAtCoderToolsFacet() != null
}