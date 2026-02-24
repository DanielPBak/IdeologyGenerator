/**
 * JavaScript port of the Python Generator class from lambda_function.py.
 * Generates random political ideologies from CSV word lists.
 *
 * This module is designed to produce identical output to the Python original
 * when given the same CSV data and the same sequence of random numbers.
 */

class Generator {
    constructor(csvText) {
        this.csvText = csvText;
        this.trace = [];
        this.debugMode = false;

        // Word lists
        this.descAdjs = [];
        this.descAdjsWeights = [];
        this.descAdjsHaspWeights = [];
        this.descNouns = [];
        this.descNounsWeights = [];
        this.descNounsHaspWeights = [];
        this.prefixes = [];
        this.prefixWeights = [];
        this.prefixHaspWeights = [];
        this.nouns = [];
        this.nounsWeights = [];
        this.nounsHaspWeights = [];
        this.adverbs = [];
        this.adverbsWeights = [];
        this.endings = [];
        this.endingsWeights = [];

        this.allDescs = [];
        this.allDescsWeights = [];
        this.allDescsHaspWeights = [];
        this.rows = [];

        // Random function - can be overridden for testing
        this._random = Math.random;
    }

    /**
     * Parse CSV text following Python csv.reader behavior with \r\n line endings.
     * Returns array of arrays (rows of fields).
     */
    static parseCSV(text) {
        const rows = [];
        let i = 0;
        const len = text.length;

        while (i < len) {
            const row = [];
            // Parse one row
            while (i < len) {
                if (text[i] === '"') {
                    // Quoted field
                    i++; // skip opening quote
                    let field = '';
                    while (i < len) {
                        if (text[i] === '"') {
                            if (i + 1 < len && text[i + 1] === '"') {
                                // Escaped quote
                                field += '"';
                                i += 2;
                            } else {
                                // End of quoted field
                                i++; // skip closing quote
                                break;
                            }
                        } else {
                            field += text[i];
                            i++;
                        }
                    }
                    row.push(field);
                } else {
                    // Unquoted field
                    let field = '';
                    while (i < len && text[i] !== ',' && text[i] !== '\r' && text[i] !== '\n') {
                        field += text[i];
                        i++;
                    }
                    row.push(field);
                }

                if (i < len && text[i] === ',') {
                    i++; // skip comma, continue to next field
                } else {
                    // End of row
                    break;
                }
            }

            // Skip line endings (\r\n, \r, or \n)
            if (i < len && text[i] === '\r') i++;
            if (i < len && text[i] === '\n') i++;

            rows.push(row);
        }

        return rows;
    }

    /**
     * Python-compatible title case.
     * Python's str.title() capitalizes the first letter after any non-alpha character
     * and lowercases other letters.
     */
    static titleCase(s) {
        let result = '';
        let capitalizeNext = true;
        for (let i = 0; i < s.length; i++) {
            const ch = s[i];
            if (/[a-zA-Z]/.test(ch)) {
                if (capitalizeNext) {
                    result += ch.toUpperCase();
                    capitalizeNext = false;
                } else {
                    result += ch.toLowerCase();
                }
            } else {
                result += ch;
                capitalizeNext = true;
            }
        }
        return result;
    }

