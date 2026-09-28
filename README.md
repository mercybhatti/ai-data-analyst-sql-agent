# AI Data Analyst / SQL Agent

An AI-powered data analysis application that lets users ask questions about structured datasets using plain English instead of writing SQL queries manually.

The application takes a user's question, understands what information they are looking for, generates the required SQL query using Google's Gemini model, executes the query against the selected dataset, and presents the result along with a natural-language insight and visualization when appropriate.

I built this project to explore how large language models can be connected with traditional data analysis workflows and how natural-language interaction can make structured data easier to work with.

---

## Overview

Working with business data often requires writing SQL queries, understanding database schemas, cleaning datasets, and interpreting query results.

This project brings these steps together into one application.

A user can upload a dataset and ask a question such as:

> "Show total sales by region."

Instead of manually writing a SQL query, the application identifies the relevant table structure, generates SQL, executes it, analyzes the returned data, and displays the result in a readable format.

The goal was not to build another generic chatbot. The focus was on creating a practical data-analysis workflow where the AI has to work with real structured data and produce an actual analytical result.

---

## Why I Built This

I wanted to build a project that combined the areas I have been studying in AI and machine learning with something that has a clear practical use.

I was particularly interested in the connection between natural language and structured data. SQL is powerful, but users who are comfortable asking questions about their business data may not always be comfortable writing SQL themselves.

This project gave me an opportunity to work with LLM-based SQL generation while also dealing with the parts that are required in a real application, including authentication, dataset handling, database operations, API design, error handling, analysis history, and visualization.

---

## What the Application Does

The application provides a complete workflow for asking analytical questions about uploaded datasets.

A typical interaction looks like this:

1. The user logs into the application.
2. The user uploads a CSV or Excel dataset.
3. The dataset is processed and made available for analysis.
4. The user asks a question in plain English.
5. The application provides the relevant database schema to the SQL agent.
6. Gemini generates an SQL query based on the question and schema.
7. The query is executed against the dataset.
8. The returned result is analyzed.
9. A natural-language insight is generated.
10. A visualization is created when the result is suitable for one.
11. The analysis is stored in the user's history.

This keeps the interaction simple from the user's perspective while several backend components work together behind the scenes.

---

## Key Features

### Natural Language Data Analysis

Users can ask questions about their data using normal language rather than writing SQL manually.

For example:

- Show total sales by region.
- Show total sales by sales representative.
- Which product category generated the highest sales?
- Show the number of customers by city.

The generated SQL is based on the actual schema of the selected dataset.

### Dataset Upload

The application supports uploading structured datasets for analysis.

Supported formats include:

- CSV
- XLSX

Uploaded datasets are processed before they are made available to the SQL analysis workflow.

### AI-Powered SQL Generation

The project uses Google's Gemini API to translate natural-language questions into SQL queries.

The SQL agent receives the relevant table schema and follows instructions to generate SQL that can be executed against the application's database.

The generated query is then passed to the database layer rather than being treated as a text-only response.

### Automatic Insights

After the SQL query is executed, the result is passed through the analysis pipeline.

The application generates a short natural-language explanation of the result so that users do not have to interpret raw query output on their own.

### Data Visualization

When a query result is suitable for visualization, the application generates a chart using Plotly.

For example, grouped numerical results such as sales by region or sales by representative can be displayed visually.

The application does not force a chart for every query. A visualization is generated when the result structure supports one.

### Authentication

The application includes user authentication so that analysis history can be associated with the correct user.

Authenticated requests are handled through the FastAPI backend.

### Persistent Analysis History

Analysis history is stored in the database rather than only inside the Streamlit session.

This means previous analyses can remain available when the user returns to the application.

Each history item can also be deleted individually.

### Data Preview

After uploading a dataset, users can preview the uploaded data directly inside the application before asking analytical questions.

---

## Project Architecture

The project uses a separate frontend and backend.

The frontend is built with Streamlit and handles the user interface and interaction.

The backend is built with FastAPI and is responsible for authentication, dataset processing, SQL generation, analysis, database operations, and API endpoints.

The high-level flow is:

