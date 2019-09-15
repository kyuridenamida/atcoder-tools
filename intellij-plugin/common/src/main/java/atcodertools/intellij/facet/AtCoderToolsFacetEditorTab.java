package atcodertools.intellij.facet;

import atcodertools.intellij.model.AtCoderToolsProperties;
import com.intellij.facet.ui.FacetEditorTab;
import com.intellij.openapi.options.ConfigurationException;
import org.jetbrains.annotations.Nls;
import org.jetbrains.annotations.NotNull;

import javax.swing.*;

/**
 * EditorTab for {@link AtCoderToolsProperties}.
 * <p>
 * This editor is displayed in project module setting window and let users modify {@link AtCoderToolsProperties}.
 *
 * @see AtCoderToolsFacet
 */
public class AtCoderToolsFacetEditorTab extends FacetEditorTab {
    private JTextField contestIdTextField;
    private JPanel rootPanel;

    @NotNull
    private final AtCoderToolsProperties state;

    public AtCoderToolsFacetEditorTab(@NotNull AtCoderToolsProperties state) {
        this.state = state;
    }

    @NotNull
    @Override
    public JComponent createComponent() {
        return rootPanel;
    }

    @Nls(capitalization = Nls.Capitalization.Title)
    @Override
    public String getDisplayName() {
        return "AtCoderTools Properties";
    }

    @Override
    public boolean isModified() {
        return !state.getContestId().equals(contestIdTextField.getText());
    }

    @Override
    public void reset() {
        contestIdTextField.setText(state.getContestId());
    }

    @Override
    public void apply() throws ConfigurationException {
        state.setContestId(contestIdTextField.getText().trim());
    }
}
