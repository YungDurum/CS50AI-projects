import sys
import nltk
nltk.download('punkt_tab')

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> PP NP VP | NP VP | NP VP PP | NP VP PP Conj VP | NP VP Conj VP | PP NP VP Conj VP| NP PP NP | NP VP PP Conj NP VP | NP VP Conj NP VP PP | NP VP PP Conj NP VP PP | NP VP PP Conj VP PP
PP -> P NP | P | P NP | P NP Adv
NP -> N | Det N | Det Adj N | Det Adj Adj N | Det Adj Adj Adj N
VP -> V | V NP | Adv V NP | Adv V | V Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Convert to lowercase
    lower_sentence = sentence.lower()

    token_list = nltk.tokenize.word_tokenize(lower_sentence)
    for word in token_list[:]:
        if not word.isalnum():
            token_list.remove(word)
            continue
        if word.isdigit():
            token_list.remove(word)

    return token_list


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    Test = tree.fromstring("(NP blablabla)")
    chunks = list()

    for chunkies in (tree.subtrees(lambda t: t.label() == "NP")):
        if (len(list(chunkies.subtrees(lambda t: t.label() == "NP")))) == 1:
            chunks.append(chunkies)
    return chunks


if __name__ == "__main__":
    main()