    /**
     * Parse the CSV and populate word lists.
     * Mirrors Python Generator.get_words().
     */
    getWords() {
        const csvRows = Generator.parseCSV(this.csvText);
        let first = true;

        for (const row of csvRows) {
            this.rows.push(row);

            if (first) {
                first = false;
                continue;
            }

            if (row[0] === '') {
                continue;
            }

            // The first column may itself contain commas, which were already parsed
            // by the CSV parser. But in the Python code, row[0] is the first CSV field,
            // and then it splits by comma again. Since the Google Sheets CSV quotes fields
            // containing commas, the Python code splits the already-parsed field on commas.
            let wordsRaw = row[0];
            let words = wordsRaw.split(',');
            words = words.map(word => {
                word = word.replace(/;/g, ',');
                word = word.replace(/'/g, 'abcdefgh');
                word = Generator.titleCase(word);
                word = word.replace(/abcdefgh/g, "'");
                return word;
            });

            const type = row[1];

            let weight;
            if (row[2] === '') {
                weight = 1;
            } else {
                weight = parseFloat(row[2]);
            }

            let haspWeight;
            if (row[3] === '') {
                haspWeight = 1;
            } else {
                haspWeight = parseFloat(row[3]);
            }

            if (type === 'DESCADJ') {
                this.descAdjs.push(words);
                this.descAdjsWeights.push(weight);
                this.descAdjsHaspWeights.push(haspWeight);
            } else if (type === 'DESCNOUN') {
                this.descNouns.push(words);
                this.descNounsWeights.push(weight);
                this.descNounsHaspWeights.push(haspWeight);
            } else if (type === 'PREFIX') {
                this.prefixes.push(words);
                this.prefixWeights.push(weight);
                this.prefixHaspWeights.push(haspWeight);
            } else if (type === 'ENDING') {
                this.endings.push(words);
                this.endingsWeights.push(weight);
            } else if (type === 'NOUN') {
                this.nouns.push(words);
                this.nounsWeights.push(weight);
                this.nounsHaspWeights.push(haspWeight);
            } else if (type === 'ADVERB') {
                this.adverbs.push(words);
                this.adverbsWeights.push(weight);
            } else {
                throw new Error('Unknown type: ' + type);
            }
        }

        this.allDescs = this.descAdjs.concat(this.descNouns);
        this.allDescsWeights = this.descAdjsWeights.concat(this.descNounsWeights);
        this.allDescsHaspWeights = this.descAdjsHaspWeights.concat(this.descNounsHaspWeights);
    }

    /**
     * Weighted random choice. Returns index into the weights array.
     * Mirrors Python Generator.weighted_choice().
     */
    weightedChoice(weights) {
        const totals = [];
        let runningTotal = 0;

        for (const w of weights) {
            runningTotal += w;
            totals.push(runningTotal);
        }

        const rnd = this._random() * runningTotal;
        for (let i = 0; i < totals.length; i++) {
            if (rnd < totals[i]) {
                return i;
            }
        }
        // Should not reach here, but return last index as fallback
        // (matches Python behavior when rnd === runningTotal exactly)
        return totals.length - 1;
    }

    /**
     * Pick a random element from an array.
     * Mirrors Python random.choice().
     */
    _choice(arr) {
        const idx = Math.floor(this._random() * arr.length);
        return arr[idx];
    }

    /**
     * Generate n ideologies. Returns [ideologies, traces].
     * Mirrors Python Generator.get_ideologies().
     */
    getIdeologies(nIdeologies = 100) {
        const ideologies = [];
        const traces = [];

        for (let i = 0; i < nIdeologies; i++) {
            this.trace = [];
            ideologies.push(this.generateIdeology());
            traces.push(this.trace);
        }
        return [ideologies, traces];
    }

    /**
     * Generate a noun phrase, possibly with prefix, adjective, and double-barrel.
     * Mirrors Python Generator.get_noun().
     */
    getNoun(pAdj = 0.5, pPrefix = 0.5, pDouble = 0.25, isDouble = false) {
        this.trace.push('Noun');
        let noun = this._choice(this.nouns[this.weightedChoice(this.nounsWeights)]);

        if (this.debugMode) {
            noun = 'noun';
        }
        const hasDouble = this._random() < pDouble;

        // If we have a double, lower the odds of prefixes and adjs.
        if (hasDouble) {
            pPrefix = pPrefix / 2;
            pAdj = pAdj / 2;
        }

        const hasPrefix = this._random() < pPrefix;
        const hasAdj = this._random() < pAdj;
        const newPPrefix = Math.min(pPrefix * pPrefix, pPrefix * 0.25);
        const newPAdj = Math.min(pAdj * pAdj, pAdj * 0.25);

        if (hasPrefix) {
            let prefixPHyphen;
            if (isDouble) {
                prefixPHyphen = 0;
            } else {
                prefixPHyphen = 0.25;
            }
            const prefix = this.getPrefix(newPPrefix, prefixPHyphen);
            noun = prefix + noun;
        }

        if (hasAdj) {
            noun = this.getDesc(newPAdj, newPPrefix) + ' ' + noun;
        }

        if (hasDouble) {
            noun = noun + '-' + this.getNoun(0, 0.25, 0, true);
        }

        return noun;
    }

    /**
     * Generate a descriptor (adjective or descriptor noun).
     * Mirrors Python Generator.get_desc().
     */
    getDesc(pPrefix = 0.5, pAdj = 0.33, pDouble = 0.4, pAdverb = 0.2) {
        const newPPrefix = Math.min(pPrefix * pPrefix, pPrefix * 0.33);
        const newPAdj = Math.min(pAdj * pAdj, pAdj * 0.33);

        this.trace.push('Desc');
        const descIdx = this.weightedChoice(this.allDescsWeights);

        const adjs = this.allDescs[descIdx];

        let addAdverb = false;
        let isDescAdj;
        if (this.descAdjs.indexOf(adjs) !== -1) {
            isDescAdj = true;
        } else {
            isDescAdj = false;
        }

        if (isDescAdj && this._random() < pAdverb) {
            addAdverb = true;
        }

        let adj = this._choice(adjs);

        const prefixWeight = this.allDescsHaspWeights[descIdx];

        adj = adj.replace('{Adj1}', '{adj1}');
        adj = adj.replace('{Adj2}', '{adj2}');
        adj = adj.replace('{Adj}', '{adj}');
        adj = adj.replace('{Noun}', '{noun}');

        if (adj.includes('{adj1}') || adj.includes('{adj2}')) {
            // Python: self.get_desc(p_adj=new_p_adj, p_prefix=new_p_prefix, p_double=0)
            const adj1Val = this.getDesc(newPPrefix, newPAdj, 0);
            const adj2Val = this.getDesc(newPPrefix, newPAdj, 0);
            adj = adj.replace('{adj1}', adj1Val).replace('{adj2}', adj2Val);
            return adj;
        }

        if (this.debugMode) {
            adj = 'adj';
        }

        if (isDescAdj && this._random() < pDouble) {
            // Python: self.get_desc(p_adj=0, p_double=0, p_prefix=0.1, p_adverb=0)
            adj = adj + '-' + this.getDesc(0.1, 0, 0, 0);
        }

        if (this._random() < pPrefix * prefixWeight) {
            adj = this.getPrefix(newPPrefix) + adj;
        }

        if (addAdverb) {
            adj = this.getAdverb() + ' ' + adj;
        }

        if (this._random() < pAdj) {
            adj = this.getDesc(newPPrefix, newPAdj) + ' ' + adj;
        }

        return adj;
    }

    /**
     * Generate a prefix string, possibly recursive.
     * Mirrors Python Generator.get_prefix().
     */
    getPrefix(pPrefix = 0.15, pHyphen = 0.5) {
        this.trace.push('prefix');
        const newPPrefix = Math.min(pPrefix * pPrefix, pPrefix * 0.33);

        const prefixIdx = this.weightedChoice(this.prefixWeights);
        const prefixWeight = this.prefixHaspWeights[prefixIdx];

        let pref = this._choice(this.prefixes[prefixIdx]);

        if (this.debugMode) {
            pref = 'pref';
        }

        let pNextHyphen;
        if (pref.endsWith('-')) {
            pNextHyphen = 1;
        } else {
            if (this._random() < pHyphen) {
                pref = pref + '-';
                pNextHyphen = pHyphen;
            } else {
                pNextHyphen = 1;
            }
        }

        if (this._random() < pPrefix * prefixWeight) {
            pref = this.getPrefix(newPPrefix, pNextHyphen) + pref;
        }

        return pref;
    }

    /**
     * Generate an ending clause.
     * Mirrors Python Generator.get_ending().
     */
    getEnding() {
        this.trace.push('ending');
        let ending = this._choice(this.endings[this.weightedChoice(this.endingsWeights)]);

        ending = ending.replace('{Adj}', '{adj}');
        ending = ending.replace('{Noun}', '{noun}');

        const desc = this.getDesc(0.2, 0.1, 0.2);
        const noun = this.getNoun(0.1, 0.2, 0.2);

        ending = ending.replace('{adj}', desc).replace('{noun}', noun);

        return ending;
    }

    /**
     * Generate an adverb.
     * Mirrors Python Generator.get_adverb().
     */
    getAdverb() {
        this.trace.push('adverb');
        let adverb = this._choice(this.adverbs[this.weightedChoice(this.adverbsWeights)]);

        if (this.debugMode) {
            adverb = 'adverb';
        }
        return adverb;
    }

    /**
     * Generate a single ideology string.
     * Mirrors Python Generator.generate_ideology().
     */
    generateIdeology(pEnding = 0.33, pStart = 0.5) {
        const forcePrefix = this._choice([false, true]);
        const withEnding = this._random() < pEnding;

        let pPrefix, pAdj;
        if (forcePrefix) {
            pPrefix = 1;
            pAdj = 0.75;
        } else {
            pPrefix = 0.75;
            pAdj = 1;
        }

        const noun = this.getNoun(pPrefix, pAdj);

        let ideo = noun;

        if (withEnding) {
            let ending = this.getEnding();
            ending = ending.trim();

            if (ending.startsWith(',')) {
                // ending stays as-is
            } else {
                ending = ' ' + ending;
            }

            ideo = ideo + ending;
        }

        return ideo;
    }
}

// Export for Node.js usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Generator };
}
