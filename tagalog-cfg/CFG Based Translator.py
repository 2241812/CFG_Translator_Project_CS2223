import re
import pandas as pd
import nltk
from nltk import CFG, ChartParser, Tree, Nonterminal, Production
import sys
import time
import json
import csv 
import os

def clear_console():
    """Clears the terminal console."""
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()

# --- Functions to load linguistic resources from files ---

def load_grammar(filepath):
    """Loads CFG rules from a .cfg file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            grammar_string = f.read()
        return CFG.fromstring(grammar_string)
    except FileNotFoundError:
        print(f"Error: Grammar file not found at '{filepath}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading grammar from '{filepath}': {e}")
        sys.exit(1)

def load_lexicon(filepath):
    """Loads lexicon definitions from a TSV file."""
    lexicon = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Assuming TSV format: POS\tword
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if row and len(row) == 2: # Ensure row has POS and word
                    pos, word = row
                    lexicon.append((pos, word))
                elif row:
                    print(f"Warning: Skipping malformed lexicon line: {row}")
            return lexicon
    except FileNotFoundError:
        print(f"Error: Lexicon file not found at '{filepath}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading lexicon from '{filepath}': {e}")
        sys.exit(1)

def load_dictionary(filepath):
    """Loads translation dictionary from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            translation_dict = json.load(f)
        return translation_dict
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at '{filepath}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON dictionary file '{filepath}': {e}")
        print("Please ensure the file is valid JSON format.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading dictionary from '{filepath}': {e}")
        sys.exit(1)


# ==========================================================

# ── A) LOAD CORPUS ─────────────────────────────────────────────────────────────

DATA_FILE = 'Appendix_A_Parallel_Corpus_Tagalog_English.tsv'
# ======================================================

try:
    df = pd.read_csv(
        DATA_FILE,
        sep='\t',
        header=None,
        names=['tgl_id', 'Tagalog Phrase/Sentence', 'eng_id', 'English Translation'] # Assign names
    )
    # ============================================================================

except FileNotFoundError:
    print(f"Error: File not found at '{DATA_FILE}'. Please check the filename and path.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"Error: The file '{DATA_FILE}' is empty.")
    sys.exit(1)
except pd.errors.ParserError as e:
    print(f"Error parsing '{DATA_FILE}': {e}")
    print("Please ensure it's a valid TSV file (Tab-separated) and check for inconsistencies.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred while reading the data file: {e}")
    sys.exit(1)

required_cols = ['Tagalog Phrase/Sentence', 'English Translation']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"Error: Could not find expected columns after loading: {missing_cols}")
    print(f"Columns actually loaded: {list(df.columns)}")
    print("There might be an issue with the file format or the 'names' provided in pd.read_csv.")
    sys.exit(1)


# ── B) TOKENIZE ────────────────────────────────────────────────────────────────
def tokenize_sentence(s): # Renamed to avoid conflict with df['tokens']
    if not isinstance(s, str): return []
    s = s.lower()
    return s.split()

df['tokens'] = df['Tagalog Phrase/Sentence'].apply(tokenize_sentence)

# ── C) & D) are now handled by loading external files ───────────────────────────

def simple_lexical_translate(tagalog_words, dictionary):
    """Performs word-by-word translation using a dictionary."""
    if not isinstance(tagalog_words, list): # Ensure input is a list
        return "[Error: Input not a list]"
    english_words = []
    for word in tagalog_words:
        translated = dictionary.get(str(word).lower(), f"[{word}]") # Ensure word is string
        if translated:
            english_words.append(translated)
    if not english_words:
        return "[N/A]"
    sentence = " ".join(english_words).replace(" ?", "?").replace(" .", ".").replace(" ,", ",").replace(" !", "!")
    if sentence:
        return sentence[0].upper() + sentence[1:]
    return sentence


# ── E) Load resources and Build list of Production objects ───────────────────

print("Loading linguistic resources...")
grammar_rules_cfg = load_grammar('Appendix_Methodology_Resource_Grammar_Tagalog_CFG.cfg')
lexicon_data = load_lexicon('Appendix_B_Resource_Lexicon_Tagalog_POS.tsv')
translation_dictionary = load_dictionary('Appendix_C_Resource_Dictionary_Tagalog_English.json')

