import argparse
import sys
from datetime import datetime
from research_sources import research_and_update_sources
from generate_ideas import generate_and_email_ideas, get_fallback_ideas
from email_sender import generate_html_email, send_email

def main():
    parser = argparse.ArgumentParser(description="Test runner for Project Idea Automation")
    parser.add_argument("--test-email", action="store_true", help="Format and send/save a test HTML email using mock ideas")
    parser.add_argument("--test-research", action="store_true", help="Perform source research immediately and update sources.json")
    parser.add_argument("--test-ideas", action="store_true", help="Generate 5 new project ideas immediately and send/save the email")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    if args.test_email:
        print("--- Testing Email Formatting and Delivery ---")
        mock_ideas = get_fallback_ideas()[:5]
        html_content = generate_html_email(mock_ideas)
        subject = f"🧪 TEST: Top 5 Project Ideas - {datetime.now().strftime('%b %d, %Y')}"
        success = send_email(subject, html_content)
        if success:
            print("Test email sent successfully via SMTP!")
        else:
            print("SMTP delivery not completed. Check config or look at the local HTML copy in 'emails_sent/'.")
            
    if args.test_research:
        print("--- Testing Daily Sources Research ---")
        success = research_and_update_sources()
        if success:
            print("Sources research completed successfully! Check 'sources.json'.")
        else:
            print("Sources research encountered an error.")
            
    if args.test_ideas:
        print("--- Testing 2-Hourly Ideas Generation ---")
        success = generate_and_email_ideas()
        if success:
            print("Ideas generation and mailing completed successfully!")
        else:
            print("Ideas generation completed (check 'seen_ideas.json' and local email file).")

if __name__ == "__main__":
    main()
