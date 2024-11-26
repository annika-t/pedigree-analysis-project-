from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
from config import *
from lib204 import semantic_interface

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

PEDIGREE={} # Dictionary to store immediate family (siblings+parents)
IFAMILIES=[] # Dictionary to store individual family member (id, chars)
PEOPLE={} # Amount of people in the family 
FAMNUM=20 # Total number of family members

# Generate a dictionary represent each family member as an unique integer 
def create_people(FAMNUM):
    i=1
    while i <=FAMNUM:
        id=i
        PEOPLE.update({id: [0,0,0]})
        i+=1


@proposition(E)
class Char(object):
    def __init__(self, id, char):
        self.id = id
        self.char = char
        
    @staticmethod
    def assign_person(id, char):
        # Assign the characterisitcs for each id in the PERSON list
        if id in PEOPLE:
            if char == "Female":
                PEOPLE[id][0] = 1
            elif char == "Blood Relative":
                PEOPLE[id][1] = 1
            elif char == "Affected":
                PEOPLE[id][2] = 1

    @staticmethod
    def get_person(id):
        return PEOPLE.get(id, None)

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

        if id3 is None:
            # Two arguments case: add both to siblings
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
        return f"M({self.genertion})=True"

#Inheritance Mode
@proposition(E)
class RecessiveDisease:
    '''
    Constraints: 
    A person is affected and their parents are not. 
    This must mean the parents are carriers of the trait and the trait is recessive
    '''
    def _prop_name(self):
        return "R=True"

@proposition(E)
class XLinkedDisease:
    def _prop_name(self):
        return "X=True"

# Initialize propositions
#create something to assign the ids

child1_id = create_people()  # Assuming this is the id of the affected family member
parent1_id = 2   # Assuming this is the id of one of the parents
parent2_id = 3  # the other parent
child2_id = 4 # sibling 
generation = 3

a1 = Char(child1_id, "Affected") # Affected family member 1 (child 1)
a2 = Char(parent1_id, "Affected")  # Affected family member 2 (parent)
a3 = Char(parent2_id, "Affected")  # Affected family member 3 (another parent)
c1 = Rel(child1_id, parent1_id, parent2_id)
c2 = Rel(child2_id, parent1_id, parent2_id)# Parent-child relationship
s = Rel(child1_id, child2_id)              # Sibling relationship
m = MoreMaleAffected(generation)             # More males affected in generation
r_mode = RecessiveDisease()                    # Recessive disease mode
x_mode = XLinkedDisease()  # X-linked disease mode


# Theory for Constraints
def theory():
    # Recursive function to calculate male(i, k)
    def male(i, k, propositions):
        '''
        
        '''
        # Base cases
        if i == 1 and k == 0:
            return Female(propositions[i-1])
        elif i == 1 and k == 1:
            return ~Female(propositions[i-1])
        # Recursive cases
        if k > 0:
            # Case 1: (male(i-1, k-1) /\ !Female(person_id))
            case1 = male(i - 1, k - 1, propositions) & ~ Female(propositions[i-1])
        else:
            case1 = False  # Avoid invalid recursive calls for k < 0
        
        # Case 2: (male(i-1, k) /\ Female(person_id))
        case2 = male(i - 1, k, propositions) & Female(propositions[i-1])
        # Combine cases with OR
        return case1 | case2

    def blood_relative():
        '''
        Return the number of blood relatives in the family tree 
        (all the member except those are "married" into the family tree)
        '''
        # Initialize the count for the blood relatives
        count = 0
        for generation, members in PEDIGREE.items():  # Iterate through generations and their members
            for person_id, person_info in members.items():  # Iterate through members in the generation
                parents = IFAMILIES[person_id].get("parents", [])
                # Case 1: person has no parents and is in "gen 1"
                if generation == "gen 1" and not parents:
                    count += 1
                # Case 2: person is not in "gen 1" and has parents
                elif generation != "gen 1" and parents:
                    count += 1
        return count

    '''
    Constraints:
    '''
    # If both parents of an affected family member are unaffected, then the disease is recessive
    E.add_constraint((a1 & c1 & (~a2 & ~a3)) >> r_mode)
    
    #loops to list all possible cases where there a more male than female in a generation
    # Outer Loop for male
    # n should be number of blood relatives in a generation
    result=[]
    for i in range(n):
        m_count=M(n,i)
        # inner loop for female
        for j in range(n):
            f_count=F(n,j)
            #create constraint 
            result.append( m_count & f_count )
    E.add_constraint(m >> Or(result))

    # X-linked Disease: If there are more males in a generation than females, the M(g) is true, and male which carried this diesease is affected
    E.add_constrainconstraints(>> x_mode)



if __name__ == "__main__":
    T = theory()
    # Compile the Constraints to the main
    T = T.compile()

    # Sample IDs for family members
    person1_id, person2_id, person3_id, person4_id, person5_id, person6_id = range(1, 7)
    
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
    Char.assign_person(person2_id, "Affected")
    Char.assign_person(person3_id, "Blood Relative")
    Char.assign_person(person4_id, "Female")
    #person5 would be an unaffected, non blood relative male
    Char.assign_person(person6_id, "Blood Relative") 
    
    
    # Create relationships between individuals
    Rel.create_ifam(person3_id, person4_id) # Siblings
    Rel.create_ifam(person3_id, person1_id, person2_id) # Gen 0 and gen 1
    Rel.create_ifam(person4_id, person1_id, person2_id) # Gen 0 and gen 1
    Rel.create_ifam(person6_id, person4_id, person5_id) # Gen 1 and gen 2
    
    # Build the pedigree from the relationships
    PEDIGREE = Rel.create_pedigree()
    
    # Print generated pedigree for verification
    print("Pedigree:", PEDIGREE)
    
    # Initialize propositions for family members
    f = Char.assign_person(person1_id, "Female")   
    a1 = Char.assign_person(person2_id, "Affected")
    a2 = Char.assign_person(person4_id, "Affected")
    c = Rel.create_ifam(person6_id, person4_id, person5_id)
    s = Rel.create_ifam(person4_id, person3_id)
    m = MoreMaleAffected(1)
    r_mode = RecessiveDisease()
    x_mode = XLinkedDisease()

    # Compile and analyze the theory
    T = theory()  # Define the theory with constraints
    T = T.compile()

    # Run the likelihood function as a test
    likelihood_value = likelihood(E, r_mode)
    print("Likelihood of recessive disease:", likelihood_value)

