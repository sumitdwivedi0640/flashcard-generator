# flashcard-generator
Absolutely! Here’s a **detailed explanation** of your LLM-Powered Flashcard Generator project and a **step-by-step guide** to set it up and run it on your system.

---

# 📚 Project Overview: LLM-Powered Flashcard Generator

## **What is it?**
This project is a web app that uses Large Language Models (LLMs) like OpenAI GPT or Cohere to automatically generate question-answer flashcards from educational content (textbook excerpts, lecture notes, etc.). It’s designed for students, teachers, and self-learners to quickly create study materials.

---

## **Key Features**
- **Input Methods:** Upload `.txt` or `.pdf` files, or paste text directly.
- **LLM Integration:** Uses OpenAI GPT or Cohere to generate flashcards.
- **Flashcard Format:** Each card has a clear question and a self-contained answer.
- **Bonus Features:**  
  - Difficulty levels (Easy/Medium/Hard)
  - Topic grouping (if detected)
  - Export to CSV, JSON, Anki, or Quizlet formats
  - Edit and review flashcards before export
  - Multi-language support (if LLM supports it)
- **User Interface:** Built with Streamlit for a simple, interactive web experience.

---

## **How Does It Work?**
1. **User uploads or pastes educational content.**
2. **User selects options** (subject, language, number of cards, etc.).
3. **App sends a prompt to the LLM** (OpenAI or Cohere) to generate flashcards.
4. **LLM returns flashcards** in Q&A format.
5. **User can review, edit, and export** the flashcards in various formats.

---

# 🖥️ How to Set Up and Run on Your System

## **1. Prerequisites**
- **Python 3.8+** installed ([Download Python](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **An OpenAI or Cohere API key** (Cohere is free for small usage, OpenAI may require payment)

---

## **2. Clone or Download the Project**
If you have git:
```sh
git clone <your-repo-url>
cd <project-folder>
```
Or download and unzip the project, then open a terminal in the project folder.

---

## **3. Install Dependencies**
```sh
python -m pip install -r requirements.txt
```
If you want to use Cohere, also run:
```sh
python -m pip install cohere
```

---

## **4. Set Up Your API Key**
- **For Cohere:**  
  Go to [Cohere Dashboard](https://dashboard.cohere.com/api-keys), create an API key, and copy it.
- **For OpenAI:**  
  Go to [OpenAI API Keys](https://platform.openai.com/api-keys), create a key, and copy it.

**Create a `.env` file** in your project folder with this content (choose one provider):
```
# For Cohere
COHERE_API_KEY=your-cohere-key-here

# For OpenAI (if you want to use OpenAI instead)
# OPENAI_API_KEY=your-openai-key-here
```

---

## **5. Run the App**
```sh
streamlit run app.py
```
- The terminal will show a local URL (e.g., http://localhost:8501).
- Open this URL in your browser.

---

## **6. Use the App**
- **Input Tab:** Upload a file or paste your text.
- **Generate Tab:** Click “Generate Flashcards” to create cards.
- **Edit Tab:** Review and edit the generated flashcards.
- **Export Tab:** Download your flashcards in your preferred format.

---

## **7. Troubleshooting**
- **API Key Errors:** Make sure your `.env` file is correct and you have credits/quota.
- **No Flashcards Generated:** Try using simpler, more explicit prompts or check your API quota.
- **Red Error Boxes:** These are normal for errors; read the message for details.

---

# 📝 Example `.env` File

For Cohere:
```
COHERE_API_KEY=7wMdexyRWutu2u0Uk0V5j65PKqgsuQowHdxYD4W4
```
For OpenAI:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

# 🏁 Summary

- **This project**: Converts educational content into flashcards using AI.
- **You need**: Python, dependencies, and an API key.
- **How to run**: Install, set up `.env`, and run with Streamlit.
- **How to use**: Upload/paste content, generate, edit, and export flashcards.

---

**If you want a video demo, screenshots, or have any issues, just ask!**
