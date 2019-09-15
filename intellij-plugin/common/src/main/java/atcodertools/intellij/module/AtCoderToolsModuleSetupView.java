package atcodertools.intellij.module;

import atcodertools.intellij.model.AtCoderToolsProperties;
import com.intellij.ui.DocumentAdapter;
import org.jetbrains.annotations.NotNull;

import javax.annotation.Nullable;
import javax.swing.*;
import javax.swing.event.DocumentEvent;

/**
 * A view used in project setup wizard to collect required information to initialize AtCoderTools project module.
 *
 * @see AtCoderToolsModuleBuilder
 */
public class AtCoderToolsModuleSetupView {

    /**
     * An interface to listen changes on {@link AtCoderToolsProperties}.
     */
    public interface AtCoderToolsPropertiesChangedListener {
        /**
         * Invoked with new properties when any changes are made.
         */
        void onPropertiesChanged(AtCoderToolsProperties properties);
    }

    @Nullable
    private AtCoderToolsPropertiesChangedListener listener;

    // These swing components are instantiated by reflection before the constructor.
    private JTextField contestIdTextField;
    private JPanel rootPanel;

    public AtCoderToolsModuleSetupView() {
        contestIdTextField.getDocument().addDocumentListener(new DocumentAdapter() {
            @Override
            protected void textChanged(@NotNull DocumentEvent e) {
                if (listener != null) {
                    listener.onPropertiesChanged(getAtCoderToolsProperties());
                }
            }
        });
    }

    public JComponent getComponent() {
        return rootPanel;
    }

    public JComponent getPreferredFocusedComponent() {
        return contestIdTextField;
    }

    public AtCoderToolsProperties getAtCoderToolsProperties() {
        AtCoderToolsProperties properties = new AtCoderToolsProperties();
        properties.setContestId(contestIdTextField.getText().trim());
        return properties;
    }

    public void setContestId(@NotNull String contestId) {
        contestIdTextField.setText(contestId);
    }

    public void setListener(@Nullable AtCoderToolsPropertiesChangedListener listener) {
        this.listener = listener;
    }
}
