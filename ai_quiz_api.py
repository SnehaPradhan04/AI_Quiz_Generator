# -*- coding: utf-8 -*-
"""AI_quiz_API.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dQ9t3mtlZkNv3lOUXz4jgJqLLHHQzVgI
"""

!pip install openai gradio spacy
!python -m spacy download en_core_web_sm

!pip install openai==0.28

import openai
import gradio as gr
import spacy
import re
import os

openai.api_key = "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"  # Replace with your actual OpenAI API key

nlp = spacy.load("en_core_web_sm")

def extract_key_terms(text):
    """Extract key terms using Named Entity Recognition (NER)."""
    doc = nlp(text)
    return ", ".join([ent.text for ent in doc.ents])

def generate_mcq(text):
    """Generate an MCQ from input text using OpenAI API."""
    prompt = f"""Generate a multiple-choice question with four answer choices and the correct answer from the following text:
    \n{text}\n
    Format the response strictly as follows:
    Question: <question text>
    Options:
    A) <option 1>
    B) <option 2>
    C) <option 3>
    D) <option 4>
    Answer: <correct option letter (A/B/C/D)>"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an AI that generates multiple-choice questions."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )

    mcq_text = response["choices"][0]["message"]["content"]

    match = re.match(r"Question:\s*(.*?)\nOptions:\s*A\)\s*(.*?)\nB\)\s*(.*?)\nC\)\s*(.*?)\nD\)\s*(.*?)\nAnswer:\s*([ABCD])", mcq_text, re.DOTALL)

    if match:
        question = match.group(1).strip()
        options = [
            f"A) {match.group(2).strip()}",
            f"B) {match.group(3).strip()}",
            f"C) {match.group(4).strip()}",
            f"D) {match.group(5).strip()}",
        ]
        correct_option = match.group(6).strip()
    else:
        question = "Could not extract question properly."
        options = ["Option A", "Option B", "Option C", "Option D"]
        correct_option = "A"

    return question, options, correct_option

def check_answer(user_answer, correct_answer):
    """If the user's selected answer is correct."""
    if user_answer.startswith(correct_answer):
        return "✅ Correct!"
    else:
        return f"❌ Incorrect! The correct answer is {correct_answer}."
def process_text(text):
    """Generate MCQ and return UI components."""
    key_terms = extract_key_terms(text)
    question, options, correct_option = generate_mcq(text)

    return key_terms, question, gr.update(choices=options, value=options[0]), correct_option

with gr.Blocks() as app:
    gr.Markdown("# 🧠 AI-Powered Quiz Generator")
    gr.Markdown("Enter a paragraph of text, and the AI will generate a multiple-choice quiz for you.")

    text_input = gr.Textbox(label="Enter a paragraph of text")
    generate_btn = gr.Button("Generate MCQ")

    key_terms_output = gr.Textbox(label="Key Terms Identified")
    question_output = gr.Textbox(label="Generated Question")
    options_output = gr.Radio([], label="Choose your answer")
    correct_option_output = gr.Textbox(visible=False)
    check_btn = gr.Button("Check Answer")
    feedback_output = gr.Textbox(label="Result")

    def update_options(text):
        key_terms, question, options, correct_option = process_text(text)
        return key_terms, question, options, correct_option

    def validate_answer(selected, correct):
        return check_answer(selected, correct)

    generate_btn.click(update_options, inputs=[text_input], outputs=[key_terms_output, question_output, options_output, correct_option_output])
    check_btn.click(validate_answer, inputs=[options_output, correct_option_output], outputs=[feedback_output])

app.launch()