# AI Sales Call Intelligence POC 🚀

A lean Proof of Concept (POC) designed to automate sales call transcription, scoring, and feedback using Groq's LPU™ inference engine.

## 🌟 Features
- **Audio Upload:** Support for MP3/WAV/M4A sales call recordings.
- **Ultra-Fast Transcription:** Powered by Whisper-large-v3 on Groq.
- **AI Analysis:** Scoring logic powered by Llama 3 on Groq.
- **Sales Dashboard:** Visual performance metrics and actionable feedback.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Inference Engine:** Groq (Whisper + Llama 3)
- **Language:** Python

🧠 Company Brain OS: Revenue & Operations Platform
📖 Overview
The Company Brain OS is an AI-native enterprise operating system designed to replace siloed CRMs (like Salesforce) and disjointed project management tools (like Monday.com). By utilizing autonomous AI agents directly integrated into Google Workspace, this platform achieves Zero-Data Entry for sales reps and enables Asynchronous Interventions, proven to reduce operational status meetings by up to 40%.

This repository currently houses the Proof of Concept (POC). Below is the strategic roadmap for transitioning this POC into a highly scalable, production-ready Minimum Viable Product (MVP) built entirely on the Google Cloud Platform (GCP).

🚀 Phase 1: MVP Tech Stack (100% Google Ecosystem)
To ensure seamless integration, enterprise-grade security, and simplified IAM, the production MVP will be hosted completely within GCP.

Frontend (UI/UX): Next.js (React) + Tailwind CSS

Hosting: Google Cloud Run for serverless, auto-scaling frontend delivery.

Backend Framework: FastAPI (Python)

Hosting: Google Cloud Run to handle rapid, asynchronous API endpoints and push notifications.

Database (The Single Source of Truth): Google Cloud SQL (PostgreSQL)

Why: Fully managed relational database to map Deals ➔ Tasks ➔ AI Transcripts, tightly integrated with Google Cloud IAM for role-based security.

Storage (Evidence & Media): Google Cloud Storage (GCS)

Why: Secure, low-cost object storage for videos, photos, and PDF permits uploaded by field reps.

Core AI & Telephony Engine: Google Gemini 1.5 Pro (Vertex AI)

Why: Gemini 1.5 Pro is natively multimodal. It handles reasoning, text generation, image analysis, and direct audio processing. We do not need a separate transcription service; Gemini listens to the raw call audio and generates the coaching playbook in one pass.

🔑 Phase 2: Required APIs & Integrations
By keeping everything under Google, API authentication is handled seamlessly via Google Service Accounts and OAuth 2.0.

Google Workspace APIs (The Ingestion Layer)

Gmail API & Google Calendar API: Allows the AI Agent to securely read inbound customer emails and meeting schedules.

Google Meet API: To automatically ingest sales call recordings directly from the rep's calendar events.

Google Drive API: For auto-filing contracts, proposals, and permits directly into the company's shared drives.

Google Vertex AI (The Brain)

Gemini 1.5 Pro API: Acts as the central nervous system. It parses emails, analyzes uploaded permit PDFs, scores audio sales calls, and generates the CEO's cross-departmental executive synthesis.

🗓️ Phase 3: MVP Development Timeline (Estimated 8-10 Weeks)
Assuming a small, agile development pod (1 Lead Architect, 1 Full-Stack Developer).

Sprint 1: Google Cloud Foundation (Weeks 1-2)

Provision Google Cloud SQL (PostgreSQL) and GCS buckets.

Set up Google Workspace OAuth and Cloud IAM for the 4 user profiles.

Sprint 2: Core Platform CRUD (Weeks 3-4)

Build the Next.js Sales Hub (CRM) and Operations Board.

Deploy initial microservices via Google Cloud Run.

Sprint 3: The Asynchronous Loop (Weeks 5-6)

Build the Push Notification system.

Enable multi-media file uploads from the Employee Terminal directly to GCS.

Sprint 4: Workspace & Vertex AI Integration (Weeks 7-8)

Connect Gmail/Calendar/Meet APIs.

Build the Gemini 1.5 Pro prompts for native audio call scoring and COO Playbook generation.

Sprint 5: Executive Synthesis & Polish (Weeks 9-10)

Build the CEO Command Center.

Engineer the systemic risk detection prompts (cross-referencing sales pipeline with ops capacity).

💸 Phase 4: Estimated API & Cloud Costs (Production MVP)
Note: This projection strictly covers GCP consumption for a ~$10M revenue company (assuming ~15 active users processing roughly 500+ audio calls and thousands of emails per month). Zero labor/development costs are included.

Service / Tool	Primary Function	Estimated Volume	Projected Monthly Cost
Google Vertex AI (Gemini 1.5 Pro)	Multimodal processing: Native audio analysis, email parsing, and executive synthesis.	
~10k audio mins +


~15M text tokens

$80.00 - $140.00
Google Workspace APIs (Gmail, Drive, Meet)	The ingestion layer for the autonomous agents.	Unlimited internal queries	$0.00 (Included in existing G-Suite licenses)
Google Cloud SQL (PostgreSQL)	Relational database for CRM and Ops Tasks.	1 vCPU, 4GB RAM, 20GB SSD	~ $45.00
Google Cloud Run	Serverless hosting for Next.js frontend and FastAPI backend.	~2M requests / auto-scaling	~ $15.00
Google Cloud Storage (GCS)	Raw media storage for operations evidence and call recordings.	~100GB of hot storage	~ $2.50
TOTAL ESTIMATED OPEX	Complete System Operation	--	$142.50 - $202.50 / month
The ROI Architecture Pitch: By transitioning to the Google-native Company Brain OS, the organization replaces traditional per-seat licensing models (e.g., Salesforce @ $150/user/mo + Monday.com @ $20/user/mo = ~$2,500+/mo) with a unified GCP cloud infrastructure that costs less than $250 a month total, while eliminating data silos and maximizing the ROI of their existing Google Workspace subscription.

🛠️ Phase 5: Running the Current Python POC
If you are evaluating this repository via the Streamlit Proof of Concept, follow these steps to run it locally:

1. Clone the repository:

Bash
git clone https://github.com/your-repo/company-brain-os.git
cd company-brain-os
2. Create a virtual environment & install dependencies:

Bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install streamlit pandas google-genai
3. Setup your Environment Variables:

Create a .streamlit/secrets.toml file in the root directory.

Add your temporary API key for local testing:

Ini, TOML
GEMINI_API_KEY = "your_api_key_here"
4. Run the Application:

Bash
streamlit run main.py
Note: To reset the mock database or clear cached interactions during your demo, click the "Reset Global Database" button at the bottom of the left-hand navigation sidebar.
