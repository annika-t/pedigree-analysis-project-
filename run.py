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
        list_NB = [id for id in PEOPLE if id not in list_BR]  # Non-blood relatives
    
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
    
        # Process non-blood relatives in list_NB  once all blood relatives are processed
        def process_nb(last_gen):
            while list_NB:
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
    
        # Process non-blood relative after blood relatives
        process_nb(len(PEDIGREE))
    
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

# Family Member that is affected
@proposition(E)
class Affected(Char):
    def _prop_name(self):
        return f"A({self.id})=True"
        

# Initialize propositions
f = Char(person_id,"Female")   
a1 = Char(person_id,"Affected")
a2 = Char(parent1_id,"Affected")
a3 = Char(parent2_id,"Affected")
r = Char(person_id,"Blood Relative")
c = Rel(person_id, parent1_id, parent2_id)
s = Rel(person1_id, person2_id)
m = MoreMalesAffected(generation)
r_mode = RecessiveDisease()
x_mode = XLinkedDisease()

# Theory for Constraints
def theory():
    # If both parents of an affected family member are unaffected, then the disease is recessive
    E.add_constraint((a & c & (~a2 & ~a3)) >> r_mode)
    #loops to list all possible cases where there a more male than female in a generation
    # Outer Loop for male
    # n should be number of blood relatives in a generation"
    result=[]
    for i in range(n):
        m_count=M(n,i)
        # inner loop for female
        for j in range(n):
            f_count=F(n,j)
            #create constraint 
            result.append( m_count & f_count )
    E.add_constraint(m >> Or(result))

#Template
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

# Our code:
if __name__ == "__main__":
    T = theory()
    # Compile the Constraints to the main
    T = T.compile()

    # Sample IDs for family members
    person1_id, person2_id, person3_id, person4_id, parent1_id, parent2_id = range(1, 7)
    
    # Set up the size of the family
    FAMNUM = 6
    
    """
    examplar tree:
    person1-----person2                   gen 0
             | 
     person3   person4-----person5        gen 1
                        |
                     person6              gen 2 
    """

    # Generate people and define their characteristics and relationships
    create_people(FAMNUM)  # Initialize PEOPLE dictionary

    # Assign characteristics to individuals
    Char.assign_person(person1_id, "Female")
    Char.assign_person(person2_id, "Blood Relative")
    Char.assign_person(person3_id, "Affected")
    Char.assign_person(person4_id, "Female")
    Char.assign_person(parent1_id, "Blood Relative")
    Char.assign_person(parent2_id, "Blood Relative")
    and more
    
    # Create relationships between individuals
    Rel.create_ifam(person3_id, person4_id) # Siblings
    Rel.create_ifam(person3_id, parent_id, parent2_id) # Gen 0 and gen 1
    Rel.create_ifam(person4_id, parent_id, parent2_id) # Gen 0 and gen 1
    Rel.create_ifam(person6_id, person4_id, parent5_id) # Gen 1 and gen 2
    
    # Build the pedigree from the relationships
    PEDIGREE = Rel.create_pedigree()
    
    # Print generated pedigree for verification
    print("Pedigree:", PEDIGREE)
    
    # Initialize propositions for family members
    f = Char.assign_person(person_id, "Female")   
    a1 = Char.assign_person(person_id, "Affected")
    a2 = Char.assign_person(parent1_id, "Affected")
    a3 = Char.assign_person(parent2_id, "Affected")
    r = Char.assign_person(person_id, "Blood Relative")
    c = Rel.create_ifam(person_id, parent1_id, parent2_id)
    s = Rel.create_ifam(person1_id, person2_id)
    m = MoreMaleAffected(1)
    r_mode = RecessiveDisease()
    x_mode = XLinkedDisease()

    # Compile and analyze the theory
    T = theory()  # Define the theory with constraints
    T = T.compile()

    # Run the likelihood function as a test
    likelihood_value = likelihood(E, recessive_disease_prop)
    print("Likelihood of recessive disease:", likelihood_value)

