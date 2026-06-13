import json
import os
from datetime import datetime
import config
from gemini_client import call_gemini

# Default high-quality sources as a fallback
DEFAULT_SOURCES = [
    {
        "name": "LinkedIn Jobs",
        "url": "https://www.linkedin.com/jobs",
        "relevance_rank": 1,
        "description": "Primary job portal for recruiting Spring Boot and backend developers. Used to analyze recruiter demands and skills.",
        "query_template": "Spring Boot AI backend developer recruiter job requirements portfolio"
    },
    {
        "name": "Y Combinator Startups & Launch",
        "url": "https://www.ycombinator.com/jobs",
        "relevance_rank": 2,
        "description": "Best place to discover cutting-edge tech stacks and AI integrations favored by high-paying startups.",
        "query_template": "Spring Boot Java AI backend developer job description startup"
    },
    {
        "name": "Devfolio & Devpost Hackathons",
        "url": "https://devfolio.co",
        "relevance_rank": 3,
        "description": "Hackathon portal containing outstanding projects integrating AI models with solid backend services.",
        "query_template": "Spring Boot AI hackathon project showcase"
    },
    {
        "name": "GitHub Trending & Repositories",
        "url": "https://github.com/trending/java",
        "relevance_rank": 4,
        "description": "Repository search to inspect trending Java/Spring Boot frameworks and libraries integrating AI API clients.",
        "query_template": "Spring Boot AI LLM integration template starter"
    },
    {
        "name": "Stack Overflow & Developer Communities",
        "url": "https://stackoverflow.com",
        "relevance_rank": 5,
        "description": "Developer Q&A boards to find practical architectural challenges and features recruiters look for in backends.",
        "query_template": "Spring Boot AI integration implementation issues architecture"
    }
]

def research_and_update_sources():
    """
    Researches job portals and developer networks to compile and rank
    the best sources for Spring Boot + AI project inspiration.
    """
    print(f"[{datetime.now()}] Starting sources research...")
    
    prompt = """
    You are an expert researcher for developer job markets and backend portfolios.
    The target student is an intermediate Spring Boot developer willing to learn AI Engineering (integrating LLMs, vector databases, agents, RAG, etc. into backends).
    They need a backend internship and a high-paying job.
    
    Perform a web search to identify the top 5 to 7 platforms, job portals, or developer communities where recruiters post active Spring Boot + AI job requirements, or where developers share outstanding project ideas (e.g. LinkedIn, Y Combinator, Devfolio, StackOverflow, Reddit, GitHub, etc.).
    
    Rank these sources in order of relevance (1 to N, where 1 is the most relevant) for finding high-quality, recruiter-approved backend project ideas.
    For each source, provide:
    1. Name of the platform.
    2. Approximate search URL.
    3. Relevance rank (1-indexed).
    4. A concise description of why it is relevant.
    5. A Google Search query template that can be used to query this platform for active project ideas and backend recruiter features.
    
    You MUST respond with a valid JSON array of objects. Do not wrap the JSON in Markdown backticks.
    Each object in the array must have the following keys:
    - "name" (string)
    - "url" (string)
    - "relevance_rank" (integer)
    - "description" (string)
    - "query_template" (string)
    
    Example Output Format:
    [
      {
        "name": "LinkedIn Jobs",
        "url": "https://www.linkedin.com/jobs",
        "relevance_rank": 1,
        "description": "...",
        "query_template": "..."
      }
    ]
    """
    
    sources = []
    
    if not config.GEMINI_API_KEY:
        print("GEMINI_API_KEY not configured. Falling back to default high-quality sources.")
        sources = DEFAULT_SOURCES
    else:
        try:
            # Query Gemini using search grounding
            response_text = call_gemini(prompt, response_json=True, use_search=True)
            
            # Clean response text in case LLM wrapped it in markdown
            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                # strip out markdown block
                lines = clean_text.splitlines()
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    lines = lines[1:-1]
                clean_text = "\n".join(lines).strip()
                
            sources = json.loads(clean_text)
            
            # Simple validation on results
            if not isinstance(sources, list) or len(sources) == 0:
                raise ValueError("Response is not a non-empty JSON list.")
                
            # Sort by rank
            sources.sort(key=lambda s: s.get("relevance_rank", 99))
            print("Successfully researched and parsed sources from Gemini API.")
            
        except Exception as e:
            print(f"Error researching sources via Gemini API: {e}")
            print("Falling back to default high-quality sources.")
            sources = DEFAULT_SOURCES

    # Write to file
    try:
        with open(config.SOURCES_FILE, "w", encoding="utf-8") as f:
            json.dump(sources, f, indent=2)
        print(f"Successfully updated sources file: {config.SOURCES_FILE}")
        return True
    except Exception as e:
        print(f"Critical Error saving sources file: {e}")
        return False

if __name__ == "__main__":
    research_and_update_sources()
