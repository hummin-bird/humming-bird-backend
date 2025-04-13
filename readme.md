# Encode AI Hackathon 2025 - Humming Bird

## 🏆 About the Hackathon

The **Encode AI Hackathon 2025** is a three-day immersive AI experience held in Shoreditch. It brings together top AI talent, developers, and industry leaders for hands-on innovation. Our team embraced the opportunity to build **Humming Bird** — an intelligent, conversation-driven app that guides aspiring founders from idea to execution using smart AI workflows.

## 🚀 About Humming Bird

**Humming Bird** is an AI-powered startup ideation and tool recommendation assistant. It:

- Chats with users to understand their startup vision
- Breaks down the business idea into structured development steps
- Searches for the best tools and technologies to build the product

With the help of **Portia AI**, Humming Bird transforms vague startup ideas into actionable roadmaps.

## ⚙️ Installation (Run Locally)

### 1. Clone the Repository

```bash
git clone https://github.com/hummin-bird/humming-bird-frontend.git
cd portia-hackathon-hummingbird
```

### 2. Install Dependencies

Open two terminals for Frontend and Backend.

#### Frontend

```bash
cd frontend/hummingbird-ui
npm install
```

#### Backend

Make sure Python 3.10+ is installed:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

- `PORTIA_API_KEY`: Your Portia AI key
- `OPENAI_API_KEY`: Your OpenAI API key

### 4. Run the Servers

#### Frontend

```bash
cd frontend/hummingbird-ui
npm run dev
```

#### Backend

```bash
cd backend
uvicorn main:app --reload
```

---

## 📁 About the Project

- **What?**\
  Humming Bird is an AI agent assistant that turns abstract startup ideas into structured development blueprints and toolkits.

- **Why?**\
  Many aspiring entrepreneurs have ideas but struggle to know where to start. Humming Bird gives them a guided path to execution.

- **How?**\
  Using Portia AI, the app decomposes user input into a step-by-step tech plan and finds actual tools (e.g., Django, Supabase, React) to execute it.

---

##

### Team Members

- **[Your Name]** - [GitHub](https://github.com/YOUR_USERNAME)

---

## 🎯 Key Features



- **Conversational Business Ideation**

Humming Bird engages users in dynamic, voice-driven dialogues powered by ElevenLabs' Conversational AI. This interaction helps users articulate and refine their business ideas through natural, real-time conversations.​

Strategic Workflow Generation

Leveraging Portia AI's open-source SDK, Humming Bird translates user inputs into structured development strategies. The system employs Portia's planning capabilities to outline clear, actionable steps for building the proposed business product.​

- **Tool Recommendation for Each Development Phase**

For every stage identified in the development strategy, Humming Bird recommends specific tools. This is achieved through Portia AI's integration capabilities, allowing for the selection of appropriate technologies tailored to each development phase.​

- **Customized Portia AI Integration**

The backbone of Humming Bird is a customized implementation of Portia AI, enhanced with OpenAI's GPT-4o-mini. The integration includes tailored planning modules, search functionalities, and language model tools, ensuring a seamless and efficient user experience.​

- **Intuitive and Engaging User Interface**

Humming Bird features a beautifully designed UI that presents the conversation dialogue in a clear and engaging manner. The interface is crafted to enhance user experience, making interactions both visually appealing and user-friendly.​

- **Persistent Conversation History**

To provide context-aware assistance, Humming Bird stores and retrieves conversation histories. This ensures continuity in interactions, allowing users to revisit and build upon previous dialogues seamlessly.​

- **Sponsor Showcase Section**

The application includes a dedicated section on the front end to feature sponsors. This space allows for the presentation of sponsor information, highlighting their contributions and maintaining transparency.​

---

## 🛠️ Tech Stack

- **Frontend:** TypeScript (Lovable)
- **Backend:** Python (FastAPI)
- **AI Agents:** Portia, OpenAI, ElevenLabs

---

## 🔗 Links

- **Live Demo:** [Coming Soon]
- **GitHub Repo:** \
  frontend: [https://github.com/hummin-bird/humming-bird-frontend.git](https://github.com/hummin-bird/humming-bird-frontend.git)\
  backend: [https://github.com/hummin-bird/humming-bird-backend.git](https://github.com/hummin-bird/humming-bird-backend.git)

---

## 💡 Future Enhancements

- **Cross-Industry Product Support**

  Expanding beyond software to accommodate physical goods, services, and digital content, enabling creators across various industries to bring their ideas to life.​
- **Integrated Product Launch Tools**

  Providing users with detailed analytics on market trends, user engagement, and product performance to inform decision-making and strategy.​
- **Community Engagement and Feedback**

  Building a vibrant community where users can share ideas, provide feedback, and collaborate, fostering a supportive environment for innovation.​
- **Advanced Analytics and Insights**

  Providing users with detailed analytics on market trends, user engagement, and product performance to inform decision-making and strategy.​

---

## 📧 Contact

**Name:** [Your Name]\
📩 **Email:** [your.email@example.com](mailto\:your.email@example.com)

