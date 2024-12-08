# default_tree.py

def get_default_data():
    """Returns default pedigree tree data for testing"""
    
    generation_data = {
        1: {'id': [1, 2], 'count': 2},
        2: {'id': [3, 4, 5, 6, 7, 8], 'count': 6},
        3: {'id': [9, 10, 11, 12, 13, 14], 'count': 6}
    }
    
    people_data = {
        1: {'is_male': True, 'is_affected': False, 'is_blood_relative': True},
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
        14: {'is_male': True, 'is_affected': False, 'is_blood_relative': True}
    }
    
    families_data = [
        {'parents': [1, 2], 'children': [4, 5, 7]},
        {'parents': [3, 4], 'children': [9, 10]},
        {'parents': [5, 6], 'children': [11, 12]},
        {'parents': [7, 8], 'children': [13, 14]}
    ]
    
    return generation_data, people_data, families_data

# If you need to test the data structure directly
if __name__ == "__main__":
    GENERATION, PEOPLE, FAMILIES = get_default_data()
    
    print("\nGeneration Data:")
    print(GENERATION)
    
    print("\nPeople Data:")
    print(PEOPLE)
    
    print("\nFamilies Data:")
    print(FAMILIES)
