from bauhaus import Encoding, proposition, constraint, Or, And
from nnf import config
from default_tree import get_default_data

# Configure SAT solver
config.sat_backend = "kissat"

# Global variables for storing pedigree data
PEOPLE = {}      # Dictionary mapping ID to person characteristics
FAMILIES = []    # List of family relationships
GENERATION = {}  # Dictionary mapping generation number to generation data
ID = 1          # Counter for assigning unique IDs

class Hashable:
    """Base class providing hash functionality for propositions"""
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return hash(self) == hash(other)
    def __repr__(self):
        return str(self)

def build_recessive_theory():
    """
    Builds theory to test if inheritance is recessive.
    Theory is unsatisfiable if any affected child has unaffected parents.
    """
    E = Encoding()
    
    @proposition(E)
    class Affected(Hashable):
        def __init__(self, id):
            self.id = id
        def __str__(self):
            return f"{self.id} is affected"
        @classmethod
        def _prop_name(cls):
            return "Affected"

    @proposition(E)
    class Child(Hashable):
        def __init__(self, child_id, parent1_id, parent2_id):
            self.child = child_id
            self.p1 = parent1_id
            self.p2 = parent2_id
        def __str__(self):
            return f"{self.child} is child of {self.p1} and {self.p2}"
        @classmethod
        def _prop_name(cls):
            return "Child"

    # Create affected status propositions
    affected_props = {}
    for pid, person in PEOPLE.items():
        affected = Affected(pid)
        affected_props[pid] = affected
        if person['is_affected']:
            E.add_constraint(affected)
        else:
            E.add_constraint(~affected)

    # Add inheritance pattern constraints
    for family in FAMILIES:
        p1, p2 = family['parents']
        for child in family['children']:
            # Add child relationship
            E.add_constraint(Child(child, p1, p2))
            
            # If unaffected parents have affected child -> must be recessive
            if (PEOPLE[p1]['is_blood_relative'] and 
                PEOPLE[p2]['is_blood_relative'] and 
                not PEOPLE[p1]['is_affected'] and 
                not PEOPLE[p2]['is_affected'] and 
                PEOPLE[child]['is_affected']):
                E.add_constraint(affected_props[child] & 
                               ~affected_props[p1] & 
                               ~affected_props[p2])
    
    return E

