package atcodertools.intellij.model

/**
 * Data class containing atcoder tools problem facet specific information. All fields in this data class will be
 * persisted as xml file.
 *
 * @see [atcodertools.intellij.facet.AtCoderToolsProblemFacetConfiguration]
 */
data class AtCoderToolsProblemProperties(
    var problemName: String = "",
    var systemTestResult: SystemTestResult = SystemTestResult.NOT_SUBMITTED
)

/**
 * Represents a result of a submission.
 */
enum class SystemTestResult {
    NOT_SUBMITTED,
    WRONG_ANSWER,  // Not in use yet.
    ACCEPTED  // Not in use yet.
}