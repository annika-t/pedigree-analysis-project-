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
    if g>1:
        g_people = int(input(f"The total number of people in generation {g}: "))  # Get the number of people in the generation
    else:
        g_people = 2
    generation_info = {}  # Initialize dictionary to store ids of people in the generation
    generation_info["id"] = []  # Create a list for this generation
    
    for person_id in range(ID, ID + g_people):
        print(f"\nEnter information for Person {person_id} in Generation {g}:")
        
        # Get user input for each attribute
        is_male = int(input("Is the person male? (True=1/False=0): ")) == 1
        if g==1:
            is_blood_relative = True
        else:
            is_blood_relative = int(input("Is the person a blood relative? (True=1/False=0): ")) == 1
        if is_blood_relative:
            is_affected = int(input("Is the person affected by the trait? (True=1/False=0): ")) == 1
            if g>1: #for generation grerater than 1
                p1 =int(input("Enter ID of Parent 1: "))
                p2 = int(input("Enter ID of Parent 2: "))
                if p1>p2:
                    p1, p2 = p2, p1
                create_fam_units(person_id, p1, p2)# Add the person to the family unit
        else:
            is_affected = False
            
        # Store the person's info in a dictionary called person
        person = {
            "is_male": is_male,
            "is_affected": is_affected,
            "is_blood_relative": is_blood_relative
        }
        
        PEOPLE[person_id] = person
        generation_info["id"].append(person_id)  # Add the person ID to the generation list
              
        count+=1
    # Update the ID for the next generation after processing all people in the current generation
    ID += g_people
    
    # Add affected count to the generation info dictionary
    generation_info["count"] = count
    
    return generation_info, ID

def generate_pedigree():
    global ID  # Ensure we modify the global ID variable
    val_input = input("do you wish to input values?(y/n)").lower()=="y"#determines if you want to preload or input your own values
    if val_input:
        GENERATION_COUNT = int(input("The total number of generations in the pedigree: "))
        for g in range(1, GENERATION_COUNT + 1):  # Correct the range to start from 2
            generation_data, ID = create_generation(g, ID)  # Collect data for this generation and update ID
            GENERATION[g] = generation_data  # Store the generation information in the GENERATION dictionary
            print(GENERATION)
            print("\n")
    else:
        GENERATION.update({1: {'id': [1, 2], 'count': 2}, 
        2: {'id': [3, 4, 5, 6, 7, 8], 'count': 6}, 
        3: {'id': [9, 10, 11, 12, 13, 14], 'count': 6}})
            
        PEOPLE.update({1: {'is_male': True, 'is_affected': False, 'is_blood_relative': True}, 
        2: {'is_male': False, 'is_affected': True, 'is_blood_relative': True}, 
        3: {'is_male': True, 'is_affected': False, 'is_blood_relative': False}, 
        4: {'is_male': False, 'is_affected': False, 'is_blood_relative': True}, 
        5: {'is_male': True, 'is_affected': True, 'is_blood_relative': True}, 
        6: {'is_male': False, 'is_affected': False, 'is_blood_relative': False}, 
        7: {'is_male': False, 'is_affected': True, 'is_blood_relative': True}, 
        8: {'is_male': True, 'is_affected': False, 'is_blood_relative': False}, 
        9: {'is_male': False, 'is_affected': False, 'is_blood_relative': True}, 
        10: {'is_male': False, 'is_affected': False, 'is_blood_relative': True}, 
        11: {'is_male': False, 'is_affected': True, 'is_blood_relative': True}, 
        12: {'is_male': True, 'is_affected': True, 'is_blood_relative': True}, 
        13: {'is_male': True, 'is_affected': True, 'is_blood_relative': True}, 
        14: {'is_male': True, 'is_affected': False, 'is_blood_relative': True}})

        FAMILIES.extend([{'parents': [1, 2], 'children': [4, 5, 7]}, 
        {'parents': [3, 4], 'children': [9, 10]}, 
        {'parents': [5, 6], 'children': [11, 12]}, 
        {'parents': [7, 8], 'children': [13, 14]}] )
    

# Execute the program
generate_pedigree()

print(GENERATION)
print(PEOPLE)
print(FAMILIES)
# Hashable Base Class
class Hashable:
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)
    def __repr__(self):
        return str(self)
    
# Propositions for gender
@proposition(E)
class Male(Hashable):
    def __init__(self, id):
        self.id = id
    def __str__(self) -> str:
        return f"{self.id} is male"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


# Propositions for whether a person has a trait
@proposition(E)
class Affected(Hashable):
    _prop_name = "Affected"
    def __init__(self, id):
        self.id = id
    def __str__(self) -> str:
        return f"{self.id} is affected"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


# Propositions for whether a person is a blood relative
@proposition(E)
class Blood_Relative(Hashable):
    _prop_name = "Blood_Relative"
    def __init__(self, id):
        self.id = id
    def __str__(self) -> str:
        return f"{self.id} is a blood relative"
    @classmethod
    def _prop_name(cls):
        return cls.__name__
# Propositions for parent-child relationships
@proposition(E)
class Child(Hashable):
    _prop_name = "Child"
    def __init__(self, i, j, k):  # Child(i,j,k): True if i is the child of j and k
        self.i = i
        self.j = j
        self.k = k
    def __str__(self) -> str:
        return f"{self.i} is the child of {self.j} and {self.k}"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


# Propositions for generation comparison of affected counts
@proposition(E)
class More_Male(Hashable):
    _prop_name = "More_Male"
    def __init__(self, g):
        self.g = g
    def __str__(self) -> str:
        return f"Generation {self.g} has more affected males than females"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


