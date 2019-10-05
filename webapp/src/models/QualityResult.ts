import Problem from './Problem'
import JudgeMethod from "./JudgeMethod";

export default interface QualityResult {
    problem: Problem,
    contest: {
        contest_id: string,
    },
    statement_parse: {
        error: string | null
    },
    format_prediction: {
        error: string | null
    },
    modulo: {
        value: number | null
        error: string | null
    },
    yes_str: {
        error: string | null
        value: string | null
    },
    no_str: {
        error: string | null
        value: string | null
    },
    judge_method: {
        error: string | null
        value: JudgeMethod | null
    },
    codes: {
        [lang: string] : string,
    }
}
