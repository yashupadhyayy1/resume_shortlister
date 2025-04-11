import pandas as pd
import pdfplumber
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ResumeJobMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.jobs_df = None
        self.resumes = {}
        self.resume_dir = Path('resumes')
        
    def parse_salary(self, salary_str):
        """Parse salary string to min and max values, handling equity and special cases"""
        try:
            # Remove $ and , from the string
            salary = salary_str.replace('$', '').replace(',', '')
            
            # Handle equity or additional compensation
            if '+' in salary and 'equity' in salary.lower():
                salary = salary.split('+')[0].strip()
                
            # Check if it's a range
            if '-' in salary:
                min_sal, max_sal = salary.split('-')
                return {
                    'Min Salary': float(min_sal.strip()),
                    'Max Salary': float(max_sal.strip())
                }
            else:
                # Single number (base salary)
                base = float(salary.split()[0].strip())
                return {
                    'Min Salary': base,
                    'Max Salary': base
                }
        except:
            return {}
            
    def load_jobs(self, paraform_csv_path):
        """Load jobs from both Paraform CSV and scraped SRN data"""
        jobs_data = []
        
        # Load Paraform jobs
        try:
            paraform_df = pd.read_csv(paraform_csv_path)
            paraform_df['source'] = 'Paraform'
            jobs_data.append(paraform_df)
            logging.info(f"Loaded {len(paraform_df)} jobs from Paraform CSV")
        except Exception as e:
            logging.error(f"Error loading Paraform jobs: {e}")
        
        # Load scraped SRN jobs
        try:
            with open('srn_jobs.json', 'r') as f:
                srn_data = json.load(f)
                srn_jobs = srn_data['jobs']
                # Convert SRN job structure to match Paraform
                for job in srn_jobs:
                    # Map basic fields
                    job['Role'] = job.pop('title', '')
                    job['Company'] = job.pop('company', '')
                    job['Locations'] = job.pop('location', '')
                    
                    # Extract and standardize salary data
                    if 'salary' in job:
                        salary_data = self.parse_salary(job.pop('salary'))
                        job.update(salary_data)
                    
                    # Map and standardize other fields
                    job['Workplace'] = job.pop('workplace', '')
                    job['Tech Stack'] = job.get('Tech Stack', '')
                    job['One liner'] = job.get('One liner', '')
                    job['Equity'] = job.get('Equity', 'Not specified')
                    job['Visa'] = job.get('Visa', 'Contact company')
                    job['YOE'] = job.get('YOE', 'Not specified')
                    job['Team Size'] = job.get('Team Size', 'Not specified')
                    job['Funding'] = job.get('Funding', 'Not specified')
                    job['Requirements'] = job.get('Requirements', '')
                    job['Industry'] = job.get('Industry', 'Tech')
                    
                srn_df = pd.DataFrame(srn_jobs)
                srn_df['source'] = 'SRN'
                jobs_data.append(srn_df)
                logging.info(f"Loaded {len(srn_df)} jobs from SRN")
        except Exception as e:
            logging.error(f"Error loading SRN jobs: {e}")
        
        # Combine all jobs
        if jobs_data:
            self.jobs_df = pd.concat(jobs_data, ignore_index=True)
            
            # Create combined text for matching - using all relevant fields
            self.jobs_df['combined_text'] = self.jobs_df.apply(
                lambda x: f"{x.get('Role', '')} {x.get('Tech Stack', '')} {x.get('One liner', '')} "
                         f"{x.get('Requirements', '')} {x.get('Industry', '')} {x.get('Workplace', '')} "
                         f"{x.get('YOE', '')}",
                axis=1
            )
            
            # Generate embeddings for matching
            self.job_embeddings = self.model.encode(self.jobs_df['combined_text'].tolist())
            logging.info(f"Successfully processed {len(self.jobs_df)} total jobs")
        else:
            raise Exception("No jobs could be loaded from any source")
            
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return None
    
    def load_resumes(self):
        """Load all resumes from the resumes directory"""
        if not self.resume_dir.exists():
            logging.error(f"Resume directory {self.resume_dir} does not exist!")
            return False
            
        resume_count = 0
        for file_path in self.resume_dir.glob('*.pdf'):
            try:
                resume_text = self.extract_text_from_pdf(file_path)
                if resume_text:
                    self.resumes[file_path.name] = resume_text
                    resume_count += 1
                    logging.info(f"Successfully loaded resume: {file_path.name}")
            except Exception as e:
                logging.error(f"Error loading resume {file_path}: {str(e)}")
                
        if resume_count == 0:
            logging.warning("No resumes found in the resumes directory!")
            return False
            
        logging.info(f"Successfully loaded {resume_count} resumes")
        return True
                
    def calculate_match_score(self, resume_text, job_embedding):
        """Calculate match score between resume and job"""
        resume_embedding = self.model.encode([resume_text])
        similarity = cosine_similarity(resume_embedding, job_embedding.reshape(1, -1))[0][0]
        # Convert similarity to 1-10 scale
        return round(similarity * 10, 1)
    
    def analyze_tech_stack_match(self, resume_text, job):
        """Analyze how well the resume matches the job's tech stack"""
        if pd.isna(job.get('Tech Stack')):
            return []
            
        tech_stack = job['Tech Stack'].split(', ')
        matches = []
        for tech in tech_stack:
            if tech.lower() in resume_text.lower():
                matches.append(tech)
        return matches
    
    def analyze_experience_match(self, resume_text, job):
        """Analyze years of experience match"""
        if pd.isna(job.get('YOE')):
            return None
            
        yoe_required = str(job['YOE'])
        try:
            if '+' in yoe_required:
                min_years = float(yoe_required.replace('years', '').replace('year', '').replace('+', '').strip())
                return f"Requires {min_years}+ years of experience"
            elif '-' in yoe_required:
                years_range = [float(y.replace('years', '').replace('year', '').strip()) 
                             for y in yoe_required.split('-')]
                return f"Requires {years_range[0]}-{years_range[1]} years of experience"
            else:
                years = float(yoe_required.replace('years', '').replace('year', '').strip())
                return f"Requires {years} years of experience"
        except (ValueError, IndexError):
            return f"Experience requirement: {yoe_required}"
    
    def find_top_matches(self, resume_text, n=2):
        """Find top n job matches for a resume"""
        resume_embedding = self.model.encode([resume_text])
        similarities = cosine_similarity(resume_embedding, self.job_embeddings)[0]
        top_indices = similarities.argsort()[-n:][::-1]
        
        matches = []
        for idx in top_indices:
            job = self.jobs_df.iloc[idx]
            score = round(similarities[idx] * 10, 1)
            tech_matches = self.analyze_tech_stack_match(resume_text, job)
            exp_requirement = self.analyze_experience_match(resume_text, job)
            
            # Format salary range with proper handling of missing/invalid values
            min_salary = job.get('Min Salary')
            max_salary = job.get('Max Salary')
            if pd.isna(min_salary) or pd.isna(max_salary):
                salary_range = "Salary not specified"
            else:
                try:
                    salary_range = f"${int(min_salary):,} - ${int(max_salary):,}"
                except (ValueError, TypeError):
                    salary_range = "Salary format error"

            matches.append({
                'company': job['Company'],
                'role': job['Role'],
                'score': score,
                'tech_matches': tech_matches,
                'experience_req': exp_requirement,
                'location': job.get('Locations', 'Not specified'),
                'workplace': job.get('Workplace', 'Not specified'),
                'source': job.get('source', 'Unknown'),
                'tech_stack': job.get('Tech Stack', ''),
                'one_liner': job.get('One liner', ''),
                'salary_range': salary_range,
                'equity': job.get('Equity', 'Not specified'),
                'visa': job.get('Visa', 'Contact company'),
                'team_size': job.get('Team Size', 'Not specified'),
                'funding': job.get('Funding', 'Not specified'),
                'industry': job.get('Industry', 'Tech'),
                'requirements': job.get('Requirements', ''),
                'justification': self.generate_justification(resume_text, job, tech_matches, exp_requirement)
            })
        return matches
    
    def generate_justification(self, resume_text, job, tech_matches, exp_requirement):
        """Generate a detailed justification for the match"""
        justification_points = []
        
        if tech_matches:
            justification_points.append(f"Technical match: {', '.join(tech_matches)}")
        
        if exp_requirement:
            justification_points.append(exp_requirement)
            
        if job.get('Industry'):
            justification_points.append(f"Industry: {job['Industry']}")
            
        source = job.get('source', 'Unknown')
        justification_points.append(f"Source: {source}")
            
        if not justification_points:
            justification_points.append("General skill set and experience match")
            
        return " | ".join(justification_points)
    
    def match_all_resumes(self):
        """Match all loaded resumes to jobs"""
        if not self.resumes:
            logging.error("No resumes loaded! Please add PDF resumes to the 'resumes' folder.")
            return []
            
        results = []
        for resume_name, resume_text in self.resumes.items():
            matches = self.find_top_matches(resume_text)
            results.append({
                'resume_name': resume_name,
                'matches': matches
            })
        return results

