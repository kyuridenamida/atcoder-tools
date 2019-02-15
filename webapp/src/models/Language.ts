
type Language = 'cpp' | 'rust' | 'java' | 'python';
export const ALL_LANGUAGES : Language[] = ['cpp', 'rust', 'java'];

export const langToDisplayName = (language: Language) => {
    switch (language){
        case 'cpp': return 'C++';
        case 'java': return 'Java';
        case 'rust': return 'Rust';
        case 'python': return 'Python 3';
    }
    throw Error(`no display name for ${language}`);
};

export default Language;
