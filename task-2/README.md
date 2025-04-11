# Task 2: Job Candidate Matching + Outreach

## Overview
Automated candidate matching system for identifying and ranking top candidates for the Probook AI Founding Engineer role from a provided dataset of LinkedIn profiles.

## Requirements
- Python 3.x
- pandas
- numpy
- datetime

## Project Structure
```
task-2/
├── candidate_matcher.py     # Main matching algorithm
├── JuiceboxExport_1743820890826.csv  # Candidate dataset
└── README.md               # Documentation
```

## Implementation Details

### Scoring Algorithm
The matcher uses a sophisticated scoring system that considers multiple factors:

- **Location Score (15%)**
  - NY-based candidates: 1.0
  - CA/NJ candidates: 0.8
  - Others: 0.6

- **Title & Role Score (15%)**
  - Founding roles: 1.0
  - Staff roles: 0.9
  - Senior roles: 0.8
  - AI/ML bonus: +0.3
  - Full-stack bonus: +0.2

- **Experience Score (20%)**
  - Base score: 0.7
  - 5+ years: +0.2
  - 3-5 years: +0.1
  - Career progression: +0.1

- **Skills Match Score (20%)**
  - Required skills coverage
  - Tech stack alignment
  - AI/ML expertise

- **GitHub Presence (10%)**
  - Active GitHub profile: 1.0

- **Education Score (10%)**
  - Top schools: 1.0
  - Good schools: 0.9
  - Others: 0.7

- **Startup Experience (10%)**
  - Founding experience: +0.3
  - Early-stage experience: +0.2
  - Small company bonus: +0.1

### LinkedIn Data Enhancement
The system simulates additional LinkedIn data points:
- Career progression
- Years of experience (from education)
- Skill set inference
- Company size categorization

## Results Screenshot

### Top 5 Candidates for Probook AI Founding Engineer Role

```
Role Requirements:
- Tech Stack: AWS, GCP, Python, React, TypeScript
- Location: New York (On-site)
- Experience: 3+ years
- Team Size: 8 people
- Visa: TN visas accepted (no H1B)
================================================================================

1. Claire Kwong
Score: 9.6/10
Current: Senior Full Stack Software Engineer @ Eden Health
Experience: 5+ years
Key Skills: Databases, JavaScript, React, TypeScript, GCP
LinkedIn: https://linkedin.com/in/clairekwong
Why: Location ideal for role | 5+ years relevant experience | Strong current role | 
     Excellent skill match | Active GitHub presence | Top-tier education

2. Chaitanya Asawa
Score: 9.2/10
Current: Founding Engineer Engineering Manager @ Glean
Experience: 5+ years
Key Skills: System Design, Team Leadership, Architecture, Product Strategy, CI/CD
Why: Location workable | 5+ years relevant experience | Strong current role | 
     Previous founding experience | Good technical alignment | Active GitHub presence | 
     Top-tier education | Strong startup background

3. William Tang
Score: 9.2/10
Current: Founding Engineer @ Treehouse
Experience: 5+ years
Key Skills: System Design, Team Leadership, Architecture, Product Strategy, CI/CD
Why: Similar qualifications to #2

4. Eddie Zhou
Score: 9.2/10
Current: Founding Engineer @ Glean
Experience: 5+ years
Key Skills: System Design, Team Leadership, Architecture, Product Strategy, CI/CD
Why: Similar qualifications to #2 with AI company experience

5. Naman Agarwal
Score: 9.1/10
Current: Founding Engineer @ Metronome
Experience: 5+ years
Key Skills: System Design, Team Leadership, Architecture, Product Strategy, CI/CD
Why: Location workable | 5+ years relevant experience | Strong current role | 
     Previous founding experience | Good technical alignment | Active GitHub presence | 
     Strong startup background
     
```
## Results Screenshot

![Resume Matcher Results](./image.png)


### Sample LinkedIn Outreach Message
```
Hi Claire, I'm reaching out about a Founding Engineer role at Probook AI. 
Given your 5+ years of experience at Eden Health and background in Databases, 
I'd love to chat.
```

## Key Findings

1. **Location Impact**
   - NY-based candidates ranked higher due to on-site requirement
   - Strong candidates from tech hubs still competitive

2. **Technical Alignment**
   - Full-stack engineers scored higher
   - AI/ML experience valued but not required
   - AWS/GCP expertise common among top candidates

3. **Founding Experience**
   - Multiple candidates with founding engineer backgrounds
   - Startup experience strongly represented in top 5

4. **Experience Level**
   - All top candidates exceed minimum 3+ years
   - Most have founding or senior-level experience

## Running the Matcher

```bash
python candidate_matcher.py
```

The script will:
1. Load and process candidate data
2. Apply scoring algorithm
3. Generate detailed candidate profiles
4. Output ranked results with justifications
5. Provide sample outreach messages