const STOPWORDS = new Set([
    'the','and','for','that','with','from','this','have','were','their','would',
    'there','which','these','other','about','could','should','those','through',
    'because','between','without','within','during','before','after','above',
    'below','while','where','when','what','where','who','whom','why','how','many',
    'some','each','such','like','just','also','most','only','well','then','than',
    'your','youre','theyre','weve','youll','ill','isnt','arent','dont','doesnt',
    'cant','wont','shouldnt','couldnt'
]);

function normalizeText(text) {
    return text.replace(/\s+/g, ' ').trim();
}

function splitSentences(text) {
    return text
        .split(/(?<=[.!?])\s+(?=[A-Z])/)
        .map(sentence => sentence.trim())
        .filter(Boolean);
}

function extractKeywords(sentence) {
    const words = sentence.match(/\b[A-Za-z]{4,}\b/g) || [];
    return words.filter(word => !STOPWORDS.has(word.toLowerCase()));
}

function unique(array) {
    return [...new Set(array)];
}

function shuffle(array) {
    return array.slice().sort(() => Math.random() - 0.5);
}

function choose(array) {
    if (!array || array.length === 0) return null;
    return array[Math.floor(Math.random() * array.length)];
}

function buildOptions(correct, pool) {
    const choices = unique([correct, ...shuffle(pool).filter(item => item.toLowerCase() !== correct.toLowerCase())]).slice(0, 4);
    while (choices.length < 4) {
        choices.push(`Option ${choices.length + 1}`);
    }
    return shuffle(choices);
}

function createBlankSentence(sentence, keyword) {
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escaped}\\b`, 'i');
    return sentence.replace(regex, '____');
}

export function generateReviewerLocal(type, lesson, count) {
    const text = normalizeText(lesson || '');
    if (!text) {
        throw new Error('Please provide lesson text for Puter.js generation.');
    }

    const sentences = splitSentences(text);
    if (!sentences.length) {
        throw new Error('The lesson text could not be split into sentences.');
    }

    const allKeywords = unique(sentences.flatMap(extractKeywords));
    if (!allKeywords.length) {
        throw new Error('Unable to extract keywords from lesson text. Try a longer or clearer passage.');
    }

    const maxCount = Math.min(Math.max(1, count), 50);
    const questions = [];
    const answers = [];
    let candidateSentences = shuffle(sentences);

    for (let i = 0; i < maxCount && questions.length < maxCount && candidateSentences.length; i += 1) {
        const sentence = candidateSentences.shift();
        const keywords = extractKeywords(sentence);
        if (!keywords.length) continue;

        const keyword = choose(keywords);
        if (!keyword) continue;

        if (type === 'trueFalse') {
            const wrongWords = allKeywords.filter(k => k.toLowerCase() !== keyword.toLowerCase());
            const useFalse = wrongWords.length > 1 && Math.random() > 0.4;
            const questionText = useFalse
                ? `True or False: ${sentence.replace(new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')}\\b`, 'i'), choose(wrongWords))}`
                : `True or False: ${sentence}`;
            questions.push(`${questions.length + 1}. ${questionText}`);
            answers.push(`${answers.length + 1}. ${useFalse ? 'False' : 'True'}`);
            continue;
        }

        const blankSentence = createBlankSentence(sentence, keyword);
        const optionPool = allKeywords.filter(k => k.toLowerCase() !== keyword.toLowerCase()).slice(0, 20);
        const options = buildOptions(keyword, optionPool);
        const letterMap = ['A', 'B', 'C', 'D'];

        if (type === 'identification') {
            questions.push(`${questions.length + 1}. Identify the missing term:
${blankSentence}`);
            answers.push(`${answers.length + 1}. ${keyword}`);
            continue;
        }

        // Default to multiple choice
        const formattedOptions = options.map((option, index) => `${letterMap[index]}. ${option}`).join('\n');
        const correctIndex = options.findIndex(opt => opt.toLowerCase() === keyword.toLowerCase());
        const answerLetter = correctIndex >= 0 ? letterMap[correctIndex] : 'A';

        questions.push(`${questions.length + 1}. ${blankSentence}
${formattedOptions}`);
        answers.push(`${answers.length + 1}. ${answerLetter}`);
    }

    if (!questions.length) {
        throw new Error('Puter.js could not generate questions from the provided content.');
    }

    return {
        questions: questions.join('\n\n'),
        answers: answers.join('\n')
    };
}
