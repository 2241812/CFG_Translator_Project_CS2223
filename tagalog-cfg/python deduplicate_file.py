import os

def remove_duplicate_lines(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return

    unique_lines = []
    seen_lines = set()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                cleaned_line = line.strip()
                if cleaned_line not in seen_lines:
                    unique_lines.append(line)
                    seen_lines.add(cleaned_line)

        with open(filepath, 'w', encoding='utf-8') as f:
            for line in unique_lines:
                f.write(line)

        print(f"Successfully removed duplicate lines from '{filepath}'.")

    except IOError as e:
        print(f"Error accessing file '{filepath}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


remove_duplicate_lines('tagalog_grammar.cfg')
remove_duplicate_lines('tagalog_lexicon.tsv')
remove_duplicate_lines('Sentence pairs in Tagalog-English.tsv')
# remove_duplicate_lines('Sentence pairs in Tagalog-English.tsv')
