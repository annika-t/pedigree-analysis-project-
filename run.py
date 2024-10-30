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
#amount of people in the family 
FAMNUM=20

#generate a dictionary represent each family member as an unique integer 
def create_people(FAMNUM):
    while i <=FAMNUM:
        id=i
        PEOPLE.update({id: None})
    
    
def create_pedigree(IFAMILIES):





@proposition(E)
class Char(object):
    def assign_person(id, char):
        characteristic=[0,0] #char[0]: bool for female, char[1]: bool for blood relative, char[2]: bool for affected 
        if char="Female":
            char[0]=1
        elif char="Blood Relative":
            char[1]=1
        elif char="Affected":
            char[2]=1
        PEOPLE[id]=characteristic
    def get_person:
        if if in PEOPLE:
            if id <=FAMNUM:
                return PEOPLE[id]
    def _prop_name(self):
        return f"Char.{self.id}={self.char}"

@proposition(E)
class Rel(object):
    def create_ifam(id1, id2, id3=None): 
    # Helper function to add a person to a list without duplicates
        def add_to_list(person, list_name):
            if person not in IFAMILY[list_name]:
                ifamily[list_name].append(person)
    
        # Add people to appropriate lists based on the number of arguments
        if id3 is None:
            # Two arguments case: add both to siblings
            add_to_list(id1, "siblings")
            add_to_list(id2, "siblings")
            # Constraint: the siblings should have the same parents
            if (id1["parents"] != id2["parents]): # Constraints: person1 and person2 do not have the same parents
                raise ValueError("The siblings should have the same parents.")
            elif (id1["parents"] == True): # only person1 has parents
                id2["parents"] = id1["parents"]
            elif (id2["parents] == True): # only person2 has parents
                id1["parents"] = id2["parents"]
            else: #if both person have no parents
                id1["parents"] = None
                id2["parents"] = None         
        else: 
        # Three arguments case: first goes to siblings, second and third go to parents
        # Check Constraint: the parents should not be blood relatives
            if id2["parents"] == id2["parents"]:
                raise ValueError("Parents should not be blood relatives (i.e. siblings)")
            else:
                add_to_list(id1, "siblings")
                add_to_list(id2, "parents")
                add_to_list(id3, "parents")
        IFAMILIES.append(ifamily)
        self.family1 = family1
        self.family2 = family2
        

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
f = Char(person_id,"Female")   
a = Char(person_id,"Affected")
r = Char(person_id,"Blood Relative")
c = Rel(person_id, parent1_id, parent2_id)
s = Rel(person1_id, person2_id)
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
