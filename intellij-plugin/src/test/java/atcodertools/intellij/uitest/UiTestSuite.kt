package atcodertools.intellij.uitest

import atcodertools.intellij.uitest.testcase.EndToEndIntegrationTest
import com.intellij.testGuiFramework.framework.GuiTestSuite
import com.intellij.testGuiFramework.framework.GuiTestSuiteRunner
import org.junit.runner.RunWith
import org.junit.runners.Suite

@RunWith(GuiTestSuiteRunner::class)
@Suite.SuiteClasses(EndToEndIntegrationTest::class)
class UiTestSuite : GuiTestSuite()
