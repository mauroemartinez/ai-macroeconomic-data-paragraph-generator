# 🤖 AI Macroeconomic Data Paragraph Generator (Analytics Engineer Component)

[![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?style=flat&logo=microsoft-sql-server&logoColor=white)](https://www.microsoft.com/sql-server)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Gemini API](https://img.shields.io/badge/Gemini_API-1A73E8?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)

**🌐 Enterprise Pipeline Integration:** This analytical engineering component acts as a decoupled module within the primary automation pipeline. The core data ingestion and orchestration architecture can be found at: [RPA - Exchange Rate Scrapping Automatic Mailing](https://github.com/mauroemartinez/RPA-exchange-rate-scrapping-automatic-mailing).

---

## 📝 Executive Summary

This component automates the **Data Storytelling** layer within an Argentine macroeconomic data pipeline. Utilizing the official Gemini AI SDK (**`google-genai`**), the script extracts historical time series directly from a relational database engine, processes key macroeconomic variations by applying conditional business logic, and generates a structured financial narrative in natural language.

The core engineering value rests on two architectural pillars:
1. **Dynamic Context Curation (Smart Prompt Engineering):** Prevents narrative noise by dynamically filtering out static financial variables, exposing only the indicators that exhibit significant fluctuations (outliers and trend shifts).
2. **High-Availability API Ingestion:** Implements a robust **Failover and Key Rotation Engine** to guarantee pipeline continuity against rate limits (HTTP 429) or external API infrastructure downtime.

---

## 🛠️ Architecture & Data Flow

The component operates via secure, parameterized transactions to guarantee the persistence and integrity of the generated metadata:

[ SQL Server (Fact_Mercado_Macro) ]
│
▼ (Extracts 26-row historical window via SQLAlchemy)
[ Financial Logic Engine (Pandas) ] ───► Evaluates Dynamic Thresholds (BCRA / FED TEA)
│
▼ (Structured context injection)
[ Gemini AI Client ] ◄───► [ Failover Engine ] (Automatic Key Rotation on 429 Errors)
│
▼ (Returns standardized analytical paragraph)
[ Transact-SQL (UPDATE) ]
│
▼
[ Relational Persistence (Target Column: ai_paragraph) ]

---

## 🚀 Engineering Features

* **Relational Extraction Layer:** Migrated from static file processing (CSV) to optimized, native T-SQL queries leveraging `SQLAlchemy`.
* **Rolling Trend Analysis:** Evaluates a 25-business-day rolling window (~1 business month) to identify macro trends in parallel exchange rates (Blue, MEP, Billete) and Country Risk.
* **Conditional Threshold Triggers:**
  * **BCRA TEA:** Included dynamically in the prompt only if the daily variation exceeds an absolute threshold of $\mid \Delta \text{ Daily} \mid > 0.2\%$.
  * **FED TEA:** Reactive tracking; explicitly mentioned upon any nominal shift ($>0\%$).
* **Transactional Persistence (ACID):** The generated paragraph is committed securely (`engine.begin()`) back to the relational engine for historical auditing and consumption by downstream services (Mailing/Power BI).

---

## 📦 Tech Stack

* **Generative AI Suite:** `google-genai` (Modern SDK) & `google-api-core` (Advanced exception handling for `ResourceExhausted`).
* **Data Engineering & Connectivity:** `pandas` for data manipulation, `SQLAlchemy` as the ORM abstraction layer, and `pyodbc` as the native driver for Microsoft SQL Server (ODBC Driver 18).
* **Environment Management:** `python-dotenv` for secure secrets isolation.

---

## 📥 Infrastructure & Prerequisites

### Relational Schema Requirements (T-SQL)
The script expects the target table `Fact_Mercado_Macro` to be structured as follows:

```sql
CREATE TABLE Fact_Mercado_Macro (
    Fecha DATE NOT NULL CONSTRAINT PK_Fact_Mercado PRIMARY KEY,
    TCV_Blue DECIMAL(18,2),
    TCV_MEP DECIMAL(18,2),
    TCV_Billete DECIMAL(18,2),
    riesgo_pais DECIMAL(18,2),
    bcra_tea DECIMAL(18,4),
    fed_tea DECIMAL(18,4),
    ai_paragraph VARCHAR(MAX) NULL -- Pipeline target column for GenAI text
);
```
---

### Environment Configuration (`.env`)
Create a `.env` file in the root directory (ensuring it is explicitly excluded in your `.gitignore`):

```ini
# Local/Production Database Connection
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=MacroeconomicAnalytics

# GenAI Credentials (Failover Cluster)
GEMINI_API_KEY_1=your_primary_api_key
GEMINI_API_KEY_2=your_secondary_api_key
```

---

## 🚀 Deployment & Usage
# 1. Clone the repository and navigate to the directory
git clone [https://github.com/mauroemartinez/ai-macroeconomic-data-paragraph-generator.git](https://github.com/mauroemartinez/ai-macroeconomic-data-paragraph-generator.git)
cd ai-macroeconomic-data-paragraph-generator

# 2. Initialize and activate the virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# 3. Install standardized production dependencies
pip install -r requirements.txt

# 4. Execute the AI pipeline
python ia_generator.py

---

## Expected Execution Logs
🔌 Conectando a SQL Server para extraer historial...
🤖 Solicitando párrafo a Gemini para el 22/05/2026...
💾 Guardando reporte de IA en la base de datos para la fecha 2026-05-22...
✅ Columna ai_paragraph actualizada con éxito en SQL Server.


---

## 🔄 Business Logic Matrix (Inclusion Rules)

| Financial Indicator | Evaluation Metric | Prompt Inclusion Rule |
|:---|:---|:---|
| **Dólar Blue / MEP / Billete** | Daily & Monthly Variation | **Always Included** (Core business asset) |
| **Country Risk (JP Morgan)** | Nominal Delta (Points) | **Always Included** (Sovereign metric) |
| **TEA BCRA** | Absolute Percentage Change | **Conditional:** Only if $\mid \Delta \text{ Daily} \mid > 0.2\%$ |
| **TEA FED** | Nominal Variation | **Conditional:** Only if $\mid \Delta \text{ Daily} \mid > 0\%$ |

---

## 🏔️ Project Status & Integration Roadmap

- [x] **Phase 1:** Functional standalone pipeline component (Modular Engine).
- [x] **Phase 2:** Database migration from flat files (CSV) to relational storage (T-SQL).
- [x] **Phase 3:** Parameterized transactional write operations to mitigate SQL injection.
- [ ] **Phase 4:** Package as an importable module (`import ia_generator`) inside the main RPA orchestrator.

---

## 📬 Contact

* **Email:** martinezmauroezequiel@gmail.com
* **Professional Networ:** [LinkedIn Profile](https://www.linkedin.com/in/mauroemartinez/)