def build_xlinked_theory():
    """
    Builds theory to test if inheritance is X-linked using recursive counting.
    Uses n(i,k) to represent having k affected individuals in first i people.
    Theory is unsatisfiable if any generation has more affected males than females.
    """
    E = Encoding()

    # Base propositions for gender and affected status
    @proposition(E)
    class Male(Hashable):
        def __init__(self, id):
            self.id = id
        def __str__(self):
            return f"{self.id} is male"
        @classmethod
        def _prop_name(cls):
            return "Male"

    @proposition(E)
    class Affected(Hashable):
        def __init__(self, id):
            self.id = id
        def __str__(self):
            return f"{self.id} is affected"
        @classmethod
        def _prop_name(cls):
            return "Affected"

    # Propositions for counting affected individuals
    @proposition(E)
    class MaleCount(Hashable):
        def __init__(self, g, i, k):
            self.g = g  # Generation
            self.i = i  # Position in sequence (1-based)
            self.k = k  # Count of affected males so far
        def __str__(self):
            return f"Gen {self.g}: first {self.i} people have {self.k} affected males"
        @classmethod
        def _prop_name(cls):
            return "MaleCount"

    @proposition(E)
    class FemaleCount(Hashable):
        def __init__(self, g, i, k):
            self.g = g  # Generation
            self.i = i  # Position in sequence (1-based)
            self.k = k  # Count of affected females so far
        def __str__(self):
            return f"Gen {self.g}: first {self.i} people have {self.k} affected females"
        @classmethod
        def _prop_name(cls):
            return "FemaleCount"

    @proposition(E)
    class MoreMale(Hashable):
        def __init__(self, g):
            self.g = g  # Generation
        def __str__(self):
            return f"Generation {self.g} has more affected males than females"
        @classmethod
        def _prop_name(cls):
            return "MoreMale"

    def build_recursive_count(gen, people_list):
        """
        Builds recursive counting constraints for a generation.
        
        Args:
            gen: Generation number
            people_list: List of person IDs in the generation
            
        Returns:
            MoreMale proposition if generation has more affected males than females
        """
        # Create base propositions
        male_props = {}
        affected_props = {}
        for pid in people_list:
            male = Male(pid)
            affected = Affected(pid)
            male_props[pid] = male
            affected_props[pid] = affected
            
            # Add known gender and affected status
            if PEOPLE[pid]['is_male']:
                E.add_constraint(male)
            else:
                E.add_constraint(~male)
            
            if PEOPLE[pid]['is_affected']:
                E.add_constraint(affected)
            else:
                E.add_constraint(~affected)

        N = len(people_list)
        
        # Create counting propositions
        male_counts = {}    # (i,k) -> MaleCount proposition
        female_counts = {}  # (i,k) -> FemaleCount proposition
        
        # Base cases for first person (i=1)
        pid1 = people_list[0]
        
        # Male counting base cases
        # n(1,0) <-> !male(1) or !affected(1)
        male_counts[(1,0)] = MaleCount(gen, 1, 0)
        E.add_constraint(male_counts[(1,0)] >> 
            (~male_props[pid1] | ~affected_props[pid1]))
        E.add_constraint((~male_props[pid1] | ~affected_props[pid1]) >> 
            male_counts[(1,0)])
        
        # n(1,1) <-> male(1) and affected(1)
        male_counts[(1,1)] = MaleCount(gen, 1, 1)
        E.add_constraint(male_counts[(1,1)] >> 
            (male_props[pid1] & affected_props[pid1]))
        E.add_constraint((male_props[pid1] & affected_props[pid1]) >> 
            male_counts[(1,1)])
        
        # Female counting base cases
        female_counts[(1,0)] = FemaleCount(gen, 1, 0)
        E.add_constraint(female_counts[(1,0)] >> 
            (male_props[pid1] | ~affected_props[pid1]))
        E.add_constraint((male_props[pid1] | ~affected_props[pid1]) >> 
            female_counts[(1,0)])
        
        female_counts[(1,1)] = FemaleCount(gen, 1, 1)
        E.add_constraint(female_counts[(1,1)] >> 
            (~male_props[pid1] & affected_props[pid1]))
        E.add_constraint((~male_props[pid1] & affected_props[pid1]) >> 
            female_counts[(1,1)])
        
        # Build recursive cases (i > 1)
        # n(i,k) <-> ((n(i-1,k-1) & affected(i)) | (n(i-1,k) & !affected(i)))
        for i in range(2, N + 1):
            pid = people_list[i-1]
            
            # Male counting recursive cases
            for k in range(i + 1):
                count_prop = MaleCount(gen, i, k)
                male_counts[(i,k)] = count_prop
                
                conditions = []
                if k > 0:  # Can add 1 to previous count
                    conditions.append(
                        male_counts[(i-1, k-1)] & 
                        male_props[pid] & 
                        affected_props[pid]
                    )
                if k <= i-1:  # Can keep previous count
                    conditions.append(
                        male_counts[(i-1, k)] & 
                        (~male_props[pid] | ~affected_props[pid])
                    )
                
                if conditions:
                    expr = Or(conditions)
                    E.add_constraint(count_prop >> expr)
                    E.add_constraint(expr >> count_prop)
            
            # Female counting recursive cases
            for k in range(i + 1):
                count_prop = FemaleCount(gen, i, k)
                female_counts[(i,k)] = count_prop
                
                conditions = []
                if k > 0:  # Can add 1 to previous count
                    conditions.append(
                        female_counts[(i-1, k-1)] & 
                        ~male_props[pid] & 
                        affected_props[pid]
                    )
                if k <= i-1:  # Can keep previous count
                    conditions.append(
                        female_counts[(i-1, k)] & 
                        (male_props[pid] | ~affected_props[pid])
                    )
                
                if conditions:
                    expr = Or(conditions)
                    E.add_constraint(count_prop >> expr)
                    E.add_constraint(expr >> count_prop)
        
        # Create more-male proposition for final counts
        more_male = MoreMale(gen)
        comparisons = []
        
        # Compare final counts: more_male <-> exists k,m: k>m & male_count(k) & female_count(m)
        for male_k in range(N + 1):
            for female_k in range(N + 1):
                if male_k > female_k:
                    final_male = male_counts[(N, male_k)]
                    final_female = female_counts[(N, female_k)]
                    comparisons.append(final_male & final_female)
        
        if comparisons:
            E.add_constraint(more_male >> Or(comparisons))
            E.add_constraint(Or(comparisons) >> more_male)
        
        return more_male

    # Process each generation after the first
    for gen in GENERATION:
        if gen == 1:  # Skip first generation
            continue
            
        people = [pid for pid in GENERATION[gen]['id'] 
                 if PEOPLE[pid]['is_blood_relative']]
        
        if people:  # Only process if generation has people
            more_male = build_recursive_count(gen, people)
            # Theory unsatisfiable if more males found
            E.add_constraint(~more_male)

    return E

