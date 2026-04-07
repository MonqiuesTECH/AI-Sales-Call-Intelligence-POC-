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

# 🧠 Company Brain OS: Revenue & Operations Platform

## 📖 Overview

The Company Brain OS is an AI-native enterprise operating system designed to replace siloed CRMs (like Salesforce) and cluttered project management tools (like Monday.com). By utilizing autonomous AI agents integrated directly into Google Workspace, this platform achieves **Zero-Data Entry** for sales reps and enables **Asynchronous Interventions**, proven to reduce operational status meetings by up to 40%.

**The Streamlit POC phase is complete.** To genuinely replace Monday.com and provide a premium mobile experience, this repository outlines the architecture for a highly scalable, production-ready Minimum Viable Product (MVP) built entirely on the **Google Cloud Platform (GCP)** using an enterprise-grade React frontend.

**Development Context:** This MVP is architected to be delivered in an aggressive 8-week sprint by a solo developer, leveraging AI code generation (Cursor/Copilot) to dramatically accelerate UI component creation and backend boilerplate.

-----

## 📱 The Mobile-First UX Strategy (Beating Monday.com)

Monday.com feels cluttered because it relies on the user to manually manage massive data grids. The Company Brain OS uses AI to manage the data, surfacing only what is necessary to the human.

  * **Progressive Web App (PWA):** Built as a Next.js PWA, the platform operates seamlessly on **iOS and Android**. Users simply "Add to Home Screen" to install it like a native app—complete with push notifications, camera access, and offline caching—bypassing the 2-to-3 week Apple App Store review process.
  * **Exception-Based Design:** Field reps and executives will not see endless spreadsheets on their phones. The UI relies on bottom-sheet modals, swipe-to-complete gestures, and an "Action Inbox" that only displays immediate roadblocks requiring human intervention.
  * **Ambient Intelligence:** Because Gemini is natively integrated, the AI has ambient context. When a rep opens a deal, the AI has already summarized the client's tone from their last email and analyzed the attached engineering permits.

-----

## 🚀 Phase 1: MVP Tech Stack (100% Google Ecosystem)

To replicate a fluid drag-and-drop UX while integrating autonomous AI, we are deploying a decoupled, serverless architecture entirely within GCP.

  * **Frontend (UI/UX):** **Next.js (React) + Tailwind CSS + `dnd-kit`**
      * *Why:* Streamlit cannot handle complex, real-time drag-and-drop interfaces. Next.js combined with `dnd-kit` allows us to build the interactive Operations Board that Monday.com users expect, optimized for touch on mobile devices.
      * *Hosting:* **Google Cloud Run** for serverless frontend delivery.
  * **Backend Framework:** **FastAPI (Python) with WebSockets**
      * *Why:* Python handles the Gemini API integrations perfectly. FastAPI's native WebSocket support allows for live, real-time board updates (e.g., when a field rep uploads a site photo via their iPhone, the COO's dashboard updates instantly).
      * *Hosting:* **Google Cloud Run**.
  * **Database:** **Google Cloud SQL (PostgreSQL)**
      * *Why:* Relational data mapped via an ORM (like Prisma or SQLAlchemy).
  * **Storage (Evidence & Media):** **Google Cloud Storage (GCS)**
      * *Why:* Secure object storage for the `.mp4` videos, `.jpg` site photos, and PDF permits uploaded by field teams.
  * **Core AI Engine:** **Google Gemini 1.5 Pro (Vertex AI)**
      * *Why:* Gemini 1.5 Pro is natively multimodal. We do not need complex third-party transcription pipelines. Gemini listens to the raw call audio directly from GCP, reads the uploaded permits, and scores the reps in a single pass.

-----

## 🗓️ Phase 2: The 8-Week AI-Accelerated Solo Sprint

*Strategy: The solo developer acts as the Architect. AI coding tools generate the CRUD operations, UI layouts, and basic API routes.*

  * **Sprint 1: Architecture & Scaffolding (Weeks 1-2)**
      * Set up GCP infrastructure (Cloud SQL, GCS, Cloud Run).
      * Use AI to generate the PostgreSQL schema and ORM models. Configure Google Workspace OAuth for secure logins.
  * **Sprint 2: The Next-Gen Operations Board (Weeks 3-4)**
      * Build the interactive Next.js PWA tailored for iOS/Android.
      * Prompt the AI to generate the `dnd-kit` Kanban boards and exception-based Action Inbox. Wire up FastAPI WebSockets for real-time collaboration.
  * **Sprint 3: The AI Agents & Workspace Auth (Weeks 5-6)**
      * Connect Gmail/Calendar APIs and Vertex AI.
      * Write the system prompts for Gemini 1.5 Pro to handle native audio call scoring and predictive operational forecasting.
  * **Sprint 4: Asynchronous Loop & Launch (Weeks 7-8)**
      * Build the Push Notification system and the CEO Command Center.
      * Implement the GCS file upload handlers for rich media (videos/photos) from the mobile terminal. Run full end-to-end testing and deploy to Cloud Run.

-----

## 💸 Phase 3: Estimated API & Cloud Costs (Production MVP)

*Note: This projection strictly covers GCP consumption for a \~$10M revenue company (assuming \~15 active users processing roughly 500+ audio calls and thousands of emails per month).*

| Service / Tool | Primary Function | Estimated Volume | Projected Monthly Cost |
| :--- | :--- | :--- | :--- |
| **Google Vertex AI** *(Gemini 1.5 Pro)* | Native audio analysis, email parsing, and executive synthesis. | \~10k audio mins + <br>\~15M text tokens | **$80.00 - $140.00** |
| **Google Workspace APIs** *(Gmail, Drive)* | The ingestion layer for the autonomous agents. | Unlimited queries | **$0.00** *(Included in G-Suite)* |
| **Google Cloud SQL** *(PostgreSQL)* | Relational database for CRM and Ops Tasks. | 1 vCPU, 4GB RAM, 20GB | **\~ $45.00** |
| **Google Cloud Run** | Serverless hosting for Next.js and FastAPI backend. | \~2M requests / mo | **\~ $15.00** |
| **Google Cloud Storage (GCS)** | Raw media storage for site videos and call recordings. | \~100GB hot storage | **\~ $2.50** |
| **TOTAL ESTIMATED OPEX** | **Complete System Operation** | -- | **$142.50 - $202.50 / month** |

**The ROI Architecture Pitch:** By transitioning to the Google-native Company Brain OS, the organization replaces traditional per-seat licensing models (e.g., Salesforce + Monday.com = \~$2,500+/mo) with a unified GCP cloud infrastructure that costs **less than $250 a month total**, while eliminating data silos and maximizing the ROI of their existing Google Workspace subscription.

-----

## 🛠️ Phase 4: Running the Current Python POC

If you are evaluating this repository via the Streamlit Proof of Concept, follow these steps to run it locally on your desktop:

**1. Clone the repository:**

```bash
git clone https://github.com/your-repo/company-brain-os.git
cd company-brain-os
```

**2. Create a virtual environment & install dependencies:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install streamlit pandas google-genai
```

**3. Setup your Environment Variables:**

  * Create a `.streamlit/secrets.toml` file in the root directory.
  * Add your temporary API key for local testing:
    ```toml
    GEMINI_API_KEY = "your_api_key_here"
    ```

**4. Run the Application:**

```bash
streamlit run main.py
```

*Note: To reset the mock database or clear cached interactions during your demo, click the "Reset Global Database" button at the bottom of the left-hand navigation sidebar.*
