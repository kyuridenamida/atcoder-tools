package atcodertools.intellij.common.model

/**
 * Data class containing atcoder tools facet specific information. All fields in this data class will be
 * persisted as xml file.
 *
 * @see [atcodertools.intellij.facet.AtCoderToolsFacetConfiguration]
 */
data class AtCoderToolsProperties(
    var contestId: String = "",
    var isContentEnvGenerated: Boolean = false
)