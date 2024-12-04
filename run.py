from bauhaus import Encoding, proposition, constraint, And, Or
from bauhaus.utils import count_solutions, likelihood
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()
PEOPLE = {}  # Dictionary to store characteristics of each person
FAMILIES = []  # List to store family units (sibling groups and parents)
GENERATION = {}  # Dictionary to store generations
ID = 1  # Variable to assign unique integer ID to each family member

# Ask for the number of generations in the tree
GENERATION_COUNT = int(input("The total number of generations in the pedigree: "))

def create_fam_units(c, p1, p2):
    """
    Creates or updates an immediate family dictionary with parents and children.

    Args:
        c (int): The ID of the child.
        p1 (int): The ID of the first parent.
        p2 (int): The ID of the second parent.
    """
    parents = [p1, p2]  # Store parents as a list

    # Check if a family with the same parents already exists
    for family in FAMILIES:
        if family["parents"] == parents:  # Compare parents as lists
            family["children"].append(c)  # Add the child to the existing family unit
            break
    else:
        # If no matching family exists, create a new one
        new_family = {
            "parents": parents,  # Use a list instead of a tuple
            "children": [c]
        }
        FAMILIES.append(new_family)


def create_generation(g, ID):
    """
    Collects information about people in a specific generation of the pedigree tree.

    Args:
        g (int): The generation number.
        ID (int): The starting ID for the generation.

    Returns:
        tuple: A dictionary with person IDs as keys and their attributes as values, and the updated ID.
    """
    count = 0  # Store the number of people in a generation
    g_people = int(input(f"The total number of people in generation {g}: "))  # Get the number of people in the generation
    generation_info = {}  # Initialize dictionary to store ids of people in the generation
    generation_info[g] = []  # Create a list for this generation
    
    for person_id in range(ID, ID + g_people):
        print(f"\nEnter information for Person {person_id} in Generation {g}:")
        
        # Get user input for each attribute
        is_male = input("Is the person male? (True/False): ").strip().lower() == 'true'
        is_affected = input("Is the person affected by the trait? (True/False): ").strip().lower() == 'true'
        is_blood_relative = input("Is the person a blood relative? (True/False): ").strip().lower() == 'true'
        
        # Store the person's info in a dictionary called person
        person = {
            "is_male": is_male,
            "is_affected": is_affected,
            "is_blood_relative": is_blood_relative
        }
        
        PEOPLE[person_id] = person
        generation_info[g].append(person_id)  # Add the person ID to the generation list
        
        # If the generation is greater than 0, ask for parent IDs and store family information
        if g > 0:
            p1 = input("Enter ID of Parent 1: ")
            p2 = input("Enter ID of Parent 2: ")
            create_fam_units(person_id, p1, p2)  # Add the person to the family unit
        count+=1
    # Update the ID for the next generation after processing all people in the current generation
    ID += g_people
    
    # Add affected count to the generation info dictionary
    generation_info["count"] = count
    
    return generation_info, ID

def generate_pedigree():
    global ID  # Ensure we modify the global ID variable
    for g in range(1, GENERATION_COUNT + 1):  # Correct the range to start from 1
        generation_data, ID = create_generation(g, ID)  # Collect data for this generation and update ID
        GENERATION[g] = generation_data  # Store the generation information in the GENERATION dictionary

# Execute the program
generate_pedigree()

# Propositions for gender

@proposition(E)
class Male:
    def __init__(self, id):
        self.id = id
    def _repr_(self):
        return f"{self.id} is male"
    
# Propositions for whether or not a person has a trait
@proposition(E)
class Affected:
    def __init__(self, id):
        self.id = id
    def _repr_(self):
        return f"{self.id} is affected"

# Propositions for whether or not a person is a blood relative
@proposition(E)
class Blood_Relative:
    def __init__(self, id):
        self.id = id
    def _repr_(self):
        return f"{self.id} is a blood relative"

# Propositions to describe relationships between family members
@proposition(E)
class Child:
    def __init__(self, i, j, k):  # Child(i,j,k) is true if i is the child of j and k
        self.i = i
        self.j = j
        self.k = k
    def _repr_(self):
        return f"{self.i} is the child of {self.j} and {self.k}"
    
# Propositions that will be true if there are more affected male relatives in a generation than female
@proposition(E)
class More_Male:
    def __init__(self, g):
        self.g = g
    def _repr_(self):
        return f"Generation {self.g} has more affected male relatives than female ones"

# Propositions to describe mode of inheritance of the trait
@proposition(E)
class Recessive:
    def _repr_(self):
        return f"The trait is recessive"

@proposition(E)
class Dominant:
    def _repr_(self):
        return f"The trait is dominant"

