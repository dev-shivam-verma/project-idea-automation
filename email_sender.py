import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
from pathlib import Path
import config

def generate_html_email(ideas: list) -> str:
    """
    Generates a beautiful HTML email containing the top 5 project ideas.
    """
    timestamp = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    
    # Render each idea card
    cards_html = ""
    for idx, idea in enumerate(ideas, 1):
        # Determine difficulty badge colors
        diff = idea.get("level_of_difficulty", "Medium").strip().capitalize()
        if diff == "Easy":
            diff_color = "#10B981" # Green
            diff_bg = "#E6F4EA"
        elif diff == "Hard":
            diff_color = "#EF4444" # Red
            diff_bg = "#FCE8E6"
        else:
            diff_color = "#F59E0B" # Orange
            diff_bg = "#FEF3C7"
            diff = "Medium"

        # Tech badges
        tech_list = idea.get("technology_used", [])
        if isinstance(tech_list, str):
            tech_list = [t.strip() for t in tech_list.split(",") if t.strip()]
        
        tech_badges = "".join([
            f'<span style="background-color: #EEF2F6; color: #4B5563; padding: 4px 8px; margin-right: 6px; margin-bottom: 6px; border-radius: 4px; font-size: 12px; font-weight: 600; display: inline-block; font-family: sans-serif;">{tech}</span>'
            for tech in tech_list
        ])

        # Phases
        phases = idea.get("phases_to_develop", [])
        phases_html = ""
        if isinstance(phases, list):
            for p_idx, phase in enumerate(phases, 1):
                p_title = phase.get("title", f"Phase {p_idx}")
                p_desc = phase.get("description", "")
                phases_html += f"""
                <li style="margin-bottom: 8px;">
                    <strong style="color: #1E293B;">{p_title}</strong>: 
                    <span style="color: #475569;">{p_desc}</span>
                </li>
                """
        else:
            phases_html = f'<li style="color: #475569;">{phases}</li>'

        # Sources
        sources_list = idea.get("sources_from_it_came", [])
        if isinstance(sources_list, str):
            sources_list = [s.strip() for s in sources_list.split(",") if s.strip()]
        sources_html = ", ".join([f'<span style="color: #2563EB; font-weight: 500;">{src}</span>' for src in sources_list])

        # Demand score visual bar
        demand_score = int(idea.get("demand_score", 0))
        # Ensure between 0 and 100
        demand_score = max(0, min(100, demand_score))

        cards_html += f"""
        <!-- Card {idx} -->
        <div style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #E2E8F0; margin-bottom: 30px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); padding: 18px 24px;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="left">
                            <span style="color: #818CF8; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; font-family: sans-serif;">Idea #{idx}</span>
                            <h2 style="color: #ffffff; margin: 4px 0 0 0; font-size: 20px; font-weight: 700; font-family: sans-serif;">{idea.get("title", "Project Idea")}</h2>
                        </td>
                        <td align="right" valign="top" style="white-space: nowrap;">
                            <span style="background-color: {diff_bg}; color: {diff_color}; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; font-family: sans-serif;">{diff}</span>
                        </td>
                    </tr>
                </table>
            </div>
            
            <div style="padding: 24px; font-family: sans-serif;">
                <!-- Description -->
                <p style="color: #334155; font-size: 15px; line-height: 1.6; margin-top: 0; margin-bottom: 20px;">
                    {idea.get("description", "")}
                </p>

                <!-- Tech Used -->
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #475569; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0; margin-bottom: 8px;">Technologies</h4>
                    <div>{tech_badges}</div>
                </div>

                <!-- Demand Score -->
                <div style="margin-bottom: 20px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td align="left">
                                <h4 style="color: #475569; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">Market Demand Score</h4>
                            </td>
                            <td align="right">
                                <span style="font-weight: 700; color: #4F46E5; font-size: 14px;">{demand_score}/100</span>
                            </td>
                        </tr>
                    </table>
                    <div style="background-color: #E2E8F0; height: 8px; border-radius: 4px; margin-top: 6px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #4F46E5 0%, #818CF8 100%); width: {demand_score}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>

                <!-- Development Phases -->
                <div style="margin-bottom: 20px; border-left: 3px solid #E2E8F0; padding-left: 16px;">
                    <h4 style="color: #475569; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0; margin-bottom: 10px;">Phases to Develop</h4>
                    <ol style="margin: 0; padding-left: 0; list-style-type: none; font-size: 14px; line-height: 1.5;">
                        {phases_html}
                    </ol>
                </div>

                <!-- Strengths & Weaknesses -->
                <div style="margin-bottom: 20px; background-color: #F8FAFC; border-radius: 8px; padding: 16px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td width="50%" valign="top" style="padding-right: 10px;">
                                <strong style="color: #15803D; font-size: 13px; display: block; margin-bottom: 6px;">🟢 Strengths (Recruiter Appeal)</strong>
                                <span style="color: #475569; font-size: 13px; line-height: 1.4;">{idea.get("strength", "Highly appealing to AI integration interests.")}</span>
                            </td>
                            <td width="50%" valign="top" style="padding-left: 10px; border-left: 1px solid #E2E8F0;">
                                <strong style="color: #B91C1C; font-size: 13px; display: block; margin-bottom: 6px;">🔴 Weaknesses (Challenges)</strong>
                                <span style="color: #475569; font-size: 13px; line-height: 1.4;">{idea.get("weakness", "Requires complex prompt orchestration or async job queues.")}</span>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- Source Footnote -->
                <div style="border-top: 1px solid #F1F5F9; padding-top: 12px; font-size: 12px; color: #64748B;">
                    <strong>Source Origins:</strong> {sources_html}
                </div>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Ideas Briefing</title>
    </head>
    <body style="background-color: #F1F5F9; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #F1F5F9; padding: 30px 10px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%;">
                        <!-- Header Banner -->
                        <tr>
                            <td align="center" style="background: linear-gradient(135deg, #4F46E5 0%, #312E81 100%); border-radius: 12px 12px 0 0; padding: 35px 20px;">
                                <h1 style="color: #ffffff; font-size: 26px; font-weight: 800; margin: 0 0 10px 0; font-family: sans-serif; letter-spacing: -0.025em;">💡 Top 5 Project Ideas</h1>
                                <p style="color: #C7D2FE; font-size: 15px; margin: 0; font-family: sans-serif; font-weight: 500;">Intermediate Spring Boot & AI Engineering Briefing</p>
                            </td>
                        </tr>
                        
                        <!-- Intro info -->
                        <tr>
                            <td style="background-color: #ffffff; border-bottom: 1px solid #E2E8F0; padding: 24px; font-family: sans-serif;">
                                <h3 style="color: #1E293B; margin-top: 0; margin-bottom: 8px; font-size: 16px;">Hello Shivam,</h3>
                                <p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0;">
                                    Here are the latest curated project ideas aligned to backend job markets, recruiter expectations, and developer communities. These ideas focus on intermediate Spring Boot combined with AI technologies to maximize your portfolio's high-paying job appeal.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Cards Container -->
                        <tr>
                            <td style="padding: 24px 0 0 0;">
                                {cards_html}
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding: 20px; font-family: sans-serif; font-size: 12px; color: #94A3B8;">
                                <p style="margin: 0 0 6px 0;">This email was generated automatically by your Project Idea Automation system.</p>
                                <p style="margin: 0 0 12px 0;">Generated on {timestamp} • Runs every 2 hours</p>
                                <div style="border-top: 1px solid #CBD5E1; padding-top: 12px; width: 100px; margin: 0 auto;"></div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_content

def send_email(subject: str, html_content: str) -> bool:
    """
    Sends email via SMTP or falls back to writing to files if SMTP is unconfigured.
    """
    # Write to local file first as fallback/logs
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    fallback_file = config.EMAILS_DIR / f"email_{timestamp_str}.html"
    
    try:
        with open(fallback_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved local HTML copy of email to: {fallback_file}")
    except Exception as e:
        print(f"Warning: Failed to save local copy of email: {e}")

    # Check config
    if not config.SMTP_USER or not config.SMTP_PASSWORD or not config.RECIPIENT_EMAIL:
        print("SMTP Credentials or Recipient Email not fully configured. Email was saved locally.")
        return False
        
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = config.SENDER_EMAIL
        msg["To"] = config.RECIPIENT_EMAIL
        
        # Attach HTML content
        part_html = MIMEText(html_content, "html")
        msg.attach(part_html)
        
        # Connect and Send
        print(f"Connecting to SMTP server {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SENDER_EMAIL, config.RECIPIENT_EMAIL, msg.as_string())
        print(f"Successfully sent email to {config.RECIPIENT_EMAIL}!")
        return True
    except Exception as e:
        print(f"Error occurred while sending email via SMTP: {e}")
        print("Email content is preserved in the local folder.")
        return False
