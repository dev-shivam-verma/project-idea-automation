import json
import os
import re
from datetime import datetime
import config
from gemini_client import call_gemini
from email_sender import generate_html_email, send_email

def load_seen_ideas() -> list:
    """Loads previously generated ideas from Gist or local file."""
    try:
        import storage
        return storage.load_seen_ideas()
    except Exception as e:
        print(f"Warning: Failed to load seen ideas: {e}")
    return []

def save_new_ideas(new_ideas: list):
    """Saves new ideas to the seen ideas file/Gist."""
    seen = load_seen_ideas()
    seen.extend(new_ideas)
    try:
        import storage
        storage.save_seen_ideas(seen)
        print(f"Saved {len(new_ideas)} new ideas to seen list. Total seen: {len(seen)}")
    except Exception as e:
        print(f"Error saving seen ideas: {e}")

def load_sources() -> list:
    """Loads sources list from Gist or local file."""
    try:
        import storage
        sources = storage.load_sources()
        if not sources:
            print("sources list is empty or not found. Running source research first...")
            from research_sources import research_and_update_sources
            research_and_update_sources()
            sources = storage.load_sources()
        return sources
    except Exception as e:
        print(f"Error loading sources: {e}")
        return []

def get_fallback_ideas() -> list:
    """Generates high-quality fallback project ideas if the API fails."""
    return [
        {
            "title": "Spring AI RAG Resume Screener & Recruiter Assistant",
            "description": "An automated candidate screening platform built with Spring Boot that parses resumes, indexes them in a pgvector database, and allows recruiters to query candidates using semantic search and ask contextual questions via a chat interface powered by Gemini.",
            "technology_used": ["Spring Boot", "Spring AI", "pgvector / PostgreSQL", "Gemini API", "Apache POI / PDFBox", "Thymeleaf"],
            "level_of_difficulty": "Medium",
            "demand_score": 95,
            "strength": "Directly addresses a real recruiter pain point, demonstrates vector database indexing, Spring AI RAG pipeline, and document parsing.",
            "weakness": "Requires careful handling of large PDF resumes and token limits.",
            "phases_to_develop": [
                {"title": "Phase 1: Resume Upload & Parsing", "description": "Build Spring Boot API to accept PDF/Word resumes and extract text using Apache PDFBox."},
                {"title": "Phase 2: pgvector Indexing & Vector Search", "description": "Set up PostgreSQL with pgvector, use Spring AI embeddings to vectorise resumes and implement semantic search."},
                {"title": "Phase 3: AI Interviewer Assistant", "description": "Integrate Gemini API to chat with candidate data and generate interview questions based on job description."}
            ],
            "sources_from_it_came": ["LinkedIn Jobs", "GitHub Trending"]
        },
        {
            "title": "Autonomous AI Customer Agent with Spring Boot WebSockets",
            "description": "A customer support backend using Spring AI Agents to process customer inquiries, execute database tools (e.g. look up order history, cancel orders, update addresses), and stream live responses to a chat widget using WebSockets.",
            "technology_used": ["Spring Boot", "Spring AI", "WebSockets", "H2 / PostgreSQL", "LangChain4j", "Docker"],
            "level_of_difficulty": "Hard",
            "demand_score": 92,
            "strength": "Demonstrates advanced agentic workflows, function calling (tool use) in Java, and real-time asynchronous streaming communication.",
            "weakness": "Complex state management and agent feedback loops can lead to infinite calls if not properly bounded.",
            "phases_to_develop": [
                {"title": "Phase 1: Database and Websocket Setup", "description": "Build order database schema and configure Spring WebSockets for bidirectional messaging."},
                {"title": "Phase 2: Spring AI Agent with Tool Call", "description": "Configure Spring AI model with function call callbacks to execute DB lookups automatically when prompted."},
                {"title": "Phase 3: Guardrails and Streaming", "description": "Add prompt constraints, log agent traces, and implement token-by-token streaming responses."}
            ],
            "sources_from_it_came": ["Y Combinator Startups", "Devfolio"]
        },
        {
            "title": "Smart Financial Transaction Analyzer & Budget Planner",
            "description": "A smart backend system that ingests transaction logs via REST APIs, categorizes them automatically using LLM classifier prompts, detects anomalous spending patterns, and provides personalized AI-driven budgeting recommendations.",
            "technology_used": ["Spring Boot", "Spring AI", "Spring Security (JWT)", "PostgreSQL", "Redis Cache", "Gemini API"],
            "level_of_difficulty": "Medium",
            "demand_score": 88,
            "strength": "Combines classic backend fundamentals (Spring Security, CRUD, caching) with AI intelligence, making it look like a commercial fintech SaaS.",
            "weakness": "Requires robust prompt validation to prevent categorizing security codes or personal data incorrectly.",
            "phases_to_develop": [
                {"title": "Phase 1: Ingestion API & Security", "description": "Create transaction schema, secure endpoints with JWT, and build CRUD operations."},
                {"title": "Phase 2: AI Classification Engine", "description": "Integrate Gemini API to categorize transactions asynchronously and cache results in Redis."},
                {"title": "Phase 3: Analytics and Budget recommendations", "description": "Add summary charts and generate AI-driven monthly budget advice based on user spending habits."}
            ],
            "sources_from_it_came": ["LinkedIn Jobs", "Devfolio"]
        },
        {
            "title": "AI-Driven E-Commerce Dynamic Pricing Backend",
            "description": "An e-commerce pricing engine that adjusts product prices in real-time based on market demands, stock levels, competitor pricing data scraped via search, and user demand signals parsed by a Spring AI reasoning loop.",
            "technology_used": ["Spring Boot", "Spring AI", "Spring WebClient", "Redis", "MongoDB", "Quartz Scheduler"],
            "level_of_difficulty": "Hard",
            "demand_score": 90,
            "strength": "Recruiters love pricing systems; demonstrates background scheduling, scraping integration, dynamic rules, and AI reasoning.",
            "weakness": "Scraping and competitor API rate limiting; pricing decisions need strict safety margins to avoid pricing products at zero.",
            "phases_to_develop": [
                {"title": "Phase 1: E-Commerce Product Catalog", "description": "Set up MongoDB for products and write basic transactional operations."},
                {"title": "Phase 2: Competitor Price Scraper", "description": "Schedule a background job using Spring WebClient to scrape competitor websites or mock APIs for price changes."},
                {"title": "Phase 3: Dynamic Pricing Brain", "description": "Implement Spring AI reasoning agent that evaluates stock, competitor price, and target profit to suggest optimized pricing hourly."}
            ],
            "sources_from_it_came": ["Y Combinator Startups", "LinkedIn Jobs"]
        },
        {
            "title": "AI Semantic Documentation Search Engine",
            "description": "A developer tool that ingests documentation repositories, markdown files, and code comments, processes them, generates embeddings, and provides a semantic Q&A backend for developers to navigate massive codebases/APIs easily.",
            "technology_used": ["Spring Boot", "Spring AI", "Milvus / Pinecone", "Docker", "Git Integration", "Gemini API"],
            "level_of_difficulty": "Medium",
            "demand_score": 85,
            "strength": "Highly relevant for engineering teams; showcases Git file sync, vector search integration, and document chunking logic.",
            "weakness": "Requires implementing advanced document chunking algorithms to preserve code context.",
            "phases_to_develop": [
                {"title": "Phase 1: Document Ingestion", "description": "Sync files from directory or Git repo and chunk text to preserve headings."},
                {"title": "Phase 2: Embedding Generation", "description": "Generate embeddings for each chunk and index into a vector database."},
                {"title": "Phase 3: Semantic QA API", "description": "Expose endpoint to retrieve relevant chunks and query Gemini to summarize answers with links to sources."}
            ],
            "sources_from_it_came": ["Stack Overflow", "GitHub Trending"]
        }
    ]

