import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    print(people)
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)

    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1
    for person in people:
        if person in one_gene:
            # check father
            if people[person]["father"] and people[person]["mother"]:
                # probability of father giving gene
                # father has two genes
                if people[person]["father"] in two_genes:
                    prob_father = 0.99
                # father has one gene
                elif people[person]["father"] in one_gene:
                    prob_father = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                # father has zero genes
                else:
                    prob_father = 1 * PROBS["mutation"]
            # check mother (same method as father)
                if people[person]["mother"] in two_genes:
                    prob_mother = 0.99
                elif people[person]["mother"] in one_gene:
                    prob_mother = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                else:
                    prob_mother = 1 * PROBS["mutation"]

            # inclusion-exclusion for getting one gene from father and mother ( you exclude the times that both are true and since there have also been counted double it is times two)
                probability = probability * (prob_mother + prob_father -
                                             2*(prob_mother * prob_father))
            else:
                probability = probability * PROBS["gene"][1]

            # check if person has trait or not
            if person in have_trait:
                probability = probability * PROBS["trait"][1][True]
            else:
                probability = probability * PROBS["trait"][1][False]

        elif person in two_genes:
            if people[person]["father"] and people[person]["mother"]:
                # probability of father giving gene
                # two genes
                if people[person]["father"] in two_genes:
                    prob_father = 0.99
                # one gene
                elif people[person]["father"] in one_gene:
                    prob_father = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                # zero genes
                else:
                    prob_father = PROBS["mutation"]
            # check mother (same as father)
                if people[person]["mother"] in two_genes:
                    prob_mother = 0.99
                elif people[person]["mother"] in one_gene:
                    prob_mother = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                else:
                    prob_mother = PROBS["mutation"]

                probability = probability * prob_mother * prob_father

            else:
                probability = probability * PROBS["gene"][2]

            if person in have_trait:
                probability = probability * PROBS["trait"][2][True]
            elif not person in have_trait:
                probability = probability * PROBS["trait"][2][False]

        # person has zero genes
        else:
            if people[person]["father"] and people[person]["mother"]:
                # probability of father giving gene
                # father has two genes
                if people[person]["father"] in two_genes:
                    prob_father = PROBS["mutation"]
                # father has one gene
                elif people[person]["father"] in one_gene:
                    prob_father = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                # father has zero genes
                else:
                    prob_father = 1 - PROBS["mutation"]
            # check mother (same method as father)
                if people[person]["mother"] in two_genes:
                    prob_mother = PROBS["mutation"]
                elif people[person]["mother"] in one_gene:
                    prob_mother = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                else:
                    prob_mother = 1 - PROBS["mutation"]

                probability = probability * prob_mother * prob_father

            # If person has no father and mother
            else:
                probability = probability * PROBS["gene"][0]

            if person in have_trait:
                probability = probability * PROBS["trait"][0][True]
            else:
                probability = probability * PROBS["trait"][0][False]

    # print("Probability of person is", probability)

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # We iterate through each person and update the corresponding gene and trait he is in.
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:
        # sum of the gene
        sum_gene = sum(probabilities[person]["gene"].values())
        sum_trait = sum(probabilities[person]["trait"].values())
        for gene in probabilities[person]["gene"]:
            # to normalize we update each gene with the value of sum of the individual genes
            probabilities[person]["gene"][gene] = probabilities[person]["gene"][gene]/sum_gene

        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] = probabilities[person]["trait"][trait]/sum_trait


if __name__ == "__main__":
    main()