def main():
    """Main program execution"""
    global GENERATION, PEOPLE, FAMILIES
    
    print("Genetic Inheritance Pattern Analyzer")
    print("-" * 35)
    
    # Load data
    use_default = input("Use default values? (y/n): ").lower() == 'y'
    if use_default:
        GENERATION, PEOPLE, FAMILIES = get_default_data()
    else:
        GENERATION, PEOPLE, FAMILIES = get_user_data()
    
    # Print initial statistics
    print("\nGeneration Statistics:")
    for gen in sorted(GENERATION.keys()):
        affected_males = sum(1 for pid in GENERATION[gen]['id'] 
                           if PEOPLE[pid]['is_male'] and 
                           PEOPLE[pid]['is_affected'] and 
                           PEOPLE[pid]['is_blood_relative'])
        affected_females = sum(1 for pid in GENERATION[gen]['id'] 
                             if not PEOPLE[pid]['is_male'] and 
                             PEOPLE[pid]['is_affected'] and 
                             PEOPLE[pid]['is_blood_relative'])
        print(f"\nGeneration {gen}:")
        print(f"Affected Males: {affected_males}")
        print(f"Affected Females: {affected_females}")
    
    # Analyze inheritance patterns
    print("\nAnalyzing inheritance patterns...")
    try:
        R = build_recessive_theory()
        X = build_xlinked_theory()
        
        R = R.compile()
        X = X.compile()
        
        is_recessive = R.satisfiable()
        is_xlinked = X.satisfiable()
        
        # Print conclusions
        print("\nResults:")
        print("-" * 20)
        print(f"Inheritance Type: {'RECESSIVE' if is_recessive else 'DOMINANT'}")
        print(f"Chromosome Type: {'X-LINKED' if is_xlinked else 'AUTOSOMAL'}")
        
        # Print evidence by generation
        print("\nEvidence by generation:")
        for gen in sorted(GENERATION.keys()):
            if gen == 1:
                continue
            
            affected_males = sum(1 for pid in GENERATION[gen]['id'] 
                               if PEOPLE[pid]['is_male'] and 
                               PEOPLE[pid]['is_affected'] and 
                               PEOPLE[pid]['is_blood_relative'])
            affected_females = sum(1 for pid in GENERATION[gen]['id'] 
                                 if not PEOPLE[pid]['is_male'] and 
                                 PEOPLE[pid]['is_affected'] and 
                                 PEOPLE[pid]['is_blood_relative'])
            
            print(f"\nGeneration {gen}:")
            print(f"Affected Males: {affected_males}")
            print(f"Affected Females: {affected_females}")
            if affected_males > affected_females:
                print("More affected males than females -> suggests autosomal")
            else:
                print("Not more affected males than females -> consistent with X-linked")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        return
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()

