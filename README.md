# CIPHER 2.0 - Team Zypher Prototype

This repository contains the functional Phase 1 MVP for **Zypher: Intelligent Cohort Team Formation & Task Allocation System**.

## Files Included
* `zypher_engine.py`: The core algorithm engine handling Greedy Seeding, Constraint Detection, and Hungarian Bipartite Matching.
* `students.json`: A mock dataset of 10 students, including self-reported skill ratings, project preferences, availability, and hard-constraint peer blacklists.

## How to Run the Prototype

**1. Install Prerequisites**
The allocation engine requires Python's scientific libraries to execute the optimal Hungarian matching logic. Run the following command in your terminal:

pip install numpy scipy

**2. Execute the Engine**
Ensure both files are in the same directory, then run the script:

python zypher_engine.py

**3. Expected Output**
The terminal will output a finalized batch-matching report demonstrating:
* Two perfectly balanced teams of 5 members.
* Optimal project assignments with no overlaps.
* Real-time constraint verification (flagging intentional peer conflicts while enforcing strict capacity limits).
