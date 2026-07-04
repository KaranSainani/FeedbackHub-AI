# 📊 FeedbackHub AI — B2B Online Reputation & Insights Platform with AI

**FeedbackHub AI** is an interactive, data-driven web application designed for local businesses and B2B managers to consolidate, analyze, and automate customer review management in real-time. 

The platform combines robust analytics data processing with the power of the **Google Gemini 2.5 Flash** model to extract critical business insights and automatically draft empathetic, professional responses.

---

## 🚀 Key Features

*   **📈 Advanced Analytical Dashboard (KPIs):** Instant visualization of total review volume, business average rating, and automated counters tracking critical alerts (reviews with ≤ 2 stars).
*   **📊 Dynamic Statistical Charts:** Interactive bar chart displaying the overall distribution of star ratings, and a line chart monitoring the business's historical reputation timeline.
*   **🔍 Reactive Real-Time Filters:** Smart search filtering by keywords (scanning both comments and customer names) and dynamic segmentation by star level from the sidebar.
*   **🧠 On-Demand Unitary Review Analysis:** A dedicated tab where managers can paste any standalone customer comment to generate a structured 3-part AI report (Sentiment, Key Insight, and Proposed Response).
*   **📂 Flexible Data Management:** Supports bulk history uploads via CSV files (with built-in comment duplication checks), manual individual registration forms, and record deletion by ID.
*   **📥 Data Exporting:** Integrated download button to export the currently filtered dataset into a clean CSV file fully compatible with Microsoft Excel, Google Sheets, and Apple Numbers.

---

## 🛠️ Architecture and Tech Stack

*   **Frontend / UI:** [Streamlit](https://streamlit.io/) (A reactive Python framework for building data dashboards).
*   **Data Processing:** [Pandas](https://pandas.pydata.org/) (DataFrame manipulation, dynamic time-series aggregation, and strict column formatting).
*   **AI Engine:** [Google Gemini API (v1 REST via `requests`)](https://ai.google.dev/). Built using optimized HTTP POST requests directly to Google's REST endpoint to prevent Python SDK backward-compatibility version issues.
*   **State Management:** Advanced implementation of persistent session states (`st.session_state`) in Python.

---

## 🔧 Installation and Local Setup

Follow these steps to spin up the project locally on your machine:

**1. Clone this repository:**
  git clone [https://github.com/](https://github.com/)[YOUR_GITHUB_USERNAME]/FeedbackHub-AI.git<br>
  cd feedbackhub-ai
   
**2. Install all required dependencies:**
  pip install -r requirements.txt


**3. Configure your Environment Variables:**
  Create a secret file named .env in the root folder of the project and add your Google AI API key:
  GEMINI_API_KEY=your_secret_api_key_here

**4. Launch the application:**
  streamlit run main.py

**5. Dependencies (requirements.txt)**
  To ensure a seamless setup in any environment, create a file named requirements.txt in your root folder with these exact dependencies:

  streamlit<br>
  pandas<br>
  requests<br>
  python-dotenv
