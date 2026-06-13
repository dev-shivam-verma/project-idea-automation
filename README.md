# 💡 Project Idea Automation System

An autonomous backend project research and briefing service tailored for **Computer Science students** focusing on **Spring Boot (Intermediate)** and **AI Engineering**.

This system daily researches developer portals, job boards, and communities (e.g. LinkedIn, Y Combinator, Devfolio, GitHub, Stack Overflow) using **Gemini API with Google Search Grounding**. Every **2 hours**, it generates the top 5 high-paying backend project ideas (with detailed implementation roadmaps, demand scores, and recruiter appeal metrics), filters out any previously generated ideas to prevent repetition, and emails you a highly styled briefing.

---

## 🚀 Recommended Setup: Active Workspace
To make editing and tracking this project easier, we recommend setting this project directory as your active workspace in your IDE:
```text
/home/shivam/.gemini/antigravity/scratch/project_idea_automation
```

---

## 📁 Directory Structure
- `config.py` - Manages `.env` loading and path configurations.
- `gemini_client.py` - Invokes Gemini 2.5 Flash API with search grounding (zero external dependencies).
- `email_sender.py` - Renders a premium HTML email template and sends it via SMTP (or saves locally).
- `research_sources.py` - Performs daily research of developer sources & job boards.
- `generate_ideas.py` - Brainstorms top 5 project roadmaps, checks for duplicates, and triggers the email.
- `scheduler.py` - Background daemon that orchestrates timing loops statefully.
- `test_run.py` - Utility CLI to trigger individual steps for verification.
- `sources.json` - Current relevance-ranked search targets (updated daily).
- `seen_ideas.json` - Log of all sent ideas to prevent duplicates.
- `scheduler_state.json` - State persistence for system restarts.
- `emails_sent/` - Local folder storing copy of emails for browser viewing.

---

## ⚙️ Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the following details:
   - **`GEMINI_API_KEY`**: Your Google Gemini API Key from Google AI Studio.
   - **SMTP Credentials**:
     - `SMTP_USER`: Your Gmail address.
     - `SMTP_PASSWORD`: An App Password generated from your Google Account settings (do not use your regular password).
     - `RECIPIENT_EMAIL`: The email address where you want to receive the briefs.

> [!NOTE]
> **No Credentials Fallback**: If `GEMINI_API_KEY` or SMTP details are left blank, the system will run using pre-curated high-quality Spring Boot + AI project fallbacks and save the beautiful HTML emails locally to `emails_sent/` so you can open them in any browser to verify them.

---

## 🧪 Testing & Verification
You can manually run and test specific parts of the project using `test_run.py`:

1. **Test Email Layout & Delivery**:
   ```bash
   python3 test_run.py --test-email
   ```
   *Generates a mock email with 5 sample project ideas and either sends it or saves the HTML file into the `emails_sent/` folder.*

2. **Test Sources Research**:
   ```bash
   python3 test_run.py --test-research
   ```
   *Runs the search-grounded research tool and updates your `sources.json` configuration file.*

3. **Test End-to-End Brainstorming & Emailing**:
   ```bash
   python3 test_run.py --test-ideas
   ```
   *Queries the current sources, filters out duplicates, generates 5 detailed roadmaps, appends them to your seen list, and emails/saves the result.*

---

## 🕒 Running the Background Daemon
To run the automated scheduler continuously in the background (orchestrating the daily source research and 2-hourly briefings):
```bash
python3 scheduler.py
```
To run it in the background as a detached process:
```bash
nohup python3 scheduler.py > scheduler.log 2>&1 &
```
The scheduler is state-persistent. If you restart it or if your system reboots, it will inspect `scheduler_state.json` to see if a run was missed and run it immediately, rather than restarting timers.

---

## 🐳 Docker Containerization & Azure Deployment

### 1. Build and Test Locally
To containerize the application and run it locally to verify:

1. **Build the Docker image**:
   ```bash
   docker build -t project-idea-automation .
   ```

2. **Run it locally** (feeding in the `.env` file credentials and mapping your state files to host filesystem for persistence):
   ```bash
   docker run -d \
     --name idea-automation-service \
     --env-file .env \
     -v $(pwd)/seen_ideas.json:/app/seen_ideas.json \
     -v $(pwd)/sources.json:/app/sources.json \
     -v $(pwd)/scheduler_state.json:/app/scheduler_state.json \
     project-idea-automation
   ```

3. **Check container logs**:
   ```bash
   docker logs -f idea-automation-service
   ```

---

### 2. Push to Azure Container Registry (ACR)
Follow these commands to push the built container image to Azure:

1. **Log in to your Azure Account**:
   ```bash
   az login
   ```

2. **Create a Resource Group** (e.g., in East US region):
   ```bash
   az group create --name IdeaAutomationRG --location eastus
   ```

3. **Create an Azure Container Registry** (Registry name must be globally unique):
   ```bash
   az acr create --resource-group IdeaAutomationRG --name myideaautomationregistry --sku Basic
   ```

4. **Log in to your ACR instance**:
   ```bash
   az acr login --name myideaautomationregistry
   ```

5. **Tag your local image**:
   ```bash
   docker tag project-idea-automation myideaautomationregistry.azurecr.io/project-idea-automation:v1
   ```

6. **Push the image to your Azure Registry**:
   ```bash
   docker push myideaautomationregistry.azurecr.io/project-idea-automation:v1
   ```

---

### 3. Deploy and Run on Azure (Azure Container Instances)
The easiest and cheapest way to run this 24/7 background python service on Azure is **Azure Container Instances (ACI)**. 

Run the following command to deploy the container directly from your ACR and pass your environment variables securely:

```bash
az container create \
  --resource-group IdeaAutomationRG \
  --name project-idea-automation-service \
  --image myideaautomationregistry.azurecr.io/project-idea-automation:v1 \
  --cpu 1 \
  --memory 1.5Gi \
  --restart-policy Always \
  --registry-login-server myideaautomationregistry.azurecr.io \
  --registry-username <ACR_USERNAME> \
  --registry-password <ACR_PASSWORD> \
  --environment-variables \
    GEMINI_API_KEY="your_gemini_api_key" \
    SMTP_SERVER="smtp.gmail.com" \
    SMTP_PORT="587" \
    SMTP_USER="shivamvrma3012@gmail.com" \
    SMTP_PASSWORD="your_app_password" \
    SENDER_EMAIL="shivamvrma3012@gmail.com" \
    RECIPIENT_EMAIL="shivamvrma3012@gmail.com"
```
*(Note: Replace `<ACR_USERNAME>` and `<ACR_PASSWORD>` with the admin credentials found in the Access Keys section of your ACR portal in the Azure console, or fetch them using `az acr credential show --name myideaautomationregistry`)*

