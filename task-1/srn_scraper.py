import logging
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)

class SRNScraper:
    def __init__(self):
        """Initialize the scraper with Chrome webdriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def parse_tech_stack(self, description_text):
        """Extract tech stack from job description"""
        common_techs = [
            'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'AWS', 
            'GCP', 'Azure', 'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB',
            'Redis', 'GraphQL', 'REST', 'FastAPI', 'Django', 'Flask', 'Vue',
            'Angular', 'Next.js', 'Express', 'Go', 'Rust', 'Java', 'C++',
            'TensorFlow', 'PyTorch', 'OpenAI', 'Git', 'CI/CD'
        ]
        found_techs = []
        for tech in common_techs:
            if tech.lower() in description_text.lower():
                found_techs.append(tech)
        return ', '.join(found_techs) if found_techs else ''

    def parse_yoe(self, description_text):
        """Extract years of experience requirement"""
        import re
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?).+?experience',
            r'(\d+)-(\d+)\s*(?:years?|yrs?).+?experience'
        ]
        for pattern in patterns:
            match = re.search(pattern, description_text.lower())
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)} - {match.group(2)} years"
                return f"{match.group(1)}+ years"
        return "Not specified"

    def extract_equity(self, text):
        """Extract equity information from text"""
        import re
        equity_patterns = [
            r'(\d+(?:\.\d+)?%?\s*-\s*\d+(?:\.\d+)?%?)\s*equity',
            r'(\d+(?:\.\d+)?%?)\s*equity'
        ]
        for pattern in equity_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
        return "Competitive"

    def extract_job_data(self, job_element):
        """Extract data from a job element"""
        job_data = {
            'source': 'SRN',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Company and basic info extraction (existing code)
            company_elem = job_element.find_element(By.CSS_SELECTOR, '.bubble-element.Text.baTaYaDaL')
            if company_elem:
                job_data['Company'] = company_elem.text.strip()
            
            role_elem = job_element.find_element(By.CSS_SELECTOR, '.bubble-element.Text.baTaYaGaR0')
            if role_elem:
                job_data['Role'] = role_elem.text.strip()
            
            location_elem = job_element.find_element(By.CSS_SELECTOR, '.bubble-element.Text.baTaYaDe')
            if location_elem:
                job_data['Locations'] = location_elem.text.strip()
            
            try:
                salary_elem = job_element.find_element(By.CSS_SELECTOR, '.bubble-element.Text.baTaYaEf')
                if salary_elem:
                    salary_text = salary_elem.text.strip()
                    job_data['Salary'] = salary_text
                    # Extract equity if mentioned in salary text
                    if 'equity' in salary_text.lower():
                        job_data['Equity'] = self.extract_equity(salary_text)
            except:
                job_data['Salary'] = 'Not specified'
            
            try:
                workplace_elem = job_element.find_element(By.CSS_SELECTOR, '.bubble-element.Text.baTaYaEs')
                if workplace_elem:
                    job_data['Workplace'] = workplace_elem.text.strip()
            except:
                job_data['Workplace'] = 'Not specified'

            # Extract additional information from job description
            description_text = job_element.text
            
            # Tech Stack
            job_data['Tech Stack'] = self.parse_tech_stack(description_text)
            
            # Years of Experience
            job_data['YOE'] = self.parse_yoe(description_text)
            
            # Industry (based on keywords)
            industries = []
            industry_keywords = {
                'AI': ['ai', 'machine learning', 'deep learning', 'ml', 'artificial intelligence'],
                'Fintech': ['fintech', 'financial', 'banking', 'payment'],
                'Enterprise': ['enterprise', 'b2b', 'saas'],
                'Data': ['data', 'analytics', 'big data'],
                'DevTools': ['developer', 'tools', 'devtools', 'dev tools'],
            }
            for industry, keywords in industry_keywords.items():
                if any(keyword in description_text.lower() for keyword in keywords):
                    industries.append(industry)
            job_data['Industry'] = ', '.join(industries) if industries else 'Tech'
            
            # Additional fields with default values
            job_data['Visa'] = 'Contact company'
            job_data['Team Size'] = 'Not specified'
            job_data['Funding'] = 'Not specified'
            job_data['Requirements'] = 'See job description'
            job_data['One liner'] = ''  # Would need specific element for this
            
            # Save HTML for reference
            job_data['html'] = job_element.get_attribute('outerHTML')
            
            return job_data
            
        except Exception as e:
            logging.error(f"Error extracting job data: {str(e)}")
            return None

    def scrape_jobs(self, url):
        """Scrape job listings from SRN website"""
        try:
            logging.info(f"Starting to scrape jobs from {url}")
            self.driver.get(url)
            time.sleep(5)  # Initial wait for content to load
            
            # Scroll to load all content
            scroll_attempts = 0
            max_attempts = 5
            
            while scroll_attempts < max_attempts:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Calculate new scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_attempts += 1
            
            # Find all job elements using the specific class
            job_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                '.clickable-element.bubble-element.Group.baTaYaDaT'
            )
            
            logging.info(f"Found {len(job_elements)} potential job elements")
            
            # Save page source for debugging
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            # Process each job element
            jobs_data = []
            for i, job_element in enumerate(job_elements, 1):
                try:
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
                    time.sleep(0.5)
                    
                    # Get job data
                    job_data = self.extract_job_data(job_element)
                    if job_data:
                        jobs_data.append(job_data)
                        logging.info(f"Scraped job {i}: {job_data.get('Role')} at {job_data.get('Company')}")
                except Exception as e:
                    logging.error(f"Error processing job element {i}: {str(e)}")
            
            # Save results
            if jobs_data:
                with open('srn_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'total_jobs': len(jobs_data),
                        'jobs': jobs_data,
                        'source_url': url
                    }, f, indent=2)
                    
                logging.info(f"Successfully scraped {len(jobs_data)} jobs")
                return jobs_data
            else:
                logging.warning("No jobs found!")
                return []
                
        except Exception as e:
            logging.error(f"Error scraping jobs: {str(e)}")
            return []
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()