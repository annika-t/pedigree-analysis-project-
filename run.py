
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

PEDIGREE={} 
#dictionary to store immediate family (siblings+parents)
IFAMILIES=[]
#dictionary to store individual family member (id, chars)
PEOPLE={} 

def create_person(id, gender, affected, br):
    char=[gender, affected, br]
    PEOPLE.update({id: char})

def create_ifam(person1, person2, person3=None): #parameters are id of people 
    # Helper function to add a person to a list without duplicates
    def add_to_list(person, list_name):
        if person not in IFAMILY[list_name]:
            ifamily[list_name].append(person)

    # Add people to appropriate lists based on the number of arguments
    if person3 is None:
        # Two arguments case: add both to siblings
        add_to_list(person1, "siblings")
        add_to_list(person2, "siblings")
    else:
        # Three arguments case: first goes to siblings, second and third go to parents
        if (person2.gender != person3.gender):
            add_to_list(person1, "siblings")
            add_to_list(person2, "parents")
            add_to_list(person3, "parents")
        else:
            raise ValueError("Parents must be of opposite genders.")
    IFAMILIES.append(ifamily)
    
def create_pedigree(IFAMILIES):





    
# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
#examplar:
@proposition(E)
class Char(object):
    def __init__(self, id, char):
        assert id in PEOPLE
        assert char in PEOPLE
        self.id=id
        self.char=char
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
