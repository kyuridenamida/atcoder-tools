package atcodertools.intellij.util

import com.google.common.io.Files
import com.google.gson.JsonParser
import com.intellij.openapi.vfs.VfsUtil
import com.intellij.openapi.vfs.VirtualFile
import java.nio.charset.StandardCharsets

/**
 * Represents metadata.json in AtCoderTools problem directory.
 */
data class ProblemMetadata(
    val name: String,
    val solutionSourceFileName: String
)

/**
 * Reads metadata.json in a given problem directory.
 */
fun getProblemMetadataForProblem(problemDir: VirtualFile): ProblemMetadata {
    val jsonFile = VfsUtil.virtualToIoFile(requireNotNull(problemDir.findChild("metadata.json")){
        "metadata.json file is missing"
    })
    val rootObject = JsonParser().parse(Files.asCharSource(jsonFile, StandardCharsets.UTF_8).read()).asJsonObject
    return ProblemMetadata(
        rootObject["problem"].asJsonObject["alphabet"].asString,
        rootObject["code_filename"].asString
    )
}
