# Encode AI Hackathon 2025 - Humming Bird

## 🏆 About the Hackathon

The **Encode AI Hackathon 2025** is a three-day immersive AI experience held in Shoreditch. It brings together top AI talent, developers, and industry leaders for hands-on innovation. Our team embraced the opportunity to build **Humming Bird** — an intelligent, conversation-driven app that guides aspiring founders from idea to execution using smart AI workflows.

## 🚀 About Humming Bird

**Humming Bird** is an AI-powered startup ideation and tool recommendation assistant that:

- Chats with users to understand their startup vision
- Breaks down business ideas into structured development steps
- Recommends optimal tools and technologies to build the product

With the help of **Portia AI**, Humming Bird transforms vague startup ideas into actionable roadmaps.

**Check out our [exclidraw](https://excalidraw.com/#room=20a848c6f4d32631a366,Djw04yUeLslEFkLRntfsHw) for the draft plan before we code**

## ⚙️ Installation (Run Locally)

### 1. Clone the Repositories

```bash
git clone https://github.com/hummin-bird/humming-bird-frontend.git
git clone https://github.com/hummin-bird/humming-bird-backend.git
```

### 2. Set Up Environment Variables

Copy the `.env.example` to `.env` and insert your API keys:

```bash
cd humming-bird-backend
cp .env.example .env
```

#### Required Environment Variables:

- `PORTIA_API_KEY`: Portia AI key for workflow generation and tool recommendations
- `OPENAI_API_KEY`: OpenAI key for GPT-4o-mini to enhance conversation and reasoning
- `GEMINI_API_KEY`: API key for Gemini (optional LLM integration)
- `TAVILY_API_KEY`: Key for smart search via Tavily
- `AGENT_ID`: Identifier for the deployed agent in your backend
- `ELEVENLABS_API_KEY`: Key for ElevenLabs Conversational AI for natural voice interaction

### 3. Install Dependencies

#### Backend

Make sure Python 3.12+ is installed:s

```bash
cd humming-bird-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### Frontend

```bash
cd humming-bird-frontend
brew install pnpm
pnpm install
pnpm run dev
```
---

## 📁 About the Project

- **What?**
  Humming Bird is an AI assistant that transforms abstract startup ideas into development blueprints and toolkits.

- **Why?**
  Many aspiring entrepreneurs have ideas but struggle with execution. Humming Bird offers a guided path.

- **How?**
  Using Portia AI, it decomposes user input into a tech roadmap and identifies practical tools (e.g., Django, Supabase, React).

---

## 👥 Team Members

- **[Ying Liu]**  [GitHub](https://github.com/sophia172)
-  **[Mu Jing Tsai]**  [GitHub](https://github.com/moojing)
- **[Ana Shevchenko]**  [GitHub](https://github.com/a17o)

---

## 🎯 Key Features

- **Conversational Business Ideation**: Real-time voice-driven dialogue powered by ElevenLabs helps users express and refine ideas naturally.

- **Strategic Workflow Generation**: Portia AI translates conversations into structured, actionable development workflows.

- **Tool Recommendations**: Suggests relevant tools and technologies at each development phase, powered by Portia's smart selection logic.

- **Custom Portia AI Integration**: Uses GPT-4o-mini alongside tailored modules like planning, search, and LLMs for enhanced interaction.

- **Beautiful User Interface**: Clean, engaging UI to display conversation history and insights intuitively.

- **Persistent Conversation History**: Stores sessions for context-aware assistance and ongoing project development.

- **Sponsor Showcase Section**: Frontend section to highlight sponsors, supporting transparency and acknowledgment.

---

## 🛠️ Tech Stack

- **Frontend:** TypeScript (Lovable)
- **Backend:** Python (FastAPI)
- **AI Agents:** Portia, OpenAI, ElevenLabs

---

## 🔗 Links

- **Live Demo:** [Coming Soon]
- **GitHub Repos:**
  - Frontend: [https://github.com/hummin-bird/humming-bird-frontend.git](https://github.com/hummin-bird/humming-bird-frontend.git)
  - Backend: [https://github.com/hummin-bird/humming-bird-backend.git](https://github.com/hummin-bird/humming-bird-backend.git)

---

## 💡 Future Enhancements

We aim to evolve Humming Bird into a universal launchpad for all types of products, not just software. Planned features include:

### 🌐 Cross-Industry Product Support

Support for physical goods, services, digital media — expanding usability beyond software.

### 🚀 Integrated Launch Tools

End-to-end platform for ideation to launch: hosting, deployment, analytics, and customer feedback.

### 👥 Community Engagement and Feedback

- **Forums & Q&A**: For peer-to-peer help and idea exchange
- **Surveys & Feedback Tools**: Continuous improvement via community insight
- **Reviews & Testimonials**: Build transparency and reputation
- **Recognition Systems**: Incentivize and reward user engagement

### 📊 Advanced Analytics

Real-time insights on user behavior, tech trends, and idea viability.

### 🤖 Personalized Recommendations

AI-suggested tools, features, or growth strategies based on user behavior and industry trends.

---

## 📧 Contact

**Name:** [Your Name]\
📩 **Email:** [your.email@example.com](mailto\:your.email@example.com)