# Propositions for modes of inheritance
@proposition(E)
class Recessive(Hashable):
    _prop_name = "Recessive"
    def __str__(self) -> str:
        return "The trait is recessive"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


@proposition(E)
class Dominant(Hashable):
    _prop_name = "Dominant"
    def __str__(self) -> str:
        return "The trait is dominant"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


@proposition(E)
class Autosomal(Hashable):
    _prop_name = "Autosomal"
    def __str__(self) -> str:
        return "The trait is autosomal"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


@proposition(E)
class X_linked(Hashable):
    _prop_name = "X_linked"
    def __str__(self) -> str:
        return "The trait is X-linked"

# Propositions for affected male/female counts
@proposition(E)
class Affected_Male_Count(Hashable):
    _prop_name = "Affected_Male_Count"
    def __init__(self, g, count):
        self.g = g
        self.count = count
    def __str__(self) -> str:
        return f"Generation {self.g} has {self.count} affected males"
    @classmethod
    def _prop_name(cls):
        return cls.__name__


@proposition(E)
class Affected_Female_Count(Hashable):
    _prop_name = "Affected_Female_Count"
    def __init__(self, g, count):
        self.g = g
        self.count = count
    def __str__(self) -> str:
        return f"Generation {self.g} has {self.count} affected females"
    @classmethod
    def _prop_name(cls):
        return cls.__name__

def build_theory():
    # Add family unit propositions
    family_unit_propositions = {}
    i=1
    for f in FAMILIES:
        one_family=[]
        children=[]
        parents=[]
        for p in f["parents"]:
            if PEOPLE[p]["is_affected"]:
                parents.append(Affected(p)) 
            else:
                parents.append(~Affected(p))
        E.add_constraint((PEOPLE[p]["is_male"] & ~PEOPLE[p-1]["is_male"])|(~PEOPLE[p]["is_male"] & PEOPLE[p-1]["is_male"]))
        print("Parents Propositions:", parents)
        for c in f["children"]:
            one_family.append(Child(PEOPLE[c],f["parents"][0],f["parents"][1]))
            if PEOPLE[c]["is_affected"]:
                children.append(Affected(c))
            else:
                children.append(~Affected(c))
        print("Children Propositions:", children)
        family_unit_propositions[i] = (~And(parents) & And(one_family) & Or(children))
        print(family_unit_propositions[i])
        i+=1

    def reccessive_theory(family_unit_propositions):
        E.add_constraint(Or(family_unit_propositions)>>Recessive)
        E.add_constraint(Recessive>> ~Dominant)
        E.add_constraint(~Or(family_unit_propositions)>>Dominant)
        E.add_constraint(Dominant>> ~Recessive)
        if (Or(family_unit_propositions)>>Recessive).solve():
            print("trait is recessive")
        else:
            print("trait is dominant")

    # Generate the propositions for each generation
    generation_proposition = {}
    for g in range(2, len(GENERATION) + 1): #skip first generation
        generation_proposition[g] = []
        for person_id in GENERATION[g]["id"]:
            if person_id not in PEOPLE:
                raise KeyError(f"Person ID {person_id} not found in PEOPLE")
            print(f"Processing generation {g}, person_id {person_id}")
            print(f"Person data: {PEOPLE.get(person_id, 'Not found')}")
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
            print("person props: ",person_propositions)
    print(generation_proposition)
            
    def count_affected_recursive(g, gender):
        m=0
        for idx, person_propositions in enumerate(generation_proposition[g]):  # Loop through propositions for each person
            person_id = GENERATION[g]["id"][idx]  # Retrieve person ID
            # Define affected female conditions
            if gender=="male":
                affected = Affected(person_id) & Male(person_id) & Blood_Relative(person_id)
                if person_propositions[0] =="Affected":
                    print("AFFECTED AHHHH")
                if (person_propositions[1]=="Male"):
                    print("GENRDER AHHHH")
                if(person_propositions[2]=="Blood_Relative"):
                    print("BLOOD????")
                count_function = Affected_Male_Count
                
            else:
                affected = Affected(person_id) & ~Male(person_id) & Blood_Relative(person_id)
                count_function = Affected_Female_Count
                # Add constraints for affected females
            if affected:
                print("true")
            a = And(person_propositions) & affected
            b = And(person_propositions) & ~affected
            E.add_constraint(a & (a >> count_function(g, m + 1)))
            E.add_constraint(b & (b >> count_function(g, m)))
            # Update count if affected  
            if And(person_propositions) & affected:
                m += 1 
        return count_function(g, m)
        
    print("BYEEE")
    #print(count_affected_recursive(3, "female"))
    print(count_affected_recursive(3, "male"))
        
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
        more_male_affected_in_every_generation=[]
        for g in generation_proposition:
            more_male_combo= create_all_more_male_combos(g)
            more_male_affected_in_every_generation.append(count_affected_recursive(g,"male") & count_affected_recursive(g,"female"), more_male_combo >> More_Male )
        E.add_constraint(And(more_male_affected_in_every_generation)>>X_linked)
        E.add_constraint(~And(more_male_affected_in_every_generation)>>Autosomal)
        E.add_constraint(And(Autosomal>>~X_linked))
        E.add_constraint(~And(X_linked>>~Autosomal))
        if (And(more_male_affected_in_every_generation)>>X_linked).solve():
            print("trait is X_linked")
        else:
            print("trait is autosomal")
    


if __name__ == "__main__":
    T = build_theory()
    T = T.compile()
    print()

        

