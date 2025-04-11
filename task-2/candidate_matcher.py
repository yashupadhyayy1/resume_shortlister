import pandas as pd
import numpy as np
from datetime import datetime
import re

def load_candidates(csv_path):
    return pd.read_csv(csv_path)

def calculate_location_score(location):
    """Higher score for NY-based candidates"""
    if 'New York' in location:
        return 1.0
    elif 'California' in location or 'New Jersey' in location:  # Nearby states or tech hubs
        return 0.8
    return 0.6

def calculate_title_score(title, company):
    """Score based on current title relevance"""
    title = title.lower()
    company = company.lower()
    score = 0
    
    # Base title scoring
    if 'founding' in title:
        score += 1.0
    elif 'staff' in title:
        score += 0.9
    elif 'senior' in title:
        score += 0.8
    elif 'software engineer' in title:
        score += 0.7
        
    # Role type bonus
    if any(x in title for x in ['ai', 'ml', 'machine learning']):
        score += 0.3
    if 'full stack' in title or 'fullstack' in title:
        score += 0.2
        
    # Company size/stage bonus (prefer startup/smaller company experience)
    startup_keywords = ['founding', 'founder', 'early']
    if any(kw in title.lower() for kw in startup_keywords):
        score += 0.2
        
    # AI company bonus
    ai_companies = ['waymo', 'scale', 'glean', 'openai', 'anthropic']
    if any(co in company for co in ai_companies):
        score += 0.2
        
    return min(score, 1.0)

def calculate_tech_stack_score(title, company):
    """Score based on likelihood of having Probook's required tech stack"""
    score = 0.7  # Base score
    
    # Tech stack keywords
    tech_stack = {
        'aws': ['aws', 'amazon', 'cloud'],
        'gcp': ['gcp', 'google cloud'],
        'python': ['python', 'django', 'flask'],
        'react': ['react', 'frontend', 'web'],
        'typescript': ['typescript', 'javascript', 'frontend']
    }
    
    text_to_search = f"{title} {company}".lower()
    
    # Score each tech stack component
    for tech, keywords in tech_stack.items():
        if any(kw in text_to_search for kw in keywords):
            score += 0.06  # Up to 0.3 bonus for tech stack matches
            
    return min(score, 1.0)

def calculate_github_score(github):
    """Score based on having a GitHub presence"""
    return 1.0 if isinstance(github, str) and len(github) > 0 else 0.0

def calculate_education_score(education):
    """Score based on education quality"""
    top_schools = ['stanford', 'mit', 'berkeley', 'carnegie mellon', 'princeton', 'harvard', 'yale']
    good_schools = ['cornell', 'columbia', 'ucla', 'ucsd', 'university of michigan', 'georgia tech', 'caltech']
    
    education = str(education).lower()
    score = 0.7  # Base score
    
    if any(school in education for school in top_schools):
        score = 1.0
    elif any(school in education for school in good_schools):
        score = 0.9
        
    return score

def calculate_startup_score(title, company):
    """Score based on startup and founding experience"""
    score = 0.7  # Base score
    
    # Founding experience
    if 'founding' in title.lower():
        score += 0.3
        
    # Early-stage startup experience
    startup_indicators = ['founding', 'founder', 'early', 'seed', 'series a']
    if any(ind in f"{title} {company}".lower() for ind in startup_indicators):
        score += 0.2
        
    # Small company experience (more likely to be adaptable)
    big_tech = ['google', 'meta', 'amazon', 'microsoft', 'apple']
    if not any(co in company.lower() for co in big_tech):
        score += 0.1
        
    return min(score, 1.0)

