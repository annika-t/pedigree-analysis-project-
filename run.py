
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

#
gen_count = input("number of generations: ")
gen_last_count = input("number of people in generation 3: ")

def create_family_tree(gen_count, gen_last_count):
    family_tree = []
    current_id = 1
    
    # Calculate the number of people in each generation, starting from the last generation
    gen_sizes = [gen_last_count]
    for _ in range(gen_count - 1):
        # Ensure each previous generation has enough people to be parents of the next generation
        gen_sizes.insert(0, (gen_sizes[0] + 1) // 2)
    
    # Generate unique IDs for each generation
    for size in gen_sizes:
        generation = [current_id + i for i in range(size)]
        family_tree.append(generation)
        current_id += size
    
    return family_tree

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class Char:
    def __init__(self, char,):
        self.char = char

    def _prop_name(self):
        return f"A.{self.char}"


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"

# Call your variables whatever you want
g = Char("Generation")
f = Char("Female")   
a = Char("Affected")
r = Char("Blood Relative")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
