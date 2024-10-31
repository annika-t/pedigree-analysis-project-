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



    @staticmethod
    def create_pedigree():
        PEDIGREE = {}  # Dictionary to store generational information
    
        # Divide PEOPLE into blood relatives and non-blood relatives
        list_BR = [id for id, details in PEOPLE.items() if details[1] == 1]  # Blood relatives
        list_S = [id for id in PEOPLE if id not in list_BR]  # Non-blood relatives
    
        # Recursive function to process blood relatives in generations
        def process_generation(current_gen, previous_gen=None):
            next_gen_ids = []
    
            for person_id in list_BR[:]:  # Iterate over a copy of list_BR
                person = PEOPLE[person_id]
                parents = IFAMILIES[person_id].get("parents", [])
    
                # Check for first generation (no parents)
                if not parents and current_gen == 1:
                    if "gen 1" not in PEDIGREE:
                        PEDIGREE["gen 1"] = {}
                    PEDIGREE["gen 1"][person_id] = person
                    list_BR.remove(person_id)
    
                # Process subsequent generations based on parents in the previous generation
                elif current_gen > 1 and any(parent in PEDIGREE.get(f"gen {current_gen - 1}", {}) for parent in parents):
                    gen_key = f"gen {current_gen}"
                    if gen_key not in PEDIGREE:
                        PEDIGREE[gen_key] = {}
                    
                    # Add person and their siblings
                    PEDIGREE[gen_key][person_id] = person
                    siblings = IFAMILIES[person_id].get("siblings", [])
                    for sibling in siblings:
                        if sibling in list_BR:
                            PEDIGREE[gen_key][sibling] = PEOPLE[sibling]
                            list_BR.remove(sibling)
                    
                    list_BR.remove(person_id)  # Remove person from list_BR
                    next_gen_ids.extend(parents)  # Collect for the next generation
    
            # Recurse if there are more people to process in list_BR
            if list_BR:
                process_generation(current_gen + 1, next_gen_ids)
    
        # Start processing from generation 1
        process_generation(1)
    
        # Process non-blood relatives in list_S once all blood relatives are processed
        def process_siblings(last_gen):
            while list_S:
                for person_id in list_S[:]:
                    person = PEOPLE[person_id]
                    parents = IFAMILIES[person_id].get("parents", [])
    
                    # Find a suitable generation based on parents' generation
                    for gen in range(last_gen, 0, -1):
                        if any(parent not in PEDIGREE.get(f"gen {gen - 1}", {}) for parent in parents):
                            gen_key = f"gen {gen - 1}"
                            if gen_key not in PEDIGREE:
                                PEDIGREE[gen_key] = {}
                            PEDIGREE[gen_key][person_id] = person
                            list_S.remove(person_id)
                            break
    
        # Process remaining siblings after blood relatives
        process_siblings(len(PEDIGREE))
    
        return PEDIGREE


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