print("Preparing grammar productions from loaded resources...")
structural_productions = grammar_rules_cfg.productions()
start_symbol = grammar_rules_cfg.start()

lexical_productions = []
words_in_lexicon = set()
processed_productions = set(structural_productions)

for pos_str, word in lexicon_data:
    lhs = Nonterminal(pos_str)
    rhs = [word]
    production = Production(lhs, rhs)
    if production not in processed_productions:
        lexical_productions.append(production)
        processed_productions.add(production)
        words_in_lexicon.add(word)

all_productions = structural_productions + lexical_productions

try:
    if 'tokens' in df.columns:
        all_toks = sorted(list(set(t for toks in df['tokens'] for t in toks if t)))
        added_as_default_N = 0
        for tok in all_toks:
            if tok not in words_in_lexicon:
                lhs = Nonterminal('N'); rhs = [tok]
                production = Production(lhs, rhs)
                if production not in processed_productions:
                    all_productions.append(production)
                    processed_productions.add(production)
                    added_as_default_N += 1
        print(f"Added {added_as_default_N} unique words automatically as Nouns.")
    else:
        print("Warning: 'tokens' column not found in DataFrame. Cannot check for unknown tokens.")
except NameError:
    print("Warning: 'df' (DataFrame) not available to check for unknown tokens.")
    print("Skipping automatic addition of unknown words as Nouns.")


print(f"Total unique productions in grammar: {len(all_productions)}")

# ── F) BUILD CFG & PARSER ─────────────────────────────────────────────────────

print("Building CFG directly from productions...")
start_time = time.time()
try:
    grammar = CFG(start_symbol, all_productions)
    parser = ChartParser(grammar)
except Exception as e:
    print(f"Error creating CFG or Parser: {e}")
    sys.exit(1)
end_time = time.time()
print(f"CFG and Parser built in {end_time - start_time:.4f} seconds.")


# ── G) VERIFY COVERAGE ────────────────────────────────────────────────────────

print("Verifying grammar coverage...")
try:
    all_terminals_in_grammar = set(prod.rhs()[0] for prod in grammar.productions() if prod.is_lexical())
    if 'tokens' in df.columns:
        all_toks_from_df = sorted(list(set(t for toks in df['tokens'] for t in toks if t)))
        missing_terminals = [tok for tok in all_toks_from_df if tok not in all_terminals_in_grammar]
        if missing_terminals:
            print(f"\nWarning: Grammar coverage issue. Missing terminals from corpus: {missing_terminals}\n")
        else:
            print("Grammar coverage check passed. All tokens from corpus seem to have lexical rules.")
    else:
        print("Warning: 'tokens' column not found in DataFrame. Cannot perform grammar coverage check against corpus.")

except Exception as e:
    print(f"Error during grammar coverage verification: {e}")


# ── H) PARSE-COVERAGE CHECK ───────────────────────────────────────────────────

print("Starting parsing for all sentences...")
parse_results = []
parse_times = []

if 'all_terminals_in_grammar' not in locals():
    all_terminals_in_grammar = set(prod.rhs()[0] for prod in grammar.productions() if prod.is_lexical())


for i, toks in enumerate(df['tokens']):
    if not toks: # Handle empty token lists
        parse_results.append(None)
        continue

    # Ensure all tokens are strings before checking presence in all_terminals_in_grammar
    current_tokens_str = [str(t) for t in toks if t is not None]
    if not current_tokens_str: # if after conversion all are None or list was empty
        parse_results.append(None)
        continue

    unknown_toks = [t for t in current_tokens_str if t not in all_terminals_in_grammar]
    if unknown_toks:
        # print(f"Skipping sentence due to unknown tokens: {unknown_toks} in {' '.join(current_tokens_str)}")
        parse_results.append(None)
        continue

    sent_start_time = time.time()
    try:
        parses = list(parser.parse(current_tokens_str))
        parse_results.append(parses[0] if parses else None)
    except ValueError as ve: # Catch specific NLTK parser error for words not in grammar
        # print(f"ValueError during parsing for tokens '{' '.join(current_tokens_str)}': {ve}")
        parse_results.append(None)
    except Exception as e:
        # print(f"General error during parsing for tokens '{' '.join(current_tokens_str)}': {e}")
        parse_results.append(None)
    sent_end_time = time.time()
    parse_times.append(sent_end_time - sent_start_time)

