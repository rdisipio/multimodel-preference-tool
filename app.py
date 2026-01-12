import os
import gradio as gr
from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables (for local development)
load_dotenv()

# Get API key from environment
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. "
        "Please add it as a Space secret or in your .env file for local development."
    )

# Initialize Groq client
client = Groq(api_key=api_key)

# Model mapping to Groq model IDs
MODEL_MAP = {
    "GPT-4": "llama-3.3-70b-versatile",  # Using Llama as GPT-4 alternative
    "Claude 3 Opus": "llama-3.1-70b-versatile",  # Using different Llama variant
    "Gemini Pro": "mixtral-8x7b-32768",
    "Llama 2 70B": "llama2-70b-4096",
    "Mistral Large": "mixtral-8x7b-32768"
}

# Max tokens for output length
LENGTH_MAP = {
    "Short": 150,
    "Medium": 500,
    "Full": 1500
}

# Storage for preferences (in-memory for now)
preferences_data = []

def query_model(model_name, question, max_tokens):
    """Query a single model via Groq API"""
    try:
        model_id = MODEL_MAP.get(model_name)
        if not model_id:
            return f"Model {model_name} not available"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model=model_id,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def compare_models(question, output_length, *selected_models):
    """Compare multiple models and return results"""
    # Filter selected models
    selected = [model for model, is_selected in zip(MODEL_MAP.keys(), selected_models) if is_selected]
    
    if not question.strip():
        return None, "Please enter a question."
    
    if not selected:
        return None, "Please select at least one model."
    
    max_tokens = LENGTH_MAP[output_length]
    results = []
    
    for model_name in selected:
        response = query_model(model_name, question, max_tokens)
        results.append({
            "model": model_name,
            "response": response
        })
    
    return results, None

def record_preference(question, output_length, selected_model, all_results):
    """Record user preference"""
    preference = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "output_length": output_length,
        "selected_model": selected_model,
        "all_models": [r["model"] for r in all_results]
    }
    preferences_data.append(preference)
    return f"✓ Preference recorded: {selected_model}"

# Custom CSS
custom_css = """
.model-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin: 10px 0;
    background: white;
}

.model-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
}

.answer-length {
    font-size: 12px;
    color: #666;
    margin-bottom: 12px;
}

.response-text {
    font-size: 14px;
    line-height: 1.6;
    color: #444;
    margin-bottom: 16px;
}

.compare-button {
    background: #6366f1 !important;
    border: none !important;
    color: white !important;
    font-size: 16px !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    width: 100% !important;
}

.preference-button {
    background: #3b82f6 !important;
    border: none !important;
    color: white !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    border-radius: 6px !important;
    width: 100% !important;
}

.output-length-radio label {
    padding: 8px 16px !important;
    border-radius: 20px !important;
    margin: 0 4px !important;
}

#component-0 {
    max-width: 1200px;
    margin: 0 auto;
}

.privacy-note {
    font-size: 12px;
    color: #666;
    text-align: center;
    margin-top: 20px;
}
"""

# Build Gradio interface
with gr.Blocks(css=custom_css, title="Multi-Model LLM Comparison Tool") as demo:
    gr.Markdown("# Multi-Model LLM Comparison Tool")
    gr.Markdown("### Compare answers")
    
    # Store results in state
    results_state = gr.State([])
    
    with gr.Row():
        with gr.Column():
            # Question input
            question_input = gr.Textbox(
                label="Ask a question",
                placeholder="e.g., Who is the Snow Maiden?",
                lines=4
            )
            
            # Output length selector
            output_length = gr.Radio(
                choices=["Short", "Medium", "Full"],
                value="Medium",
                label="Output length",
                info="Controls how detailed each answer is",
                elem_classes="output-length-radio"
            )
            
            # Model selection
            gr.Markdown("**Choose models**")
            model_checkboxes = []
            with gr.Row():
                for model_name in MODEL_MAP.keys():
                    checkbox = gr.Checkbox(label=model_name, value=False)
                    model_checkboxes.append(checkbox)
            
            # Compare button
            compare_btn = gr.Button("Compare answers", elem_classes="compare-button")
            
            error_msg = gr.Markdown(visible=False)
            
    # Results section
    with gr.Column(visible=False) as results_section:
        gr.Markdown("---")
        
        # Back button
        back_btn = gr.Button("← Back", size="sm")
        
        # Display question info
        question_display = gr.Markdown()
        
        # Results container
        results_container = gr.Column()
        
    # Privacy footer
    gr.Markdown(
        "**Do not sell or share my personal info** | Built by the Human Feedback Foundation | Linux Foundation AI & Data member",
        elem_classes="privacy-note"
    )
    
    def show_results(question, output_length, *selected):
        """Handle comparison and display results"""
        results, error = compare_models(question, output_length, *selected)
        
        if error:
            return {
                error_msg: gr.Markdown(value=f"⚠️ {error}", visible=True),
                results_section: gr.Column(visible=False),
                results_state: []
            }
        
        # Build results UI
        results_html = []
        for result in results:
            model = result["model"]
            response = result["response"]
            
            card_html = f"""
            <div class="model-card">
                <div class="model-title">{model}</div>
                <div class="answer-length">{output_length} answer</div>
                <div class="response-text">{response}</div>
            </div>
            """
            results_html.append(card_html)
        
        question_info = f"**Your question:** {question}  \n**Answer length:** {output_length}"
        
        # Create preference buttons
        pref_buttons = []
        for result in results:
            with gr.Row():
                btn = gr.Button(
                    f"This one works for me ({result['model']})",
                    elem_classes="preference-button"
                )
                pref_buttons.append((btn, result['model']))
        
        return {
            error_msg: gr.Markdown(visible=False),
            results_section: gr.Column(visible=True),
            question_display: gr.Markdown(value=question_info),
            results_state: results
        }
    
    def go_back():
        """Return to input screen"""
        return {
            results_section: gr.Column(visible=False),
            error_msg: gr.Markdown(visible=False)
        }
    
    # Event handlers
    compare_btn.click(
        fn=show_results,
        inputs=[question_input, output_length] + model_checkboxes,
        outputs=[error_msg, results_section, question_display, results_state]
    ).then(
        fn=lambda results: [
            gr.HTML(
                f"""
                <div class="model-card">
                    <div class="model-title">{r['model']}</div>
                    <div class="answer-length">Medium answer</div>
                    <div class="response-text">{r['response']}</div>
                </div>
                """
            ) for r in results
        ] if results else [],
        inputs=[results_state],
        outputs=[results_container]
    )
    
    back_btn.click(
        fn=go_back,
        outputs=[results_section, error_msg]
    )

if __name__ == "__main__":
    demo.launch()
