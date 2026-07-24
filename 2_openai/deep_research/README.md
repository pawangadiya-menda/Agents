---
title: deep_research
app_file: app.py
sdk: gradio
sdk_version: 6.14.0
---

# 🔍 Deep Research Agent

> A multi-agent research system that takes a single question, plans its own
> web searches, runs them in parallel, synthesizes a long-form report, and
> emails the result to you.

**[▶ Try it live →](https://deep-research-fcly.onrender.com/)**

[![Live on Render](https://img.shields.io/badge/Render-Live-46E3B7?logo=render&logoColor=white)](https://deep-research-fcly.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-412991?logo=openai&logoColor=white)](https://openai.github.io/openai-agents-python/)
[![Gradio](https://img.shields.io/badge/Gradio-UI-FF7C00?logo=gradio&logoColor=white)](https://gradio.app)

> ⏱️ **Cold start note:** the demo runs on Render's free tier. The first
> request after a period of inactivity can take 30-50 seconds while the
> instance wakes up. Subsequent requests are fast.

---

## 💡 What It Does

You ask one question. The system does the rest:

1. **Decomposes** the question into 5 distinct web searches, each with a stated reason
2. **Executes** all searches concurrently
3. **Summarizes** each result down to a tight 300-word brief
4. **Synthesizes** everything into a 1000+ word markdown report
5. **Formats and emails** the report to the address you provide

Progress streams back to the UI at every stage, so you see the plan, the
search count, and the write-up as they happen rather than staring at a
spinner.

---

## 🏗️ Architecture

Five specialized agents, each with one job, coordinated by an orchestrator:

```
User query
    |
    v
+-----------------+
|  Planner Agent  |  -> WebSearchPlan (5 x {query, reason})
+-----------------+
    |
    v
+-----------------+
|  Search Agent   |  x5, run in parallel via asyncio.gather
| (WebSearchTool) |  -> 300-word summary each
+-----------------+
    |
    v
+-----------------+
|  Writer Agent   |  -> ReportData {summary, markdown_report,
+-----------------+                  follow_up_questions}
    |
    v
+-----------------+
|  Email Agent    |  -> EmailContent {subject, text_body, html_body}
+-----------------+
    |
    v
+-----------------+
|    Messenger    |  -> Brevo HTTP API, with SMTP fallback
+-----------------+
    |
    v
Report rendered in UI  +  delivered to inbox
```

**Orchestration** lives in `ResearchManager`, an async generator that
`yield`s a status string at each stage - which is what drives the live
progress updates in the Gradio UI.

---

## 🧩 Design Decisions Worth Noting

**Structured outputs over prompt parsing.** Every agent declares a Pydantic
`output_type` (`WebSearchPlan`, `ReportData`, `EmailContent`). The SDK
enforces the schema, so there is no regex-scraping of model output and no
silent format drift between runs.

**Separation of generation and side effects.** The Email Agent is explicitly
instructed *not* to send anything - it only produces content. Actual delivery
is a separate, non-LLM function. An agent that can compose and send in one
step is much harder to test and reason about.

**Parallel search, not sequential.** `asyncio.gather` fans out all five
searches at once. Latency is bounded by the slowest search rather than the
sum of all five.

**Blocking I/O off the event loop.** `send_email` is synchronous, so it is
wrapped in `asyncio.to_thread` to avoid stalling the async pipeline.

**Email failure is non-fatal.** If delivery fails, the exception is caught
and surfaced as a warning - the report still renders in the UI. A broken
SMTP config should not destroy work the user already paid for in tokens
and time.

**Dual email transport.** Brevo's HTTP API is used when `BREVO_API_KEY` is
set, because most PaaS providers (Render included) block outbound SMTP ports
on free tiers. Plain SMTP remains available for local development.

---

## 🛠️ Tech Stack

| Layer | Choice |
|---|---|
| Agent framework | OpenAI Agents SDK (`openai-agents`) |
| Search | `WebSearchTool`, `tool_choice="required"` |
| Schema / validation | Pydantic |
| UI | Gradio Blocks, custom CSS + JS |
| Email | Brevo HTTP API, SMTP fallback |
| Config | python-dotenv |
| Hosting | Render |
| Observability | OpenAI trace IDs, surfaced per run |

---

## ⚙️ Configuration

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | Model + web search access | *required* |
| `DEFAULT_MODEL_NAME` | Model for all agents | `gpt-5.4-mini` |
| `HOW_MANY_SEARCHES` | Searches per query | `5` |
| `BREVO_API_KEY` | Email via HTTP API (recommended for deploys) | - |
| `EMAIL_ADDRESS` | SMTP sender | - |
| `EMAIL_SMTP_SERVER` | SMTP host | - |
| `EMAIL_APP_PASSWORD` | SMTP app password | - |
| `PORT` | Server port | `7860` |

---

## 🚀 Run Locally

```bash
git clone https://github.com/pawangadiya-menda/Agents.git
cd Agents/2_openai/deep_research

pip install -r requirements.txt

# create a .env with your keys, then:
python app.py
```

Open `http://localhost:7860`.

---

## 📁 Files

```
deep_research/
├── app.py                 Gradio UI + streaming entry point
├── research_manager.py    Async orchestrator across all agents
├── planner_agent.py       Query -> structured search plan
├── search_agent.py        Search term -> 300-word summary
├── writer_agent.py        Summaries -> long-form markdown report
├── email_agent.py         Report -> subject + text + HTML
├── messenger.py           Brevo API / SMTP delivery
├── styles.py              Custom CSS, JS, example prompts
├── simple.py              Minimal reference implementation
└── requirements.txt
```

---

## 🔭 Ideas for Next Iteration

- Surface `follow_up_questions` as clickable chips to chain a second run
- Persist reports so a cold start does not lose history
- Let the user tune search count and report depth from the UI
- Add inline source citations to the writer agent's output

---

## 👤 Author

**Pawan Kumar Gadiya**
Senior Product Manager · building and shipping AI products hands-on

[![GitHub](https://img.shields.io/badge/GitHub-pawangadiya--menda-181717?logo=github)](https://github.com/pawangadiya-menda)

---

*Built while working through the Agentic AI Engineering course - see the
[repo root](../../) for the rest of the coursework, and
[digital-twin](https://github.com/pawangadiya-menda/digital-twin) for
another deployed agent.*
