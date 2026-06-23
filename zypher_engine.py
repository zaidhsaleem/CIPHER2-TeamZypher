import json
import random
import copy
import numpy as np
from scipy.optimize import linear_sum_assignment

# Hardcoded projects for the MVP prototype
PROJECTS = ["Project_Alpha", "Project_Beta", "Project_Gamma"]

def load_students(filename):
    with open(filename, "r") as file:
        return json.load(file)

def calculate_total_skill(student):
    return sum(student["skills"].values())

def greedy_seed_teams(students):
    """Sorts by skill, enforces N=5 capacity, and attempts to avoid conflicts."""
    sorted_students = sorted(
        students,
        key=lambda s: (calculate_total_skill(s), s["availability"]),
        reverse=True
    )

    team1, team2 = [], []

    for student in sorted_students:
        t1_ids = [s["id"] for s in team1]
        t2_ids = [s["id"] for s in team2]

        t1_conflict = any(b in t1_ids for b in student["blacklist"]) or any(student["id"] in s["blacklist"] for s in team1)
        t2_conflict = any(b in t2_ids for b in student["blacklist"]) or any(student["id"] in s["blacklist"] for s in team2)

        # Enforce hard capacity constraint (N=5)
        t1_full = len(team1) >= 5
        t2_full = len(team2) >= 5

        # Route based on availability and conflicts, but capacity is absolute
        if not t1_full and (len(team1) <= len(team2) or t2_full):
            if not t1_conflict:
                team1.append(student)
            elif not t2_full:
                team2.append(student)
            else:
                team1.append(student) # Force placement if T2 is full
        else:
            if not t2_conflict and not t2_full:
                team2.append(student)
            elif not t1_full:
                team1.append(student)
            else:
                team2.append(student) # Force placement if T1 is full
                
    return [team1, team2]

def check_blacklists(team):
    """Scans for hard constraint peer conflicts."""
    conflicts = []
    team_ids = [student["id"] for student in team]
    for student in team:
        for blocked_id in student["blacklist"]:
            if blocked_id in team_ids:
                conflicts.append(f"⚠️ HARD CONSTRAINT: {student['name']} blacklisted {blocked_id}!")
    return conflicts

def calculate_project_preference_score(team, project):
    """Calculates Pref(T) step-function score (1st=1.0, 2nd=0.6, 3rd=0.3)"""
    score_map = {0: 1.0, 1: 0.6, 2: 0.3}
    total_score = 0
    
    for student in team:
        if project in student["preferences"]:
            pref_rank = student["preferences"].index(project)
            total_score += score_map.get(pref_rank, 0.0)
            
    # Return average preference score for the team
    return total_score / len(team)
def calculate_variance_score(teams):
    """Calculates a global score based on workload and skill variance (closer to 0 is better)."""
    t1_skill = sum(calculate_total_skill(s) for s in teams[0])
    t2_skill = sum(calculate_total_skill(s) for s in teams[1])
    
    t1_hours = sum(s["availability"] for s in teams[0])
    t2_hours = sum(s["availability"] for s in teams[1])
    
    skill_diff = abs(t1_skill - t2_skill)
    hours_diff = abs(t1_hours - t2_hours)
    
    return -(skill_diff * 2 + hours_diff)

def stochastic_swap_loop(teams):
    """O(K) Stochastic Swap Optimization to balance teams without breaking constraints."""
    print("\n🔄 Running Phase 2: Stochastic Swap Optimization...")
    
    current_score = calculate_variance_score(teams)
    no_improve = 0
    k_limit = 5000
    iterations = 0

    while no_improve < 500 and iterations < k_limit:
        iterations += 1
        
        t1_idx = random.randint(0, len(teams[0]) - 1)
        t2_idx = random.randint(0, len(teams[1]) - 1)
        
        s1 = teams[0][t1_idx]
        s2 = teams[1][t2_idx]
        
        test_t1 = copy.deepcopy(teams[0])
        test_t2 = copy.deepcopy(teams[1])
        
        test_t1[t1_idx] = s2
        test_t2[t2_idx] = s1
        
        t1_conflicts = check_blacklists(test_t1)
        t2_conflicts = check_blacklists(test_t2)
        
        if not t1_conflicts and not t2_conflicts:
            new_score = calculate_variance_score([test_t1, test_t2])
            
            if new_score > current_score:
                teams[0] = test_t1
                teams[1] = test_t2
                current_score = new_score
                no_improve = 0
            else:
                no_improve += 1
        else:
            no_improve += 1

    print(f"✅ Optimization settled after {iterations} iterations.")
    return teams

def assign_projects_hungarian(teams, projects):
    """Uses scipy's linear_sum_assignment to mathematically optimize 1:1 project allocation."""
    # Build the Score Matrix S(T,P)
    # Note: scipy minimizes cost, but we want to maximize score. 
    # Therefore, we make the scores negative.
    cost_matrix = []
    
    for team in teams:
        team_row = []
        for project in projects:
            score = calculate_project_preference_score(team, project)
            team_row.append(-score) # Negative for minimization
        cost_matrix.append(team_row)
        
    cost_matrix = np.array(cost_matrix)
    
    # Run the Hungarian Algorithm O(T^3)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    # Map results back to team indices and project names
    assignments = {}
    for i in range(len(row_ind)):
        team_idx = row_ind[i]
        project_idx = col_ind[i]
        assignments[f"TEAM {team_idx + 1}"] = projects[project_idx]
        
    return assignments

def print_final_report(teams, project_assignments):
    """Generates the final comprehensive CLI output for the judges."""
    print("\n" + "="*50)
    print("🚀 ZYPHER ENGINE: BATCH MATCHING COMPLETE 🚀")
    print("="*50)
    
    for idx, team in enumerate(teams):
        team_name = f"TEAM {idx + 1}"
        assigned_project = project_assignments[team_name]
        
        print(f"\n📂 {team_name} | Assigned Project: {assigned_project}")
        print("-" * 50)
        
        total_skill = 0
        total_hours = 0
        
        for student in team:
            skill = calculate_total_skill(student)
            total_skill += skill
            total_hours += student["availability"]
            print(f"  👤 {student['id']} - {student['name']:<8} | Skill: {skill:<2} | Avail: {student['availability']}h")
            
        print("-" * 50)
        print(f"📊 Metrics    : Total Skill: {total_skill} | Total Hours: {total_hours}h")
        
        conflicts = check_blacklists(team)
        if conflicts:
            for c in conflicts: print(f"🚨 {c}")
        else:
            print("✅ Constraints: No peer conflicts detected.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Ingest Data
    students = load_students("students.json")
    
    # 2. Greedy Seed 
    teams = greedy_seed_teams(students)
    
    # 3. Phase 2: Stochastic Swap Loop
    teams = stochastic_swap_loop(teams)
    
    # 4. Hungarian Matching 
    project_assignments = assign_projects_hungarian(teams, PROJECTS)
    
    # 5. Output Result
    print_final_report(teams, project_assignments)
