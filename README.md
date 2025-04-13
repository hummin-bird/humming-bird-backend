# Encode AI Hackathon 2025 — Humming Bird
<img width="1159" alt="Screenshot 2025-04-13 at 10 07 59 AM" src="https://github.com/user-attachments/assets/fdf30a44-ecbd-4538-8dae-29fe36dda8c3" />

## 🏆 About the Hackathon
The **Encode AI Hackathon 2025** is a three-day immersive AI experience hosted in Shoreditch. It brings together top AI talent, developers, and industry leaders for hands-on innovation and collaboration. Our team embraced the opportunity to build **Humming Bird** — an intelligent, conversation-driven app that guides aspiring founders from idea to execution using smart AI workflows.


## 🚀 About Humming Bird
**Humming Bird** is an AI-powered startup ideation and tool recommendation assistant that:
- Chats with users to understand their startup vision.
- Breaks down business ideas into structured, actionable development steps.
- Recommends optimal tools and technologies to bring products to life.

### ⚙️ How Portia AI Powers Humming Bird
When a user interacts with the Humming Bird app, their business idea is sent to **Portia AI**, which drives the behind-the-scenes workflow. Portia breaks down the process into smart, structured steps to guide users from concept to execution:

1. **Understanding the Idea**: Portia analyzes the user’s product concept and generates a five-stage development plan, focusing on technical aspects like programming frameworks, UI design, and deployment.
2. **Tool Discovery**: For each stage, Portia intelligently searches for one specific, real-world software tool. It filters out articles or tool lists, returning only concrete tools with:
   - Tool name
   - One-sentence description
   - Official website link
   - Logo image link
3. **Structured Output**: Portia organizes the selected tools into a clean, structured format that's easy for users to follow and act on.

Through this workflow, Portia AI empowers Humming Bird to provide thoughtful, tailored recommendations — turning raw ideas into actionable roadmaps.

**Check out our [Excalidraw draft plan](https://excalidraw.com/#room=20a848c6f4d32631a366,Djw04yUeLslEFkLRntfsHw) before we code!**

## 🗺️ Code Architecture

- [Backend Code Architecture](https://github.com/hummin-bird/humming-bird-backend/blob/main/code_architecture.md)
- [Frontend Code Architecture](https://github.com/hummin-bird/humming-bird-frontend/blob/main/code-architecture.md)

## 🛠️ Installation Guide

### 1️⃣ Clone the Repositories
```bash
git clone https://github.com/hummin-bird/humming-bird-frontend.git
git clone https://github.com/hummin-bird/humming-bird-backend.git
```

### 2️⃣ Set Up Environment Variables
Copy the example environment file and insert your API keys:
```bash
cd humming-bird-backend
cp .env.example .env
```

**Required Environment Variables:**
- `PORTIA_API_KEY`: Portia AI key for workflow generation and tool recommendations
- `OPENAI_API_KEY`: OpenAI key for GPT-4o-mini to enhance conversation and reasoning
- `GEMINI_API_KEY`: API key for Gemini (optional LLM integration)
- `TAVILY_API_KEY`: Key for smart search via Tavily
- `AGENT_ID`: Identifier for the deployed agent in your backend
- `ELEVENLABS_API_KEY`: Key for ElevenLabs Conversational AI for natural voice interaction

### 3️⃣ Install Dependencies
**Backend Setup**
```bash
cd humming-bird-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Frontend Setup**
```bash
cd humming-bird-frontend
brew install pnpm
pnpm install
pnpm run dev
```

---

## 📁 About the Project
- **What?**  
  Humming Bird is an AI assistant that transforms abstract startup ideas into actionable development blueprints and curated toolkits.

- **Why?**  
  Many aspiring entrepreneurs have ideas but struggle with execution. Humming Bird offers a guided, conversational path from concept to launch.

- **How?**  
  Using Portia AI, it deconstructs user input into a technical roadmap and intelligently identifies the most practical tools for each stage.

## 👥 Team Members
- **Ying Liu**  
  [GitHub](https://github.com/sophia172) | [LinkedIn](https://www.linkedin.com/in/yingliu-data/)
- **Mu Jing Tsai**  
  [GitHub](https://github.com/moojing) | [LinkedIn](https://www.linkedin.com/in/mu-jing-tsai/)
- **Ana Shevchenko**  
  [GitHub](https://github.com/a17o) | [LinkedIn](https://www.linkedin.com/in/cronaut/)

## ✨ Key Features
- **Conversational Business Ideation**: Voice and text-based brainstorming powered by ElevenLabs.
- **Strategic Workflow Generation**: Portia AI translates conversations into structured, actionable development workflows.
- **Tool Recommendations**: Tailored tools for each development phase, intelligently selected through Portia.
- **Custom Portia AI Integration**: Combining GPT-4o-mini with bespoke planning and search modules.
- **Clean, Modern User Interface**: Intuitive, engaging UI for tracking conversations, roadmaps, and tool suggestions.
- **Persistent Project History**: Saves session context to support long-term project development.
- **Sponsor Showcase Section**: Dedicated frontend space to highlight and thank our event sponsors.

## 🖥️ Tech Stack
- **Frontend:** TypeScript (Lovable)
- **Backend:** Python (FastAPI)
- **AI Agents:** Portia, OpenAI, ElevenLabs

## 🔗 Links
- **Live Demo:** Coming Soon
- **GitHub Repositories:**
  - [Frontend](https://github.com/hummin-bird/humming-bird-frontend.git)
  - [Backend](https://github.com/hummin-bird/humming-bird-backend.git)

## 🌱 Future Enhancements
- **Cross-Industry Product Support**: Expand from software to physical products, services, and digital media.
- **Integrated Launch Tools**: One-stop platform for ideation, hosting, deployment, analytics, and feedback.
- **Community Engagement & Feedback**: Forums, surveys, and reviews to build an active, insightful community.
- **Advanced Analytics**: Real-time insights into tech trends, user behavior, and idea viability.
- **Personalized Recommendations**: AI-powered suggestions for tools, features, and strategies based on project context and industry trends.

