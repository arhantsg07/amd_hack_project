# 🌐 NexusGraph

### Cross-Tool Intelligence Layer

NexusGraph is a sophisticated intelligence platform that aggregates signals from **Slack**, **Jira**, and **GitHub** into a unified **Work Graph**. By bridging the gaps between communication, task management, and version control, NexusGraph provides teams with deep insights into their development lifecycle, identifying bottlenecks and predicting risks before they impact delivery.

---

## ✨ Key Features

- **🕸️ Work Graph**: A comprehensive, interconnected view of all work items (PRs, Issues, Slack Threads) and their relationships.
- **🔍 Entity Resolution**: Intelligent linking of related items across different tools using fuzzy matching and context analysis.
- **💡 Intelligence Analysis**:
    - **Bottleneck Detector**: Identifies stale PRs and stalled discussions.
    - **Overload Scorer**: Flags team members with high task-to-activity ratios.
    - **Risk Predictor**: Detects merged PRs without corresponding closed tickets.
    - **Shadow Task Detector**: Uncovers untracked work buried in Slack threads.
- **💬 AI Chat**: Natural language interface to query your workflow and get instant insights.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Intelligence**: Custom Graph algorithms, FuzzyWuzzy for entity resolution.
- **Server**: Uvicorn

### Frontend
- **Framework**: [React](https://reactjs.org/) + [Vite](https://vitejs.dev/)
- **Visualisation**: [React Force Graph](https://github.com/vasturiano/react-force-graph)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Animations**: [Framer Motion](https://www.framer.com/motion/)
- **Icons**: [Lucide React](https://lucide.dev/)

---

## 📂 Project Structure

```text
.
├── backend/            # FastAPI Application
│   ├── api/            # API Routes and Endpoints
│   ├── models/         # Pydantic Schemas
│   ├── graph/          # Work Graph Logic
│   ├── analysis/       # Intelligence Scopes
│   └── data/           # Mock Data & Stores
├── frontend/           # React Application
│   ├── src/
│   │   ├── components/ # UI Components (Dashboard, Graph, Panels)
│   │   └── services/   # API Integration
│   └── public/         # Static Assets
└── README.md           # You are here
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### 📡 Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`. You can access the interactive docs at `http://localhost:8000/docs`.

### 💻 Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

---
