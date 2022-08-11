import re
import sys
from enum import Enum

if len(sys.argv) == 1:
    sys.exit("Give input file as 1st argument and output file as 2nd argument")

input_file = sys.argv[1]
output_file = sys.argv[2]

class Status(Enum):
    Unknown = 1
    Finished = 2
    Unfinished = 3

def update_dictionary(word_dictionary, word, sentence_no):
    word_entry = word_dictionary.setdefault(word.lower(), [])
    word_entry.append(sentence_no)

# split line into sentences based on the pattern: any number of . or ! or ? followed by space followed by a capital letter
# the capital letter will not be excluded from the sentence
# named prefixed by Mr., Ms., Mrs., Dr., St. will be recognized as part of the sentence and not be split
# characters . ! and ? will remain in the sentence if found at the end of the line
# one . at the end of the line could mean end of sentence or abbrevation
def get_sentences_from_line(line):
    return re.split(r"(?<!Mr)(?<!Ms)(?<!Mrs)(?<!Dr)(?<!St) ?[?!.]+ (?=[A-Z])", line)

# words written with hyphen will be treated as separate words
def get_words_from_sentence(sentence):
    return re.findall(r"[A-Za-z'\.]+", sentence)

def get_sentence_status(line):
    if line[-1] == "!" or line[-1] == "?" or line[-2:] == "..":
        return Status.Finished
    elif line[-3:] in ["Mr.", "Ms.", "Dr.", "St."] or line[-4:] in ["Mrs."]:
        return Status.Unfinished
    elif line[-1] == ".":
        return Status.Unknown
    else:
        return Status.Unfinished

def update_dictionary_with_last_word(word_dictionary, last_word, last_sentence_status, line, sentence_no):
    # it is considered a new sentence if the last line ended with one . and this line starts with capital letter
    if last_sentence_status == Status.Unknown:
        if line[0].isupper():
            last_sentence_status = Status.Finished
        else:
            last_sentence_status = Status.Unfinished

    if last_sentence_status == Status.Unfinished:
        update_dictionary(word_dictionary, last_word, sentence_no)

    if last_sentence_status == Status.Finished:
        update_dictionary(word_dictionary, last_word.rstrip(".!?"), sentence_no)
        sentence_no += 1

    return sentence_no

def generate_word_dictionary(input_file):
    word_dictionary = {}

    try:
        with open(input_file, "rt") as f:
            sentence_no = 1
            last_sentence_status = ""
            last_word = ""

            for line in f:
                stripped_line = line.strip()
                
                sentence_no = update_dictionary_with_last_word(word_dictionary, last_word, last_sentence_status, stripped_line, sentence_no)
                last_word = ""

                sentences = get_sentences_from_line(stripped_line)
                last_sentence_status = get_sentence_status(stripped_line)
                
                no_of_sentences = len(sentences)
                for index in range(no_of_sentences):
                    sentence = sentences[index]
                    words = get_words_from_sentence(sentence)

                    if index == no_of_sentences - 1:
                        last_word = words.pop(-1)

                    for word in words:
                        update_dictionary(word_dictionary, word, sentence_no)

                    if index < no_of_sentences - 1:
                        sentence_no += 1

            update_dictionary(word_dictionary, last_word.rstrip(".!?"), sentence_no)

    except Exception as err:
        print(err)

    return word_dictionary

def get_index(index):
    a = 97
    z = 122
    chars = 26

    count = index // chars + 1
    letter = a + index % chars
    return chr(letter) * count + "."

def get_word_label(occurences):
    count = len(occurences)
    occurences_string = ",".join(str(o) for o in occurences)
    label = f"{{{count}:{occurences_string}}}"
    return label

def generate_concordance_file(word_dictionary):
    sorted_words = sorted(word_dictionary)

    try:
        with open(output_file, "wt") as f:
            for index, word in enumerate(sorted_words):
                index = get_index(index)
                word_label = get_word_label(word_dictionary.get(word))
                
                line = f"{index.ljust(8)} {word.ljust(18)} {word_label}\n"
                f.write(line)

    except Exception as err:
        print(err)

word_dictionary = generate_word_dictionary(input_file)
generate_concordance_file(word_dictionary)