df['parse_tree'] = parse_results
df['parsed'] = df['parse_tree'].notna()

print("\n=== Parse coverage summary ===")
print(df['parsed'].value_counts(dropna=False))

unparsed_sentences_df = df[df['parsed'] == False]
if not unparsed_sentences_df.empty:
    print("\n--- Unparsed Sentences (first 10 examples) ---")
    for idx, row in unparsed_sentences_df.head(10).iterrows():
        print(f"Original: {row['Tagalog Phrase/Sentence']}")
        # print(f"Tokens: {row['tokens']}")
        # unknown_in_unparsed = [t for t in row['tokens'] if t not in all_terminals_in_grammar]
        # if unknown_in_unparsed:
        # print(f"Unknown tokens causing parse failure: {unknown_in_unparsed}")
    print("--------------------------")

if parse_times:
    avg_time = sum(parse_times) / len(parse_times) if len(parse_times) > 0 else 0
    print(f"Average parse time per attempted sentence: {avg_time:.4f} seconds")
else:
    print("No sentences were attempted for parsing (likely all had unknown tokens).")


# ── I) TREE-REWRITE TRANSLATION ───────────────────────────────────────────────

def rewrite(tree):
    if not isinstance(tree, Tree):
        return tree # Return terminals as is
    # Rule 1: VP NP -> NP VP (Verb-Subject to Subject-Verb)
    if tree.label() == "S" and len(tree) == 2:
        child1, child2 = tree
        if isinstance(child1, Tree) and child1.label() == "VP" and \
           isinstance(child2, Tree) and child2.label() == "NP":
            return Tree("S", [rewrite(child2), rewrite(child1)]) # Recursively rewrite children

    # Rule 2: NP AY VP -> NP VP (Remove AY inversion marker)
    if tree.label() == "S" and len(tree) == 3:
        child1, child2, child3 = tree
        # Check if child2 is 'AY' (terminal) or an AY Phrase
        is_ay_terminal = (not isinstance(child2, Tree) and str(child2).lower() == 'ay')
        is_ay_phrase = (isinstance(child2, Tree) and child2.label() == 'AY')

        if isinstance(child1, Tree) and child1.label() == "NP" and \
           is_ay_phrase and \
           isinstance(child3, Tree) and child3.label() == "VP":
            # AY phrase, we might want its children if it's not just the word 'ay'
            # For simplicity here, we assume AY is a simple marker and just take NP and VP
            return Tree("S", [rewrite(child1), rewrite(child3)])

    # Default: recursively process children and rebuild tree
    return Tree(tree.label(), [rewrite(child) for child in tree])


# ── J) APPLY REWRITE AND SHOW EXAMPLES ────────────────────────────────────────
df['rewritten_tree'] = df['parse_tree'].apply(lambda t: rewrite(t) if t and isinstance(t, Tree) else None)

print("\n=== Examples of Parsed Sentences (with Rewrites and Translations) ===")
# Displaying fewer examples on console as full output will be in CSV
parsed_examples_display = df[df['parsed']].head(10)

if parsed_examples_display.empty:
    print("\nNo sentences were successfully parsed based on the current grammar.")
    # ... (suggestions remain the same)
else:
    for index, row in parsed_examples_display.iterrows():
        original_sentence = row['Tagalog Phrase/Sentence']
        reference_english = row['English Translation']
        tokens = row['tokens']
        parsed_tree = row['parse_tree']
        rewritten_tree = row['rewritten_tree']

        print("-" * 40)
        print(f"Original Tagalog:   {original_sentence}")
        print(f"Tokens:             {' '.join(tokens) if tokens else 'N/A'}")
        print(f"Reference English:  {reference_english}")
        print("\nParsed Tagalog Tree:")
        if parsed_tree:
            parsed_tree.pretty_print(maxwidth=100) # Limit width for console
        else:
            print("  (No parse tree generated)")

        print("\nRewritten Tagalog Tree:")
        if rewritten_tree:
            rewritten_leaves = rewritten_tree.leaves()
            rewritten_tree.pretty_print(maxwidth=100) # Limit width
            print(f"\nRewritten Tagalog Text: {' '.join(rewritten_leaves)}")
            simple_translation = simple_lexical_translate(rewritten_leaves, translation_dictionary)
            print(f"Simple Lexical Tx:    {simple_translation}")
        else:
            print("  (Rewrite Error or No Rewrite Applicable)")