def simulate_linkedin_data(title, company, education):
    """Simulate additional LinkedIn profile data"""
    # Simulate years of experience based on education dates
    education = str(education)
    years_pattern = r'(\d{4})'
    years = re.findall(years_pattern, education)
    grad_year = min([int(y) for y in years]) if years else 2020
    years_exp = datetime.now().year - grad_year
    
    # Simulate previous roles based on current role
    current_level = get_role_level(title)
    prev_roles = generate_career_path(current_level, years_exp)
    
    # Simulate company sizes
    big_companies = ['Google', 'Meta', 'Amazon', 'Microsoft', 'Apple', 'Waymo']
    current_company_size = 'large' if any(co.lower() in company.lower() for co in big_companies) else 'startup'
    
    # Simulate relevant skills based on role
    skills = generate_skill_set(title, company)
    
    return {
        'years_experience': years_exp,
        'previous_roles': prev_roles,
        'company_sizes': [current_company_size],
        'skills': skills
    }

def get_role_level(title):
    """Determine role level from title"""
    title = title.lower()
    if 'founding' in title or 'founder' in title:
        return 4
    elif 'staff' in title or 'principal' in title:
        return 3
    elif 'senior' in title or 'lead' in title:
        return 2
    return 1

def generate_career_path(current_level, years_exp):
    """Generate likely previous roles based on current level"""
    roles = []
    if current_level >= 4:  # Founding Engineer
        roles = ['Senior Software Engineer', 'Software Engineer']
    elif current_level == 3:  # Staff
        roles = ['Senior Software Engineer', 'Software Engineer']
    elif current_level == 2:  # Senior
        roles = ['Software Engineer']
    return roles[:min(len(roles), years_exp // 2)]

def generate_skill_set(title, company):
    """Generate relevant skills based on role and company"""
    skills = set()
    
    # Base skills
    base_skills = {'Git', 'CI/CD', 'System Design'}
    skills.update(base_skills)
    
    # Role-specific skills
    title = title.lower()
    company = company.lower()
    
    if 'frontend' in title or 'full stack' in title:
        skills.update({'React', 'TypeScript', 'JavaScript', 'HTML/CSS'})
    if 'backend' in title or 'full stack' in title:
        skills.update({'Python', 'AWS', 'GCP', 'Databases'})
    if 'ai' in title or 'ml' in title or any(co in company for co in ['waymo', 'scale', 'openai']):
        skills.update({'Machine Learning', 'PyTorch', 'TensorFlow'})
    if 'founding' in title:
        skills.update({'Architecture', 'Team Leadership', 'Product Strategy'})
        
    return list(skills)

def calculate_experience_score(simulated_data):
    """Score based on years and quality of experience"""
    score = 0.7  # Base score
    years_exp = simulated_data['years_experience']
    
    # Years of experience scoring
    if years_exp >= 5:
        score += 0.2
    elif years_exp >= 3:
        score += 0.1
        
    # Previous roles progression
    if len(simulated_data['previous_roles']) >= 2:
        score += 0.1
        
    return min(score, 1.0)

def calculate_skills_match(simulated_data, required_skills):
    """Score based on skill match with requirements"""
    skills = set(skill.lower() for skill in simulated_data['skills'])
    required = set(skill.lower() for skill in required_skills)
    
    match_score = len(skills.intersection(required)) / len(required)
    return min(0.7 + match_score * 0.3, 1.0)

def rank_candidates(df):
    """Calculate final scores and rank candidates"""
    # Probook AI required skills
    required_skills = ['Python', 'AWS', 'GCP', 'React', 'TypeScript', 'System Design']
    
    scores = []
    for _, row in df.iterrows():
        # Simulate additional LinkedIn data
        simulated_data = simulate_linkedin_data(
            row['Current Title'], 
            row['Current Org Name'], 
            row['Education']
        )
        
        # Calculate individual component scores
        location_score = calculate_location_score(row['Location'])
        title_score = calculate_title_score(row['Current Title'], row['Current Org Name'])
        experience_score = calculate_experience_score(simulated_data)
        skills_score = calculate_skills_match(simulated_data, required_skills)
        github_score = calculate_github_score(row['GitHub'])
        education_score = calculate_education_score(row['Education'])
        startup_score = calculate_startup_score(row['Current Title'], row['Current Org Name'])
        
        # Weighted final score
        final_score = (
            location_score * 0.15 +      # Location weight
            title_score * 0.15 +         # Current role weight
            experience_score * 0.20 +     # Experience weight
            skills_score * 0.20 +        # Skills match weight
            github_score * 0.10 +        # GitHub presence weight
            education_score * 0.10 +     # Education weight
            startup_score * 0.10         # Startup experience weight
        ) * 10  # Scale to 0-10
        
        scores.append({
            'Name': f"{row['First name']} {row['Last name']}",
            'LinkedIn': row['LinkedIn'],
            'Score': round(final_score, 1),
            'Current Role': f"{row['Current Title']} @ {row['Current Org Name']}",
            'Location': row['Location'],
            'Years Experience': simulated_data['years_experience'],
            'Skills': ', '.join(simulated_data['skills'][:5]),  # Show top 5 skills
            'Why': generate_justification(
                row, 
                location_score,
                title_score,
                experience_score,
                skills_score,
                github_score,
                education_score,
                startup_score,
                simulated_data
            )
        })
    
    return sorted(scores, key=lambda x: x['Score'], reverse=True)

def generate_justification(row, location_score, title_score, experience_score, 
                         skills_score, github_score, education_score, 
                         startup_score, simulated_data):
    """Generate detailed explanation for the candidate's score"""
    reasons = []
    
    # Location
    if location_score > 0.8:
        reasons.append("Location ideal for role")
    elif location_score > 0.6:
        reasons.append("Location workable")
    
    # Role and Experience
    if experience_score > 0.8:
        reasons.append(f"{simulated_data['years_experience']}+ years relevant experience")
    if title_score > 0.8:
        reasons.append("Strong current role")
    if 'founding' in row['Current Title'].lower():
        reasons.append("Previous founding experience")
        
    # Skills and Tech
    if skills_score > 0.8:
        reasons.append("Excellent skill match")
    elif skills_score > 0.7:
        reasons.append("Good technical alignment")
    
    # Additional Qualifiers
    if github_score > 0:
        reasons.append("Active GitHub presence")
    if education_score > 0.9:
        reasons.append("Top-tier education")
    if startup_score > 0.8:
        reasons.append("Strong startup background")
    
    return " | ".join(reasons)

def format_linkedin_message(candidate):
    """Generate a personalized 250-char LinkedIn message"""
    company = candidate['Current Role'].split('@')[1].strip()
    exp_years = f"{candidate['Years Experience']}+"
    return f"Hi {candidate['Name'].split()[0]}, I'm reaching out about a Founding Engineer role at Probook AI. Given your {exp_years} years of experience at {company} and background in {candidate['Skills'].split(',')[0]}, I'd love to chat."

def main():
    df = load_candidates('e:/resume_shortlister/task-2/JuiceboxExport_1743820890826.csv')
    top_candidates = rank_candidates(df)[:10]
    
    print("\nTop Candidates for Probook AI Founding Engineer Role:")
    print("=" * 80)
    
    print("\nRole Requirements:")
    print("- Tech Stack: AWS, GCP, Python, React, TypeScript")
    print("- Location: New York (On-site)")
    print("- Experience: 3+ years")
    print("- Team Size: 8 people")
    print("- Visa: TN visas accepted (no H1B)")
    print("=" * 80)
    
    # Print detailed candidate information
    for i, candidate in enumerate(top_candidates[:5], 1):
        print(f"\n{i}. {candidate['Name']}")
        print(f"Score: {candidate['Score']}/10")
        print(f"Current: {candidate['Current Role']}")
        print(f"Experience: {candidate['Years Experience']}+ years")
        print(f"Key Skills: {candidate['Skills']}")
        print(f"LinkedIn: {candidate['LinkedIn']}")
        print(f"Why: {candidate['Why']}")
        if i == 1:
            print("\nSample LinkedIn message:")
            print(format_linkedin_message(candidate))
        print("-" * 80)

if __name__ == "__main__":
    main()