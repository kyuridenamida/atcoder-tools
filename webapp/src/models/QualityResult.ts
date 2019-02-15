import Problem from './Problem'

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
    codes: {
        [lang: string] : string,
    }
}
