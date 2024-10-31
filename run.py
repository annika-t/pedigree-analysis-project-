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


@proposition(E)
class Char(object):
    def assign_person(id, char):
        characteristic=[0,0] #char[0]: bool for female, char[1]: bool for blood relative, char[2]: bool for affected 
        if char=="Female":
            char[0]=1
        elif char=="Blood Relative":
            char[1]=1
        elif char=="Affected":
            char[2]=1
        PEOPLE["id"]=characteristic
    def get_person:
        if id in PEOPLE:
            if id <=FAMNUM:
                return PEOPLE["id"]
    def _prop_name(self):
        return f"Char.{self.id}={self.char}"

@proposition(E)
class Rel(object):
    def create_ifam(id1, id2, id3=None):
        # Initialize a family structure
        ifamily = {"parents": [], "siblings": []}

        # Helper function to add a person to a list without duplicates
        def add_to_list(person_id, list_name):
            person = PEOPLE[person_id]
            if person not in ifamily[list_name]:
                ifamily[list_name].append(person)

        # Two arguments case: add both to siblings
        if id3 is None:
            add_to_list(id1, "siblings")
            add_to_list(id2, "siblings")
        else:
            # Three arguments case: first goes to siblings, second and third go to parents
            add_to_list(id1, "siblings")
            add_to_list(id2, "parents")
            add_to_list(id3, "parents")

        # Add the completed family dictionary to IFAMILIES
        IFAMILIES.append(ifamily)



def create_pedigree(IFAMILIES):



#Propositions:
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
f = Char(person_id,"Female")   
a = Char(person_id,"Affected")
r = Char(person_id,"Blood Relative")
c = Rel(person_id, parent1_id, parent2_id)
s = Rel(person1_id, person2_id)
m = MoreMalesAffected(generation)
r_mode = RecessiveDisease()
x_mode = XLinkedDisease()



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