@proposition(E)
class Autosomal:
    def _repr_(self):
       return f"The trait is autosomal"

@proposition(E)
class X_linked:
    def _repr_(self):
     return f"The trait is X linked"

# Propositions for counting the number of affected male/female in a generation
@proposition(E)
class Affected_Male_Count:
    def __init__(self, p, m): 
        self.p = p
        self.m = m

@proposition(E)
class Affected_Female_Count:
    def __init__(self, p, m): 
        self.p = p
        self.m = m


# Add family unit propositions
family_unit_propositions = {}
for f in FAMILIES.item():
    one_family=[]
    children=[]
    parents=[]
    for p in f["parent"]:
        parent = PEOPLE[p]
        if parent["is_affected"]:
            parent.append(Affected(p))
        else:
            parent.append(~Affected(p))
    for c in f["children"]:
        child=PEOPLE[p]
        one_family.append(Child(child,f["parent"][0],f["parent"][1]))
        if child["is_affected"]:
            child.append(Affected(p))
        else:
            child.append(~Affected(p))
    family_unit_propositions[f].append(~And(parents) & And(one_family) & Or(children))

def reccessive_theory(family_unit_propositions):
    E.add_constraint(Or(family_unit_propositions)>>Recessive)
    E.add_constraint(Recessive>> ~Dominant)
    E.add_constraint(~Or(family_unit_propositions)>>Dominant)
    E.add_constraint(Dominant>> ~Recessive)

# Generate the propositions for each generation
generation_proposition = {}
for g in range(1, len(GENERATION) + 1):
    generation_proposition[g] = []
    for person_id in GENERATION[g]:
        person = PEOPLE[person_id]
        person_propositions = []
        
        if person["is_affected"]:
            person_propositions.append(Affected(person_id))
        else:
            person_propositions.append(~Affected(person_id))
        
        if person["is_male"]:
            person_propositions.append(Male(person_id))
        else:
            person_propositions.append(~Male(person_id))
        
        if person["is_blood_relative"]:
            person_propositions.append(Blood_Relative(person_id))
        else:
            person_propositions.append(~Blood_Relative(person_id))
        
        generation_proposition[g].append((person_propositions))

def count_affected_recursive(generation_proposition, g=1, male_m=0, female_m=0):
    if g > len(generation_proposition):  # Base case: all generations processed
        return g, male_m, female_m

    # Process the current generation
    for person_propositions in generation_proposition[g]:  # Loop through propositions for each person
        person_id = GENERATION[g][generation_proposition[g].index(person_propositions)]  # Retrieve person ID

        # Define affected male and female conditions
        affected_male = Affected(person_id) & Male(person_id) & Blood_Relative(person_id)
        affected_female = Affected(person_id) & ~Male(person_id) & Blood_Relative(person_id)

        # Add constraints for affected males
        E.add_constraint((person_propositions,And(person_propositions) >> affected_male) >> Affected_Male_Count(g, male_m + 1))
        E.add_constraint((person_propositions,And(person_propositions) >> ~affected_male) >> Affected_Male_Count(g, male_m))

        # Update male count if affected
        if (person_propositions,And(person_propositions) >> affected_male).solve():
            male_m += 1

        # Add constraints for affected females
        E.add_constraint((person_propositions,And(person_propositions) >> affected_female) >> Affected_Female_Count(g, female_m + 1))
        E.add_constraint((person_propositions,And(person_propositions) >> ~affected_female) >> Affected_Female_Count(g, female_m))

        # Update female count if affected
        if (person_propositions, And(person_propositions) >> affected_female).solve():
            female_m += 1

    # Recursive call for the next generation
    return count_affected_recursive(generation_proposition, g + 1, male_m, female_m)

def create_all_more_male_combos(g):
    """
    Create all combinations where the number of affected males (m) is greater than 
    the number of affected females (f), and the total number of affected individuals
    does not exceed g.
    
    Parameters:
        g (int): Total number of affected individuals.
    
    Returns:
        list: All valid combinations as logical expressions.
    """
    all_combos = []
    
    for m in range(1, g + 1):  # Affected males from 1 to g
        combos = []
        affected_m_prop = Affected_Male_Count(g, m)
        for f in range(m):  # Affected females less than affected males
            if m + f <= g :  # Ensure the total does not exceed g
                affected_f_prop = Affected_Female_Count(g, f)
                one_combo = affected_m_prop & affected_f_prop
                combos.append(one_combo)
        
        # Combine all female combos for the current male count
        if combos:  # Avoid appending empty Or() expressions
            all_combos.append(Or(combos))
    
    return all_combos

def x_linked_theory(generation_proposition):
    return 


        

