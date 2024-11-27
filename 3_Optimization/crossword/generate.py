import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        iterable = copy.deepcopy(self.domains)
        for var in iterable:
            for pot_word in iterable[var]:
                if len(pot_word) > var.length or len(pot_word) < var.length:
                    self.domains[var].remove(pot_word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        iterableX = copy.deepcopy(self.domains[x])
        Change= False
        empty_domain = False

        if overlap:
            overlapX, overlapY = overlap
            for wordX in iterableX:
                match_found = False
                for wordY in self.domains[y]:
                    # error handling to avoid index problems
                    if overlapY > (len(wordY)-1) or overlapX > (len(wordX)-1):
                        continue
                    # if a match has been found, this wordX cannot be deleted from the domain.
                    if wordX[overlapX] == wordY[overlapY]:
                        match_found= True
                        break
                # If a no match has been found this word will be deleted
                if not match_found:
                    self.domains[x].remove(wordX)
                    Change = True

        return Change



    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = arcs
        if arcs is None:
            queue = []
            for variables in self.crossword.overlaps:
                if self.crossword.overlaps[variables]:
                        queue.append((variables))

        while queue:
                var1, var2 = queue.pop(0)
                if self.revise(var1,var2):
                    if not self.domains[var1]:
                        return False
                    for neighbor in self.crossword.neighbors(var1):
                        if (neighbor,var1) not in queue:
                            queue.append((neighbor,var1))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if assignment.get(var) == None:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # create a copy through which can be iterated.
        checked_duplicate = set()
        for var1 in assignment:
            # check if length is consistent
            if var1.length != len(assignment[var1]):
                return False
            # check if the domain has dublicates by checking it with a group that has already been checked
            if assignment[var1] in checked_duplicate:
                return False
            checked_duplicate.add(assignment[var1])

            # check if there are any conflict with neigbouring cells.
            for var2 in assignment:
                if var1 == var2:
                    continue
                overlap = self.crossword.overlaps[var1,var2]
                if overlap:
                    overlap1, overlap2 = overlap
                    if assignment[var1][overlap1] != assignment[var2][overlap2]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        neighbors_set= self.crossword.neighbors(var)
        total_constraint = dict()
        for assigned in assignment:
            if assigned in neighbors_set:
                neighbors_set.remove(assigned)

        total_constraint = dict()
        for word1 in self.domains[var]:
            exlusion = 0
            for neighbor in neighbors_set:
                overlap1, overlap2 = self.crossword.overlaps[var, neighbor]
                for word2 in self.domains[neighbor]:
                    if word1[overlap1] != word2[overlap2]:
                        exlusion += 1
            total_constraint[word1]= exlusion

        sorted_list = sorted(total_constraint, key = lambda k: total_constraint[k])

        return sorted_list


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        remember = (None, 10000)
        for variable in self.domains:
            if variable in assignment:
                continue
            num_of_words = len(self.domains[variable])
            if num_of_words < remember[1]:
                remember = (variable, num_of_words)
                continue
            elif num_of_words == 2:
                if len(self.crossword.neighbors(variable)) > len(self.crossword.neighbors(remember[0])):
                    remember = (variable, num_of_words)

        return remember[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        dummy = assignment.copy()
        if not self.consistent(assignment):
            return None

        if self.assignment_complete(assignment):
                return assignment



        selection = self.select_unassigned_variable(assignment)
        order_check = self.order_domain_values(selection, assignment)

        for word in order_check:
            dummy[selection] = word
            result = self.backtrack(dummy)
            if result:
                return result

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
