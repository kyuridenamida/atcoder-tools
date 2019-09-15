package atcodertools.intellij.uitest

import com.intellij.execution.impl.ConsoleViewImpl
import com.intellij.testGuiFramework.fixtures.ActionButtonFixture
import com.intellij.testGuiFramework.framework.RunWithIde
import com.intellij.testGuiFramework.impl.GuiTestCase
import com.intellij.testGuiFramework.impl.button
import com.intellij.testGuiFramework.impl.jList
import com.intellij.testGuiFramework.launcher.ide.CommunityIde
import com.intellij.testGuiFramework.util.step
import com.intellij.testGuiFramework.util.waitFor
import org.fest.assertions.Assertions.assertThat
import org.fest.swing.core.Robot
import org.fest.swing.exception.ComponentLookupException
import org.junit.Test
import java.awt.Container

@RunWithIde(CommunityIde::class)
class EndToEndIntegrationTest : GuiTestCase() {
    @Test
    fun createAtCoderToolsProject() {
        welcomeFrame {
            createNewProject()
            dialog("New Project") {
                System.err.println("atcoder tools button")
                jList("AtCoderTools").clickItem("AtCoderTools")
                button("Next").click()
                typeText("agc029")
                button("Next").click()
                button("Finish").click()
            }
        }

        ideFrame {
            waitForBackgroundTasksToFinish()

            editor {
                waitFor {
                    currentFile != null
                }

                // Make sure that gen command finishes successfully and the solution file of
                // the first problem is open automatically.
                val currentSelectedFile = requireNotNull(currentFile)
                assertThat(currentSelectedFile.name).isEqualTo("main.java")
                assertThat(currentSelectedFile.parent.name).isEqualTo("A")

                // Also make sure that all other solution files are opened.
                waitFor { hasTab("A/main.java") }
                waitFor { hasTab("B/main.java") }
                waitFor { hasTab("C/main.java") }
                waitFor { hasTab("D/main.java") }
                waitFor { hasTab("E/main.java") }
                waitFor { hasTab("F/main.java") }
            }

            toolwindow("AtCoderTools") {
                content("Console") {
                    assertThat(
                        ActionButtonFixture.fixtureByTextAnyState(
                            getContent().actionsContextComponent, myRobot, "AtCoder Test").isEnabled).isTrue()
                    assertThat(
                        ActionButtonFixture.fixtureByTextAnyState(
                            getContent().actionsContextComponent, myRobot, "AtCoder Submit").isEnabled).isTrue()
                    assertThat(
                        ActionButtonFixture.fixtureByTextAnyState(
                            getContent().actionsContextComponent, myRobot, "AtCoder Stop").isEnabled).isFalse()

                    step("Run AtCoderTools test command") {
                        ActionButtonFixture.fixtureByText(
                            getContent().actionsContextComponent, myRobot, "AtCoder Test"
                        ).click()
                        // Compiling Java file may time some time so let's wait for 60 seconds.
                        waitFor(60) {
                            findConsoleView(getContent().component, myRobot)?.editor?.document?.text
                                ?.contains("Some cases FAILED (passed 0 of 2)") ?: false
                        }
                    }
                }
            }

            closeProjectAndWaitWelcomeFrame()
        }
    }

    private fun findConsoleView(container: Container, robot: Robot): ConsoleViewImpl? {
        return try {
            robot.finder().findByType(container, ConsoleViewImpl::class.java, false)
        } catch (e: ComponentLookupException) {
            null
        }
    }
}