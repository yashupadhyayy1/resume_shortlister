from srn_scraper import SRNScraper

def main():
    url = "https://app.synapserecruiternetwork.com/curated_list/1739556025152x298945208153276400"
    
    with SRNScraper() as scraper:
        print("\nScraping jobs...")
        jobs = scraper.scrape_jobs(url)
        print(f"\nFound {len(jobs)} jobs")
        
        if jobs:
            print("\nExample jobs found:")
            for i, job in enumerate(jobs[:3], 1):  # Show first 3 jobs
                print(f"\nJob {i}:")
                print(f"Title: {job.get('title', 'N/A')}")
                print(f"Company: {job.get('company', 'N/A')}")
                print(f"Location: {job.get('location', 'N/A')}")
                print(f"Workplace: {job.get('workplace', 'N/A')}")
                print(f"Salary: {job.get('salary', 'N/A')}")
                print("-" * 80)

if __name__ == "__main__":
    main()