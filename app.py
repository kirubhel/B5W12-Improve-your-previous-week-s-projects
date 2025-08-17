# app.py

import gradio as gr
from src.rag_pipeline import retrieve_relevant_chunks, build_prompt, generate_answer

def chat_with_rag(question):
    chunks = retrieve_relevant_chunks(question)
    prompt = build_prompt(question, chunks)
    answer = generate_answer(prompt)
    
    sources = "\n\n".join([f"- {c['text'][:300]}..." for c in chunks[:2]])
    
    return answer.strip(), sources

with gr.Blocks() as demo:
    gr.Markdown("# 🧾 Tenx Complaint Chatbot")
    with gr.Row():
        input_box = gr.Textbox(label="Ask a question", placeholder="e.g., What are common issues in money transfers?")
    with gr.Row():
        answer_box = gr.Textbox(label="AI Answer", lines=4)
    with gr.Row():
        sources_box = gr.Textbox(label="Retrieved Complaint Snippets", lines=8)
    with gr.Row():
        submit_btn = gr.Button("Submit")
        clear_btn = gr.Button("Clear")

    submit_btn.click(fn=chat_with_rag, inputs=[input_box], outputs=[answer_box, sources_box])
    clear_btn.click(fn=lambda: ("", ""), inputs=[], outputs=[answer_box, sources_box])

demo.launch()
