interface NormalJudge {
    "judge_type": "normal"
}

interface DecimalJudge {
    "judge_type": "decimal"
    error_type: "absolute_or_relative" | "relative" | "absolute",
    diff: number,
}

type JudgeMethod = NormalJudge | DecimalJudge;

export function judgeMethodToText(judgeMethod: JudgeMethod) {
    if (judgeMethod.judge_type === "normal") {
        return "Normal";
    }else{
        let displayName;
        if(judgeMethod.error_type === "absolute_or_relative"){
            displayName = "abs_or_rel";
        }else if(judgeMethod.error_type === "absolute"){
            displayName = "abs";
        }else if( judgeMethod.error_type === "relative"){
            displayName = "rel";
        }else{
            throw Error(`no display name for ${judgeMethod.error_type}`);
        }
        return `Decimal (${judgeMethod.diff.toExponential()}, ${displayName})`
    }
}

export default JudgeMethod;
