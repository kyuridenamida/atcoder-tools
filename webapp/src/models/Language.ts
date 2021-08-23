
type Language = 'cpp' | 'rust' | 'java' | 'python' | 'd' | 'nim' | 'cs' | 'julia';
export const ALL_LANGUAGES : Language[] = ['cpp', 'rust', 'java', 'python', 'd', 'nim', 'cs', 'julia'];

export const langToDisplayName = (language: Language) => {
    switch (language){
        case 'cpp': return 'C++';
        case 'java': return 'Java';
        case 'rust': return 'Rust';
        case 'python': return 'Python 3';
        case 'd': return 'D';
        case 'nim': return 'Nim';
        case 'cs': return 'C#';
        case 'julia': return 'Julia';
    }
    throw Error(`no display name for ${language}`);
};

export default Language;
