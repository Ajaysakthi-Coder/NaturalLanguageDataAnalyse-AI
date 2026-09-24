# NaturalLanguageDataAnalyse-AI
A schema-agnostic AI data analyst that lets users upload datasets, ask questions in natural language, and receive answers, visualizations, and explanations.
# AI Data Analyst

An AI-powered, schema-agnostic data analysis tool that allows users to upload a dataset and ask questions about it using natural language.

Instead of manually writing pandas queries, the system uses an LLM to understand the user's question, generate the required data-analysis operation, execute it on the dataset, and present the result with a visualization and a simple explanation.

## 🚀 Features

* 📂 Analyze CSV datasets
* 🤖 Ask questions about data using natural language
* 🧠 AI-generated pandas operations
* 📊 Automatic result visualization
* 💬 Simple explanation of the analysis
* 🔄 Designed to work with different/unseen dataset schemas
* ❌ Handles questions that cannot be answered from the available data

## 💡 How It Works

```text
        CSV Dataset
             │
             ▼
      ┌─────────────┐
      │ Load Dataset │
      └──────┬──────┘
             │
             ▼
     Detect Dataset Schema
             │
             ▼
      User asks a question
             │
             ▼
       ┌───────────┐
       │    LLM    │
       └─────┬─────┘
             │
             ▼
    Generate pandas operation
             │
             ▼
       Execute on Data
             │
       ┌─────┴─────┐
       ▼           ▼
     Answer      Chart
       │           │
       └─────┬─────┘
             ▼
       Simple Explanation
```

## 🧪 Example

Given a dataset containing:

```text
Product_Name | Total_Value | Units_Sold | Location
---------------------------------------------------
Milk         | 5000        | 250        | Coimbatore
Bread        | 3000        | 300        | Chennai
Eggs         | 4500        | 150        | Madurai
```

A user can ask:

> Which product sold the most units?

The AI can generate an appropriate pandas operation, execute it on the dataset, and return the result along with a visualization.

Another example:

> Total value by location

The system can group the data by location, calculate the total value, and display the result as a chart.

## 🛠️ Tech Stack

* **Python**
* **Pandas** – Data processing
* **Matplotlib** – Data visualization
* **Groq API** – LLM inference
* **LLM models** – Natural-language understanding and code generation

## 📁 Project Structure

```text
ga09/
│
├── analyze.py          # Main data analysis program
├── sales.csv           # Sample dataset
├── chart.png           # Generated visualization
└── README.md           # Project documentation
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

### 2. Install dependencies

```bash
pip install groq pandas matplotlib
```

### 3. Add your Groq API key

The application requires a Groq API key.

For local testing, configure your API key before running the application.

> **Never commit your API key to GitHub.**

### 4. Add a dataset

Place your CSV file in the project directory and configure the filename in `analyze.py`.

For example:

```python
df = pd.read_csv("sales.csv")
```

### 5. Run the application

```bash
python analyze.py
```

Then enter a natural-language question when prompted.

## 🎯 Project Goal

The goal of this project is to make data analysis accessible to users who may not know SQL or pandas.

Instead of requiring users to understand programming syntax, they can interact with their data using ordinary language.

The project also focuses on **schema-agnostic analysis**, meaning the system is intended to work with datasets it has not been specifically programmed for.

## 🔐 Security Considerations

The current prototype generates pandas operations using an LLM and executes the generated expression.

For a production-ready version, the execution layer should be isolated and restricted using techniques such as:

* Operation whitelisting
* Sandboxed execution
* Restricted imports
* Input validation
* Resource and execution limits
* Secure API-key management

## 🔮 Future Improvements

* [ ] Streamlit web interface
* [ ] Excel (`.xlsx`) support
* [ ] More visualization types
* [ ] Better schema and data-type detection
* [ ] Improved handling of unsupported questions
* [ ] Safer code execution
* [ ] AWS S3 integration
* [ ] AWS Lambda backend
* [ ] Amazon Bedrock integration
* [ ] Query history
* [ ] Multi-dataset analysis
* [ ] Deployment as a cloud application

## 🏆 Hackathon Project

This project was developed as part of a hackathon challenge focused on building an AI-powered, schema-agnostic data analysis system.

The project is also a learning exercise in:

* Artificial Intelligence
* Large Language Models
* Data Analysis
* Python
* Cloud Computing
* API integration

## 👥 Team

**Team:** X_Entity

Built with curiosity, experimentation, and a focus on learning through the hackathon.

---

⭐ If you find this project interesting, feel free to explore the code and experiment with your own datasets.

