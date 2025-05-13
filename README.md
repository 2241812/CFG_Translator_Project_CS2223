# CFG_Translator_Project_CS2223

## A Context-Free Grammar-Based Approach to Natural Language Machine Translation Using Python

This repository contains the code and resources for a research project exploring the efficacy of using Context-Free Grammar (CFG) for building a simple machine translation system between English and Tagalog.

The project was developed as a partial fulfillment of the requirements for the course Formal Languages and Automata (CS223) at Saint Louis University, Baguio City, Philippines.

## Project Overview

The primary goal of this project is to investigate the application of CFG rules in processing natural language for translation. The system is designed to parse simple sentences in one language (Tagalog or English) based on predefined CFG rules and perform a word-by-word lexical translation using a custom dictionary.

The research evaluates the effectiveness of the CFG in parsing sentence structures and assesses the quality of the resulting translations, highlighting the strengths and limitations of a pure CFG-based approach for natural language translation.

## Methodology

The translation system was built using Python and leverages the Natural Language Toolkit (NLTK) library for parsing. The core components include:

* **Context-Free Grammar (CFG) Rules:** Defined in `.cfg` files to specify the grammatical structure of simple sentences.
* **Lexicon:** Provides a list of words and their parts of speech.
* **Translation Dictionary:** Contains word-level translations between Tagalog and English.
* **Parallel Corpus:** A dataset of simple English and Tagalog sentence pairs used for testing and development.
* **Python Scripts:** For loading resources, parsing, translation, and data cleaning.

The process involves tokenizing input sentences, parsing them using the CFG and lexicon, applying simple rewrite rules (if applicable), and performing lexical substitution based on the dictionary.

## Getting Started

### Prerequisites

* Python 3.x
* NLTK library (`pip install nltk`)
* pandas library (`pip install pandas`)

### Installation

1.  Clone this repository to your local machine or download the files directly.
2.  Ensure all the project files from the repository are in the same directory or that the script paths are correctly configured.

### Running the Code

1.  Open your terminal or command prompt.
2.  Navigate to the project directory (`TAGALOG-CFG`).
3.  Run the main Python script:
    ```bash
    python "CFG Based Translator.py"
    ```
4.  The script will load the linguistic resources from the `Appendix_` files, attempt to parse and translate the sentences from the specified corpus file, and log the analysis output to `translation_analysis_output.csv`.

## Files in this Repository

* `CFG Based Translator.py`: The main program script that orchestrates the translation process.
* `grammar_resources.py`: May contain definitions or functions related to the grammar rules (although the main script loads the grammar from a `.cfg` file).
* `python deduplicate_file.py`: A utility script used for removing duplicate entries from data files.
* `python jsoncleaner.py`: A utility script specifically for cleaning duplicate key-value pairs in the JSON dictionary file.
* `Appendix_A_Parallel_Corpus_Tagalog_English.tsv`: The parallel corpus file containing sentence pairs used as input data.
* `Appendix_B_Resource_Lexicon_Tagalog_POS.tsv`: The lexicon file mapping Tagalog words to their parts of speech.
* `Appendix_C_Resource_Dictionary_Tagalog_English.json`: The dictionary file containing Tagalog to English word translations.
* `Appendix_Methodology_Resource_Grammar_Tagalog_CFG.cfg`: The Context-Free Grammar rules file used by the parser.
* `Sentence pairs in Tagalog-English (UNREDU...)`: Likely a raw or unreduced version of the parallel corpus.
* `Sentence pairs in Tagalog-English.tsv`: Another version of the parallel corpus file.
* `tagalog_english_dict.json`: An alternative or source version of the translation dictionary.
* `tagalog_grammar.cfg`: An alternative or source version of the grammar rules file.
* `tagalog_lexicon.tsv`: An alternative or source version of the Tagalog lexicon.
* `translation_analysis_output.csv`: The output file generated after running `CFG Based Translator.py`, containing the analysis of the translation results.
* `README.md`: This file.
* `__pycache__`: (Typically ignored in Git) A directory created by Python to cache compiled bytecode files.
* `Sentences`: A directory which might contain individual sentence files or related data, not directly loaded by the main script based on the provided code snippet.

## Results and Limitations

The project demonstrated that CFG is effective in parsing the syntactic structure of simple sentences. However, the simple lexical translation method, without advanced transfer rules, resulted in unnatural wording, untranslated grammatical particles, and word order issues for more complex structures. The limitations highlight the inherent complexity of natural language that cannot be fully captured by CFG alone with a basic translation approach.

## Future Directions

Potential future work includes:

* Expanding the CFG rules and lexicon to cover a wider range of grammatical structures and vocabulary.
* Developing more sophisticated transfer rules for better word reordering and handling of grammatical particles.
* Implementing mechanisms for word sense disambiguation to improve translation accuracy for ambiguous terms.
* Exploring hybrid approaches combining rule-based methods with statistical or neural machine translation techniques.

## Presented By

* Bag-eo, Jim Hendrix
* Cardenas, Aaron Miguel M.
* Menos, Brent Bona
* Narciso, Javier
* Sibayan, Erick James
* Vigilia, Paul Gabriel A.

## Presented To

* Dalos "Dale" D. Miguel

## Institution

Saint Louis University, Baguio City, Philippines

## Course

Formal Languages and Automata (CS223)

## Date

May 2025
