package atcodertools.intellij.toolwindow;

import com.intellij.execution.actions.ClearConsoleAction;
import com.intellij.execution.impl.ConsoleViewImpl;
import com.intellij.execution.process.ProcessHandler;
import com.intellij.openapi.actionSystem.*;
import com.intellij.openapi.editor.Editor;
import com.intellij.openapi.editor.actions.ScrollToTheEndToolbarAction;
import com.intellij.openapi.editor.actions.ToggleUseSoftWrapsToolbarAction;
import com.intellij.openapi.editor.impl.softwrap.SoftWrapAppliancePlaces;
import com.intellij.openapi.project.Project;
import com.intellij.openapi.ui.SimpleToolWindowPanel;
import com.intellij.openapi.util.Disposer;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import javax.swing.*;


/**
 * Tool window view used in AtCoderTools tool window (a view displayed bottom of the IDE).
 *
 * @see AtCoderToolsToolWindowFactory
 */
public class AtCoderToolsToolWindowView {
    private JPanel rootComponent;

    private final ConsoleViewImpl consoleViewImpl;

    @Nullable
    private ProcessHandler processHandler;

    public AtCoderToolsToolWindowView(@NotNull Project project) {
        SimpleToolWindowPanel mainPanel = new SimpleToolWindowPanel(/*vertical=*/false);

        // Set viewer param to false so that a user may input their user id and password
        // to the console when necessary.
        consoleViewImpl =  new ConsoleViewImpl(project, /*viewer=*/false) {
            @NotNull
            @Override
            public AnAction[] createConsoleActions() {
                Editor editor = getEditor();
                AnAction switchSoftWrapsAction = new ToggleUseSoftWrapsToolbarAction(SoftWrapAppliancePlaces.CONSOLE) {
                    @Override
                    protected Editor getEditor(@NotNull AnActionEvent e) {
                        return editor;
                    }
                };
                AnAction autoScrollToTheEndAction = new ScrollToTheEndToolbarAction(editor);
                AnAction clearConsoleAction = new ClearConsoleAction() {
                    @Override
                    public void update(@NotNull AnActionEvent e) {
                        boolean enabled = getContentSize() > 0;
                        e.getPresentation().setEnabled(enabled);
                    }

                    @Override
                    public void actionPerformed(@NotNull AnActionEvent e) {
                        clear();
                    }
                };
                return new AnAction[] {switchSoftWrapsAction, autoScrollToTheEndAction, clearConsoleAction};
            }
        };
        Disposer.register(project, consoleViewImpl);
        mainPanel.setContent(consoleViewImpl.getComponent());

        DefaultActionGroup actionGroup = new DefaultActionGroup(
                ActionManager.getInstance().getAction("atcodertools.intellij.action.StopAction"),
                Separator.getInstance(),
                ActionManager.getInstance().getAction("atcodertools.intellij.action.GenAction"),
                ActionManager.getInstance().getAction("atcodertools.intellij.action.TestAction"),
                Separator.getInstance(),
                ActionManager.getInstance().getAction("atcodertools.intellij.action.SubmitAction"));
        actionGroup.addSeparator();
        actionGroup.addAll(consoleViewImpl.createConsoleActions());

        mainPanel.setToolbar(ActionManager.getInstance().createActionToolbar(
                "AtCoderTools",
                actionGroup,
                /*horizontal=*/false
        ).getComponent());

        rootComponent.add(mainPanel);
    }

    public JComponent getComponent() {
        return rootComponent;
    }

    public void setProcessHandler(@Nullable ProcessHandler processHandler) {
        ProcessHandler prevProcessHandler = this.processHandler;
        if (prevProcessHandler != null) {
            prevProcessHandler.destroyProcess();
        }

        this.processHandler = processHandler;
        if (processHandler != null) {
            consoleViewImpl.attachToProcess(processHandler);
        }
    }

    public boolean isProcessRunning() {
        if (processHandler == null) {
            return false;
        }
        return !processHandler.isProcessTerminated() && !processHandler.isProcessTerminating();
    }
}
