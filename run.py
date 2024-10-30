
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()
PEDIGREE={} 
#immediate family (siblings+parents)
IFAMILY={
    "parents":[],
    "siblings":[]
}
PERSON={
    "id",
    "char"=[]
} #id, chars
CHARACTERISTIC=[] #characteristics a person have (affected or not, geneder, blood relation,generation) 
#
def create_person(id, gen, gender, affected, br):
    char=[gender, affected, br]
    PERSON={
        "id":id,
        "gen"=gen,
        "gender"=char[0],
        "affected"=char[1],
        "br"=char[2]
    }
def create_ifam(person1, person2, person3=None):
    if person3 is None:
        # Case with 2 arguments: Add both to siblings if not already in list
        if person1 not in IFAMILY["siblings"]:
            IFAMILY["siblings"].append(person1)
        if person2 not in IFAMILY["siblings"]:
            IFAMILY["siblings"].append(person2)
    else:
        # Case with 3 arguments: Add first to siblings, second and third to parents
        if person1 not in IFAMILY["siblings"]:
            IFAMILY["siblings"].append(person1)
        if person2 not in IFAMILY["parents"]:
            IFAMILY["parents"].append(person2)
        if person3 not in IFAMILY["parents"]:
            IFAMILY["parents"].append(person3)
    
def create_pedigree(person_id, num_siblings, parents, family_tree, generation=0):
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
        parent1_id, parent2_id = parents
        if parent1 not in family_tree:
            # Recursively add each parent and establish spousal relationship
            create_family_tree(parent1, 0, [], family_tree, generation + 1)
        if parent2 not in family_tree:
            create_family_tree(parent2, 0, [], family_tree, generation + 1)
        
        # Link the parents as spouses and set them as the person's parents
        family_tree[parent1_id]["spouse"] = parent2
        family_tree[parent2_id]["spouse"] = parent1
        family_tree[person_id]["parents"] = [parent1, parent2]
        
        # Assign siblings' parents to the same parents
        for sibling_id in siblings:
            family_tree[sibling_id]["parents"] = [parent1, parent2]
    
    return family_tree

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
#examplar:
@proposition(E)
class Char(object):
    def __init__(self, id, char):
        assert id in PEOPLE
        assert char in PEOPLE
        self.id=id
        self.char=char
    def 

    def _prop_name(self):
        return f"Char.{self.id}+={self.char}"

@proposition(E)
class Rel(object):
    def __init__(self,family1,family2):
        assert family1 in FAMILY
        assert family2 in FAMILY
        self.family1 = family1
        self.family2 = family2

    def _prop_name(self):
        return f"fam({self.char}"


#our project:
#Characteristics of each family member
@proposition(E)
class Generation(object):
    def _init_(self, person_id, generation):
        assert person_id in PEOPLE
        self.person_id = person_id
        self.generation = generation

    def _prop_name(self):
        return f"G({self.person_id}) = {self.generation}"

@proposition(E)
class Female(object):
    def _init_(self, person_id):
        assert person in PEOPLE
        self.person_id =person_id

    def _prop_name(self):
        return f"F({self.person_id})=True"

@proposition(E)
class Affection(object):
    def _init_(self, person_id):
        assert person_id in PEOPLE
        self.person_id = person_id

    def _prop_name(self):
        return f"F({self.person_id})=True"

@proposition(E)
class BloodRelative:
    def _init_(self, person_id):
        assert person_id in PEOPLE
        self.person_id = person_id

    def _prop_name(self):
        return f"F({self.person_id})=True"


#Relationship between family members
@proposition(E)
class Child:
    def _init_(self, child_id, parent1_id, parent2_id):
        assert child_id, parent1_id, parent_id in PEOPLE
        self.child_id = child_id
        self.parent1_id = parent1_id
        self.parent2_id = parent2_id

    def _prop_name(self):
        return f"C({self.child_id}, {self.parent1_id}, {self.parent2_id})=True"
        


@proposition(E)
class Sibling:
    def _init_(self, person1_id, person2_id):
        assert person1_id, person2_id in PEOPLE
        self.person1_id = person1_id
        self.person2_id = person2_id

    def _prop_name(self):
        return f"C({self.perso1n_id}, {self.person2_id})=True"

#Inheritance Pattern
@proposition(E)
class MoreMaleAffected:
    def _init_(self, generation):
        self.generation = generation

    def _prop_name(self):
        return f"M({genertion})=True"


#Inheritance Mode
@proposition(E)
class RecessiveDisease:
    def _prop_name(self):
        return "R=True"

@proposition(E)
class XLinkedDisease:
    def _prop_name(self):
        return "X=True"

# Initialize propositions
@constraint.at_least_one(E)
@proposition(E)
class AtLeastOneAffected():
    

# Initialize propositions
g = Generation(person_id, generation)
f = Female(person_id)
a = Affected(person_id)
r = BloodRelative(person_id)
c = Child(person_id, parent1_id, parent2_id)
s = Sibling(person1_id, person2_id)
m = MoreMalesAffected(generation)
r_mode = RecessiveDisease()
x_mode = XLinkedDisease()


    
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
