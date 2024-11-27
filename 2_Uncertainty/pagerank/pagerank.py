import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    print(corpus)
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    randomtopage = (1-damping_factor)/len(corpus)
    transitionmodel = dict()
    if page in corpus:
        if corpus[page] == set():
            pagetopage = damping_factor/len(corpus)
        else:
            pagetopage = damping_factor/len(corpus[page])
    else:
        print(page)
        raise ValueError(f"Page '{page}' not found in corpus")

    for current_page in corpus:
        if corpus[page] == set():
            transitionmodel[current_page] = pagetopage + randomtopage
            continue
        elif current_page not in corpus[page]:
            transitionmodel[current_page] = randomtopage
            continue
        transitionmodel[current_page] = pagetopage + randomtopage

    return transitionmodel


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # get random start value
    state = random.choice(list(corpus.keys()))
    pagerank = {key: 0 for key in corpus}

# copied from the cs50 duck
    def next_state(corpus, current_state, damping_factor):
        model = transition_model(corpus, current_state, damping_factor)
        rand = random.random()
        cumulative_prob = 0.0
        for state, prob in model.items():
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return state

    for _ in range(n-1):
        if state in pagerank:
            pagerank[state] += 1
        else:
            # Handle the case where state is not a valid key
            print(f"Invalid state: {state}")

        state = next_state(corpus, state, damping_factor)

    total_samples = sum(pagerank.values())
    for page in pagerank:
        pagerank[page] = pagerank[page]/total_samples

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # start PageRank
    pagerank = {key: 1/len(corpus) for key in corpus}
    N = len(corpus)
    buffer_rank = pagerank.copy()
    while True:
        for page in pagerank:
            sumofpages = 0
            for pagecheck in corpus:
                if not corpus[pagecheck]:
                    sumofpages += pagerank[pagecheck]/len(corpus)
                elif page in corpus[pagecheck]:
                    sumofpages += pagerank[pagecheck] / len(corpus[pagecheck])
            rank = ((1-damping_factor)/N) + (damping_factor * sumofpages)
            buffer_rank[page] = rank

        flag = 0
        for page in pagerank:
            accuracy = buffer_rank[page] - pagerank[page]
            if accuracy > 0.001 or accuracy < -0.001:
                flag += 1
                break

        pagerank = buffer_rank.copy()

        if flag == 0:
            return pagerank


if __name__ == "__main__":
    main()