def print_results(results):
    """Print results in a concise tabular format"""
    if not results:
        print("\nNo results to display. Please make sure there are PDF resumes in the 'resumes' folder.")
        return
        
    print("\nRESUME MATCHING RESULTS")
    print("=" * 120)
    print(f"{'Resume Name':<30} | {'Company & Role':<35} | {'Source':<8} | {'Score':<5} | {'Match Reasoning'}")
    print("-" * 120)
    
    for result in results:
        resume_name = result['resume_name'][:27] + "..." if len(result['resume_name']) > 30 else result['resume_name']
        
        # Print each match for this resume
        for i, match in enumerate(result['matches']):
            if i == 0:
                # First match - print with resume name
                print(f"{resume_name:<30} | ", end="")
            else:
                # Second match - indent under same resume
                print(f"{'→':<30} | ", end="")
                
            company_role = f"{match['company']}: {match['role']}"
            company_role = company_role[:32] + "..." if len(company_role) > 35 else company_role
            
            source = match['source'][:8]
            score = f"{match['score']}"
            tech_matches = f"Matches: {', '.join(match['tech_matches'])[:50]}" if match['tech_matches'] else ""
            exp = match['experience_req'].split(':')[-1].strip() if match['experience_req'] else ""
            
            justification = []
            if tech_matches:
                justification.append(tech_matches)
            if exp:
                justification.append(exp)
            justification = " | ".join(justification)
            
            print(f"{company_role:<35} | {source:<8} | {score:<5} | {justification}")
        print("-" * 120)

def main():
    try:
        matcher = ResumeJobMatcher()
        
        # Load jobs from Paraform CSV
        matcher.load_jobs('Paraform_Jobs - S1.csv')
        
        # Load resumes from the resumes directory
        if matcher.load_resumes():
            # Perform matching
            results = matcher.match_all_resumes()
            
            # Print results
            print_results(results)
        else:
            print("\nPlease add PDF resumes to the 'resumes' folder and run the script again.")
            print("Expected location:", Path('resumes').absolute())
            
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()