```text
                    ┌──────────────────────┐
                    │      Streamlit       │
                    │      Frontend        │
                    └──────────┬───────────┘
                               │
                               │ HTTP API
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │       Backend        │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          Authentication   Dataset Layer   Analysis Layer
                │              │              │
                │              │              ▼
                │              │        Insight Generation
                │              │
                │              ▼
                │        Database / SQL
                │
                ▼
             User Data

                         ┌───────────────┐
                         │    Gemini     │
                         │   SQL Agent   │
                         └───────┬───────┘
                                 │
                                 ▼
                         Generated SQL


Tech Stack
Frontend    Backend     AI                                                 Database       Data Processing      Development Tools
Python      Python      Google Gemini API                                  SQLite         Pandas               Git
Streamlit   FastAPI     Gemini-based natural-language-to-SQL generation    SQLAlchemy     CSV                  GitHub
Pandas      Uvicorn                                                                       Excel / XLSX         Virtual Environment
Plotly      SQLAlchemy                                                                                         REST APIs


Project Structure
ai-data-analyst-sql-agent/
│
├── app/
│   ├── agents/
│   │   └── sql_agent.py
│   │
│   ├── analysis/
│   │   ├── analysis_pipeline.py
│   │   ├── insight_service.py
│   │   ├── result_analyzer.py
│   │   └── __init__.py
│   │
│   ├── api/
│   │   ├── analysis.py
│   │   ├── upload.py
│   │   └── __init__.py
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── routes.py
│   │   ├── security.py
│   │   └── __init__.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── __init__.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── check_database.py
│   │   ├── loader/
│   │   └── seed/
│   │
│   ├── services/
│   │   ├── dataset_service.py
│   │   ├── schema_service.py
│   │   ├── sql_service.py
│   │   └── __init__.py
│   │
│   ├── visualization/
│   │   ├── chart_service.py
│   │   └── __init__.py
│   │
│   ├── main.py
│   └── __init__.py
│
├── data/
│   └── demo/
│       ├── customers.csv
│       ├── customers_test.xlsx
│       ├── orders.csv
│       └── products.csv
│
├── requirements.txt
├── streamlit_app.py
├── .gitignore
└── README.md

How the SQL Agent Works

The SQL agent is one of the central parts of the application.
When a user asks a question, the application first identifies the dataset table that should be used.
The schema service retrieves information about that table, including its columns and data types.
The relevant schema is then provided to the Gemini model together with the user's question and instructions for generating SQL.
The model generates an SQL query which is then passed to the database layer for execution.
This approach is important because the model is not expected to guess the structure of the data. It receives the actual schema that it needs for the requested analysis.

Data Analysis Pipeline

The analysis pipeline connects the different parts of the application.

The general flow is:

User Question
      │
      ▼
Dataset / Table Selection
      │
      ▼
Schema Retrieval
      │
      ▼
Gemini SQL Generation
      │
      ▼
SQL Validation / Execution
      │
      ▼
Query Result
      │
      ▼
Result Analysis
      │
      ├──────────────► Natural Language Insight
      │
      └──────────────► Visualization (when appropriate)

This separation keeps SQL generation, execution, result analysis, and visualization as separate responsibilities instead of putting everything into one large function.

Authentication

The application includes an authentication layer in the FastAPI backend.
Authenticated users receive an access token that is used when making protected API requests.
The frontend stores the authenticated session information and sends the token with requests that require authentication.
Analysis history is associated with the authenticated user so that one user's history is not exposed to another user.

Analysis History

The application stores completed analyses in the database.
Each history record contains information such as:

The user's question
The dataset/table used
The generated SQL query
The generated insight
The user who performed the analysis
The creation time

Users can select a previous question from the sidebar and can also delete individual history entries.

This was added because analysis history is useful when a user repeatedly works with the same dataset and wants to return to previous questions.

Visualization

The visualization layer is kept separate from the SQL generation and analysis logic. When the query result contains a structure that can be meaningfully visualized, the chart service creates a Plotly chart.

The current implementation supports visualizations such as:

Bar charts
Scatter charts

For example, a question such as:

"Show total sales by sales rep."

can produce a grouped result that is suitable for a bar chart.

For a result where a chart would not add useful information, the application can return the analytical result without forcing a visualization.

Dataset Handling

Uploaded datasets are processed through the dataset service before being used for analysis.

The service handles tasks such as:

File validation
Reading CSV files
Reading Excel files
Cleaning column names
Creating safe database table names
Profiling uploaded datasets

This allows datasets with different file structures to enter the same analysis workflow.

Demo Data

The repository includes a small set of demo datasets for testing and demonstration.

data/demo/
├── customers.csv
├── customers_test.xlsx
├── orders.csv
└── products.csv

These files make it easier to understand the project without having to create a dataset from scratch.

Running the Project Locally
1. Clone the repository
git clone https://github.com/<your-username>/ai-data-analyst-sql-agent.git
cd ai-data-analyst-sql-agent
2. Create a virtual environment

On Windows:

py -3.12 -m venv venv
3. Activate the environment
venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Create the environment file

Create a .env file in the project root.

GEMINI_API_KEY=your_gemini_api_key
COOKIES_PASSWORD=your_secure_cookie_secret

Do not commit this file to GitHub.

The repository already contains a .gitignore rule for .env.

6. Start the FastAPI backend
uvicorn app.main:app --host 127.0.0.1 --port 8001

The backend will be available at:

http://127.0.0.1:8001
7. Start the Streamlit frontend

Open another terminal, activate the virtual environment, and run:

streamlit run streamlit_app.py --server.port 8502

The frontend will be available at:

http://localhost:8502
Environment Variables

The application uses environment variables for configuration and secrets.

Variable	Purpose
GEMINI_API_KEY	API key used to access the Gemini model
COOKIES_PASSWORD	Secret used for encrypted cookie storage
API_BASE_URL	URL of the FastAPI backend used by the Streamlit frontend

Example:

GEMINI_API_KEY=your_gemini_api_key
COOKIES_PASSWORD=your_secure_cookie_secret
API_BASE_URL=http://127.0.0.1:8001

Secret values should never be committed to the repository.

Example Questions

Once a dataset has been uploaded, users can ask questions such as:

Show total sales by region.
Show total sales by sales rep.
Show the number of customers by city.
Which product category has the highest sales?

The exact questions that can be answered depend on the columns available in the uploaded dataset.

Testing the Application

The application was tested locally through the complete user workflow.

The main workflow includes:

Login
  ↓
Upload Dataset
  ↓
Preview Dataset
  ↓
Ask Question
  ↓
Generate SQL
  ↓
Execute SQL
  ↓
Generate Insight
  ↓
Display Visualization
  ↓
Save Analysis History

The application was also tested for authenticated API access, dataset upload, analysis requests, persistent analysis history, individual history deletion, session persistence, and logout behavior.

Error Handling

The application includes error handling across the frontend and backend so that failures in individual components do not expose unnecessary internal details to users.

The SQL generation workflow also includes retry handling for temporary Gemini availability failures.

If the primary model request fails temporarily, the application retries the request before moving to the configured fallback model.

Security Considerations

The project keeps application secrets outside the source code.

The following files and local resources are intentionally excluded from Git:

.env
venv/
__pycache__/
*.db

The local SQLite database is also excluded because it contains application-specific local data and should not be treated as source code.

Authentication-protected endpoints use the authenticated user's identity when accessing user-specific analysis history.

For a production deployment, environment secrets should be configured through the deployment platform rather than committed to the repository.

Current Limitations

This project is primarily designed as a portfolio and learning project.

The current version uses SQLite for database storage, which is convenient for local development but requires additional deployment considerations when persistent production storage is needed.

The SQL generation quality also depends on the language model's ability to correctly interpret the user's question and the provided schema.

For more complex datasets and queries, additional SQL validation, query safety controls, database scaling, and stronger evaluation would be useful future improvements.

Future Improvements

Some areas I would like to explore further include:

More advanced SQL validation and safety checks
Support for additional database engines
More visualization types
Better handling of complex analytical questions
Query result caching
More detailed dataset profiling
Improved conversational follow-up questions
Role-based access control
Production-grade persistent database storage
Automated testing for generated SQL
More robust evaluation of LLM-generated queries


What I Learned

Building this project helped me understand that connecting an LLM to a real application involves much more than simply sending a prompt to a model.

I worked with API design, authentication, database operations, dataset processing, schema extraction, SQL generation, result analysis, visualization, session management, error handling, and Git-based project management.

One of the most useful parts of the project was seeing how the schema, generated SQL, database result, and final explanation have to work together. A good natural-language answer is only useful when the underlying query is appropriate and the result is actually based on the user's data.

The project also gave me practical experience in separating frontend and backend responsibilities instead of putting the entire application into one file.