def generate_and_email_ideas() -> bool:
    """
    Researches job market trend sources, generates top 5 new project ideas,
    filters duplicates, and emails them.
    """
    print(f"[{datetime.now()}] Starting project ideas generation...")
    
    sources = load_sources()
    seen = load_seen_ideas()
    seen_titles = [s.get("title", "") for s in seen]
    
    # Format current sources and templates for Gemini
    sources_info = ""
    for idx, src in enumerate(sources, 1):
        sources_info += f"- {src['name']} ({src['url']}): Template Query: '{src['query_template']}'\n"
        
    seen_info = ""
    if seen_titles:
        seen_info = "Previously generated titles (DO NOT REPEAT THESE OR SEMANTICALLY SIMILAR IDEAS):\n"
        for title in seen_titles[-30:]: # Provide last 30 to avoid prompt inflation
            seen_info += f"- {title}\n"
    else:
        seen_info = "No ideas have been generated yet."

    prompt = f"""
    You are an AI career agent specializing in backend engineering portfolios.
    The user is a Computer Science student at an intermediate level in Spring Boot and looking to build projects that combine Spring Boot and AI Engineering. Their goal is to land a backend internship or a high-paying software developer job.
    
    Please research the job market, developer communities, and startup job openings by searching for trending skills and project expectations.
    
    Ground your findings by researching developer portals and jobs. Here are the prioritized sources you should research:
    {sources_info}
    
    Generate exactly 5 distinct, high-quality, recruiter-approved backend project ideas.
    
    CRITICAL CONSTRAINTS:
    1. Do not repeat any of the following ideas or make projects that are very similar in concept:
    {seen_info}
    
    2. Every idea must be suitable for an intermediate Spring Boot developer, but incorporating advanced AI engineering components (e.g. RAG, Vector search, Spring AI/LangChain4j, Multi-agent tools, semantic analysis).
    
    You MUST respond with a valid JSON array containing exactly 5 project objects. Do not wrap the JSON in Markdown backticks.
    Each object in the array must contain the following keys:
    - "title": (string) Project name.
    - "description": (string) High-level overview of features.
    - "technology_used": (list of strings) Tech stack including Spring Boot features (e.g. Security, WebSockets) and AI tools.
    - "level_of_difficulty": (string) Must be one of: "Easy", "Medium", "Hard".
    - "demand_score": (integer between 1 and 100) Indicating current job market relevance.
    - "strength": (string) Why recruiters will find this project impressive.
    - "weakness": (string) Potential technical hurdles or limitations.
    - "phases_to_develop": (list of objects) Exactly 3 phases. Each phase object must have "title" (string) and "description" (string).
    - "sources_from_it_came": (list of strings) List of source names from the sources list where this idea or requirement was inspired.
    
    Example Output Format:
    [
      {{
        "title": "AI Code Reviewer Service",
        "description": "A Spring Boot microservice that...",
        "technology_used": ["Spring Boot", "Spring AI", "GitHub Webhooks", "Docker"],
        "level_of_difficulty": "Medium",
        "demand_score": 90,
        "strength": "Demonstrates...",
        "weakness": "API rate...",
        "phases_to_develop": [
          {{"title": "Phase 1: MVP Webhook", "description": "..."}},
          {{"title": "Phase 2: Gemini API Integration", "description": "..."}},
          {{"title": "Phase 3: Redis Cache & UI Dashboard", "description": "..."}}
        ],
        "sources_from_it_came": ["GitHub Trending", "LinkedIn Jobs"]
      }}
    ]
    """
    
    ideas = []
    
    if not config.GEMINI_API_KEY:
        print("GEMINI_API_KEY not configured. Falling back to default mock ideas.")
        # Filter duplicates in fallback ideas just in case
        fallback_all = get_fallback_ideas()
        filtered_fallback = [f for f in fallback_all if f["title"] not in seen_titles]
        # If all fallbacks are seen, reset seen list or just send anyway
        ideas = filtered_fallback[:5]
        if not ideas:
            ideas = fallback_all[:5]
    else:
        try:
            # Query Gemini with Search grounding
            response_text = call_gemini(prompt, response_json=True, use_search=True)
            
            # Clean response text
            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    lines = lines[1:-1]
                clean_text = "\n".join(lines).strip()
            
            ideas = json.loads(clean_text)
            
            # Validation
            if not isinstance(ideas, list) or len(ideas) == 0:
                raise ValueError("Response is not a valid JSON list.")
            
            # Limit to exactly 5
            ideas = ideas[:5]
            print(f"Successfully generated {len(ideas)} ideas using Gemini API.")
            
        except Exception as e:
            print(f"Error generating ideas via Gemini API: {e}")
            print("Falling back to default high-quality ideas.")
            fallback_all = get_fallback_ideas()
            filtered_fallback = [f for f in fallback_all if f["title"] not in seen_titles]
            ideas = filtered_fallback[:5]
            if not ideas:
                ideas = fallback_all[:5]

    # Save to seen database
    save_new_ideas(ideas)
    
    # Generate HTML content
    html_email = generate_html_email(ideas)
    
    # Send Email
    subject = f"💡 Top 5 Spring Boot & AI Project Ideas - {datetime.now().strftime('%b %d, %Y')}"
    sent = send_email(subject, html_email)
    
    return sent

if __name__ == "__main__":
    generate_and_email_ideas()
