# 🤖 AI Customer Support Assistant using RAG (FAISS + Groq LLM)

An **AI-powered internal support assistant** that resolves customer tickets using **Retrieval-Augmented Generation (RAG)**.

The system retrieves **policy-grounded answers** from a FAISS vector database and generates **structured, agent-ready responses** using Groq’s ultra-fast LLM.

---


## 💡 Why This Project?

Customer support teams handle thousands of repetitive and sensitive queries daily.

Incorrect responses can lead to:
- ❌ Revenue loss  
- ❌ Policy violations  
- ❌ Poor customer experience  

This system ensures:
- ✅ Consistent, policy-based answers  
- ✅ Faster resolution time  
- ✅ Reduced manual workload  

---

## ⚡ Key Highlights

- Built a **RAG-based AI assistant** for real-world e-commerce scenarios  
- Designed a **multi-agent pipeline** (triage → retrieval → generation → validation)  
- Implemented **fallback logic** for reliability  
- Generated **structured outputs** for agent usability  
- Integrated **FAISS + Groq LLM** for fast and grounded responses  
- Developed a **production-style Streamlit dashboard UI**

---

## 🧠 Skills Demonstrated

- Retrieval-Augmented Generation (RAG)  
- Prompt Engineering  
- Vector Databases (FAISS)  
- LLM Integration (Groq API)  
- Python Backend Development  
- Multi-Agent System Design  
- UI Development (Streamlit)  

---

## ⚙️ How It Works (Simple)

1. User submits a customer support query  
2. Triage agent classifies the issue  
3. Relevant policy documents are retrieved  
4. LLM generates a structured response  
5. Output is validated and returned  

---

## 🏗️ Architecture

```text
Customer Query
     ↓
Triage Agent
     ↓
Retriever Agent (FAISS)
     ↓
Resolution Agent (Groq LLM)
     ↓
Compliance Agent
     ↓
Structured Response
```

---

## 🚀 Features

- 🔍 Semantic search over policies using FAISS  
- 🧠 Embeddings via sentence-transformers (MiniLM)  
- ⚡ Groq LLM (`llama-3.1-8b-instant`) for fast inference  
- 🤖 Multi-agent pipeline architecture  
- 📄 Structured outputs:
  - Classification  
  - Decision  
  - Rationale  
  - Citations  
  - Customer Response  
  - Next Steps  
- 🛡️ Fallback handling for invalid outputs  
- 💻 Production-style Streamlit dashboard  
- 🕘 Query history tracking  

---

## 🖥️ Frontend (Production UI)

- Clean dashboard layout  
- Decision highlighting (Approve / Reject / Review)  
- Expandable sections for internal use  
- Built-in copy support (no external dependencies)  
- Session-based query history  
- Toast notifications & loading states  

---

## 📂 Folder Structure

```text
ecommerce-agent/
├── app.py
├── requirements.txt
├── .env
├── data/
├── faiss_index/
└── src/
    ├── ingest.py
    ├── retriever.py
    ├── generator.py
    ├── agents.py
    └── main.py
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd ecommerce-agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.\.venv\Scripts\Activate.ps1  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install streamlit
```

---

## 🔑 Environment Setup

Create `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Get API key from: https://console.groq.com/

---

## 📦 Prepare Data

Place policy markdown files inside:

```text
data/policies/
```

---

## 🧠 Build Vector Index

```bash
python src/ingest.py
```

---

## ▶️ Run the Application

### Streamlit UI

```bash
streamlit run app.py
```

### CLI Mode

```bash
python src/main.py
```

---

## 🧪 Example

### Input

```text
My order arrived damaged, can I get a refund?
```

### Output

```text
Decision: APPROVE

Rationale:
Customer is eligible for refund based on damaged item policy.

Customer Response:
We’re sorry your order arrived damaged. Please share images...

Next Steps:
- Verify order ID
- Request images
```

---