print("-" * 40)

# ── K) PREPARE AND WRITE ALL DATA TO CSV ───────────────────────────────────────
print("\nPreparing data for CSV output...")
csv_output_data = []

for index, row in df.iterrows():
    original_tagalog = row['Tagalog Phrase/Sentence']
    tokens_list = row['tokens'] if isinstance(row['tokens'], list) else []
    tokens_str = ' '.join(tokens_list)
    reference_english = row['English Translation']
    is_parsed = row['parsed']
    parse_tree_obj = row['parse_tree']
    rewritten_tree_obj = row['rewritten_tree']

    entry = {
        'Original Tagalog': original_tagalog,
        'Tokens': tokens_str,
        'Reference English': reference_english,
        'Parsed': is_parsed,
        'Parsed Tree (Compact)': "",
        'Parsed Tree (Pretty Single Line)': "",
        'Rewritten Tree (Compact)': "",
        'Rewritten Tree (Pretty Single Line)': "",
        'Rewritten Tagalog Text': "",
        'Simple Lexical Translation': ""
    }

    if is_parsed and parse_tree_obj:
        entry['Parsed Tree (Compact)'] = str(parse_tree_obj)
        entry['Parsed Tree (Pretty Single Line)'] = parse_tree_obj.pformat(nodesep='', parens='()', quotes=False).replace('\n', ' ').replace('  ', ' ')

        if rewritten_tree_obj:
            rewritten_leaves = rewritten_tree_obj.leaves()
            entry['Rewritten Tree (Compact)'] = str(rewritten_tree_obj)
            entry['Rewritten Tree (Pretty Single Line)'] = rewritten_tree_obj.pformat(nodesep='', parens='()', quotes=False).replace('\n', ' ').replace('  ', ' ')
            entry['Rewritten Tagalog Text'] = ' '.join(rewritten_leaves)
            entry['Simple Lexical Translation'] = simple_lexical_translate(rewritten_leaves, translation_dictionary)
        else:
            entry['Rewritten Tree (Compact)'] = "N/A (No rewrite)"
            entry['Rewritten Tree (Pretty Single Line)'] = "N/A (No rewrite)"
            entry['Rewritten Tagalog Text'] = "N/A (No rewrite)"
            # If parsed but not rewritten, translate from original parsed leaves
            entry['Simple Lexical Translation'] = simple_lexical_translate(parse_tree_obj.leaves(), translation_dictionary)
    else:
        entry['Parsed Tree (Compact)'] = "Not Parsed"
        entry['Parsed Tree (Pretty Single Line)'] = "Not Parsed"
        entry['Rewritten Tree (Compact)'] = "Not Parsed"
        entry['Rewritten Tree (Pretty Single Line)'] = "Not Parsed"
        entry['Rewritten Tagalog Text'] = "Not Parsed"
        # Attempt lexical translation on original tokens if not parsed
        if tokens_list: # only if tokens exist
             entry['Simple Lexical Translation'] = simple_lexical_translate(tokens_list, translation_dictionary)
        else:
            entry['Simple Lexical Translation'] = "[No tokens]"


    csv_output_data.append(entry)

output_csv_filename = 'translation_analysis_output.csv'
fieldnames = [
    'Original Tagalog', 'Tokens', 'Reference English', 'Parsed',
    'Parsed Tree (Compact)', 'Parsed Tree (Pretty Single Line)',
    'Rewritten Tree (Compact)', 'Rewritten Tree (Pretty Single Line)',
    'Rewritten Tagalog Text', 'Simple Lexical Translation'
]

print(f"\nWriting detailed output to {output_csv_filename}...")
try:
    with open(output_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_output_data)
    print(f"Successfully wrote output to {output_csv_filename}")
except IOError as e:
    print(f"Error writing CSV file '{output_csv_filename}': {e}")
except Exception as e:
    print(f"An unexpected error occurred during CSV writing: {e}")

print("\nScript finished.")