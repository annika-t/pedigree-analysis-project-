
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

#
def create_family_tree(person_id, num_siblings, parents, family_tree, generation=0):
    # Check if the person already exists in the tree
    if person_id not in family_tree:
        # Initialize the person's data
        family_tree[person_id] = {
            "generation": generation,
            "siblings": set(),
            "parents": [],
            "spouse": None
        }
    
    # Add siblings based on num_siblings count
    siblings = []
    for i in range(num_siblings):
        sibling_id = person_id + i + 1
        if sibling_id not in family_tree:
            create_family_tree(sibling_id, 0, [], family_tree, generation)
        siblings.append(sibling_id)
        family_tree[person_id]["siblings"].add(sibling_id)
        family_tree[sibling_id]["siblings"].add(person_id)

    # Add parents if provided
    if parents:
        parent1, parent2 = parents
        if parent1 not in family_tree:
            # Recursively add each parent and establish spousal relationship
            create_family_tree(parent1, 0, [], family_tree, generation + 1)
        if parent2 not in family_tree:
            create_family_tree(parent2, 0, [], family_tree, generation + 1)
        
        # Link the parents as spouses and set them as the person's parents
        family_tree[parent1]["spouse"] = parent2
        family_tree[parent2]["spouse"] = parent1
        family_tree[person_id]["parents"] = [parent1, parent2]
        
        # Assign siblings' parents to the same parents
        for sibling_id in siblings:
            family_tree[sibling_id]["parents"] = [parent1, parent2]
    
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
