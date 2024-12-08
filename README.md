# Genetic Inheritance Pattern Analyzer
### CISC/CMPE 204 Modelling Project

## Overview
This project implements a Boolean satisfiability (SAT) solver to analyze genetic inheritance patterns in family pedigrees. It determines whether traits follow recessive/dominant and X-linked/autosomal inheritance by examining multi-generational family data.

## Theory and Analysis Approach

### Default Theory Constraints
The program builds two separate theories to test inheritance patterns:

1. **Recessive Theory**
   - Tests for recessive inheritance by default
   - If satisfiable: trait is RECESSIVE
   - If unsatisfiable: trait is DOMINANT
   - Key test: If unaffected parents have affected children, must be recessive

2. **X-linked Theory**
   - Tests for X-linked inheritance by default
   - If satisfiable: trait is X-LINKED
   - If unsatisfiable: trait is AUTOSOMAL
   - Key test: No generation should have more affected males than females

### Determining Inheritance Pattern
Based on the satisfiability of both theories:

```
Recessive Theory | X-linked Theory | Inheritance Pattern
----------------|-----------------|-------------------
Satisfiable     | Satisfiable     | Recessive, X-linked
Satisfiable     | Unsatisfiable   | Recessive, Autosomal
Unsatisfiable   | Satisfiable     | Dominant, X-linked
Unsatisfiable   | Unsatisfiable   | Dominant, Autosomal
```

## Repository Structure

### Required Components
* `documents/`: Contains draft and final submission materials
* `run.py`: Core implementation of genetic theories
* `test.py`: Verification script for submission requirements
* `default_tree.py`: Default pedigree chart data
* `pedigree_chart.svg`: svg representation of default pedigree chart 


## Implementation Details

### Key Data Structures
```python
# People Dictionary
PEOPLE = {
    id: {
        'is_male': bool,
        'is_affected': bool,
        'is_blood_relative': bool
    }
}

# Generation Dictionary
GENERATION = {
    gen_number: {
        'id': [person_ids],
        'count': total_count
    }
}
# Families Dictionary
FAMILIES = {
    family_id: {
        'parents': (parent1_id, parent2_id), # Tuple of parent IDs (None if no parents)
        'children': [child_ids],            # List of child IDs in this family
        'generation': gen_number,           # The generation number this family belongs to
        'bloodline': bool                   # True if this family is part of the primary bloodline
    }
}

```

### Recursive Counting Implementation
The X-linked theory uses recursive counting where:
```python
n(i,k) represents k affected in first i people:
- Base cases: n(1,0) and n(1,1)
- Recursive: n(i,k) <-> ((n(i-1,k-1) & affected(i)) | (n(i-1,k) & !affected(i)))
```

## Running the Project

### With Docker (Recommended)
1. Build the Docker image:
```bash
docker build -t cisc204 .
```

2. Run the container:
```bash
# Mac/Linux
docker run -it -v $(pwd):/PROJECT cisc204 /bin/bash

# Windows PowerShell
docker run -it -v ${PWD}:/PROJECT cisc204 /bin/bash

# Windows CMD
docker run -it -v "%cd%":/PROJECT cisc204 /bin/bash
```

3. Inside container, run:
```bash
python3 /PROJECT/run.py
```

### Platform-Specific Notes

#### Mac M1/M2 Users
Add platform parameter:
```bash
docker build --platform linux/x86_64 -t cisc204 .
docker run --platform linux/x86_64 -it -v $(pwd):/PROJECT cisc204 /bin/bash
```

#### Paths with Spaces
Use quotes:
```bash
docker run -it -v "%cd%":/PROJECT cisc204 /bin/bash
```

## Example Output
```
Genetic Inheritance Pattern Analyzer
-----------------------------------

Generation Statistics:
Generation 1:
- Affected Males: 0
- Affected Females: 1

Generation 2:
- Affected Males: 2
- Affected Females: 0

Results:
--------------------
Inheritance Type: RECESSIVE
Chromosome Type: AUTOSOMAL

Evidence:
- Unaffected parents have affected children
- Male-to-male transmission observed
```

## Technical Limitations
- Binary gender model for X-linked analysis
- Single trait analysis only
- Requires complete family data
- Cannot handle:
  - Incomplete penetrance
  - Variable expressivity
  - Multiple trait interactions

## Future Development
- Multiple trait analysis
- Incomplete penetrance support
- Visual pedigree representation
- Statistical confidence measures
- Data import/export functionality
  
## Authors
- Nicole Wu
    - Email: 22ll20@queensu.ca
- Sophie Liang
    - Email: 22whr@queensu.ca
- Tracy Chan
    - Email: 22thb2@queensu.ca
- Annika Tran
    - Email: 23lm5@queensu.ca
## Acknowledgments
- CISC/CMPE 204 course materials
- Bauhaus SAT solver library
- NNF library

