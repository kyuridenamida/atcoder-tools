package atcodertools.intellij.facet;

import atcodertools.intellij.model.AtCoderToolsProblemProperties;
import com.intellij.facet.ui.FacetEditorTab;
import org.jetbrains.annotations.Nls;
import org.jetbrains.annotations.NotNull;

import javax.swing.*;

/**
 * EditorTab for {@link AtCoderToolsProblemProperties}.
 * <p>
 * This editor is displayed in project module setting window and let users modify {@link AtCoderToolsProblemProperties}.
 *
 * @see AtCoderToolsProblemFacet
 */
public class AtCoderToolsProblemFacetEditorTab extends FacetEditorTab {

    @NotNull
    private final AtCoderToolsProblemProperties properties;
    private JPanel rootContainer;

    public AtCoderToolsProblemFacetEditorTab(@NotNull AtCoderToolsProblemProperties properties) {
        this.properties = properties;
    }

    @NotNull
    @Override
    public JComponent createComponent() {
        return rootContainer;
    }

    @Override
    public boolean isModified() {
        return false;
    }

    @Nls(capitalization = Nls.Capitalization.Title)
    @Override
    public String getDisplayName() {
        return "AtCoderTools Problem Properties";
    }
}
