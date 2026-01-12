import os
import gradio as gr
from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime
import csv
from pathlib import Path

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

# Model mapping to Groq model IDs (updated for current availability)
MODEL_MAP = {
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "GPT OSS 20B": "openai/gpt-oss-20b",
    "GPT OSS 120B": "openai/gpt-oss-120b"
}

# Max tokens for output length
LENGTH_MAP = {
    "Short": 150,
    "Medium": 500,
    "Full": 1500
}

# Storage for preferences (in-memory for now)
preferences_data = []

def save_preference_to_storage(question, output_length, selected_model, all_results):
    """
    Save preference data to persistent storage.
    Currently saves to CSV file. Can be extended to use database in the future.
    Saves all model responses for later comparison.
    """
    csv_file = "preferences.csv"
    file_exists = Path(csv_file).exists()
    
    # Prepare all responses as JSON
    all_responses = {result["model"]: result["response"] for result in all_results}
    
    # Write to CSV
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow([
                'timestamp', 'question', 'output_length', 
                'selected_model', 'all_models_compared', 'all_responses_json'
            ])
        
        # Write preference data
        writer.writerow([
            datetime.now().isoformat(),
            question,
            output_length,
            selected_model,
            '|'.join(all_responses.keys()),
            json.dumps(all_responses, ensure_ascii=False)
        ])

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
with gr.Blocks(title="Multi-Model LLM Comparison Tool") as demo:
    gr.Markdown("# Multi-Model LLM Comparison Tool")
    gr.Markdown("### Compare answers")
    
    # Store results in state
    results_state = gr.State([])
    
    with gr.Row():
        with gr.Column() as input_section:
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
        
        # Results with integrated buttons
        with gr.Column() as results_container:
            result_card_1 = gr.Markdown(visible=False, elem_classes="model-card")
            pref_btn_1 = gr.Button("This one works for me", elem_classes="preference-button", visible=False)
            
            result_card_2 = gr.Markdown(visible=False, elem_classes="model-card")
            pref_btn_2 = gr.Button("This one works for me", elem_classes="preference-button", visible=False)
            
            result_card_3 = gr.Markdown(visible=False, elem_classes="model-card")
            pref_btn_3 = gr.Button("This one works for me", elem_classes="preference-button", visible=False)
            
            result_card_4 = gr.Markdown(visible=False, elem_classes="model-card")
            pref_btn_4 = gr.Button("This one works for me", elem_classes="preference-button", visible=False)
        
        # Preference status
        preference_status = gr.Markdown()
        
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
                input_section: gr.Column(visible=True),
                results_section: gr.Column(visible=False),
                results_state: [],
                result_card_1: gr.Markdown(visible=False),
                pref_btn_1: gr.Button(visible=False),
                result_card_2: gr.Markdown(visible=False),
                pref_btn_2: gr.Button(visible=False),
                result_card_3: gr.Markdown(visible=False),
                pref_btn_3: gr.Button(visible=False),
                result_card_4: gr.Markdown(visible=False),
                pref_btn_4: gr.Button(visible=False)
            }
        
        # Build results
        question_info = f"**Your question:** {question}  \n**Answer length:** {output_length}"
        
        num_results = len(results)
        
        # Create individual card HTML and button updates
        card_updates = {}
        btn_updates = {}
        
        for i in range(4):
            if i < num_results:
                model = results[i]["model"]
                response = results[i]["response"]
                # Use markdown with HTML wrapper for styling
                card_content = f"""<div class='model-title'>{model}</div>
<div class='answer-length'>{output_length} answer</div>

---

{response}"""
                card_updates[f"result_card_{i+1}"] = gr.Markdown(value=card_content, visible=True)
                btn_updates[f"pref_btn_{i+1}"] = gr.Button(value=f"This one works for me - {model}", visible=True)
            else:
                card_updates[f"result_card_{i+1}"] = gr.Markdown(visible=False)
                btn_updates[f"pref_btn_{i+1}"] = gr.Button(visible=False)
        
        return {
            error_msg: gr.Markdown(visible=False),
            input_section: gr.Column(visible=False),
            results_section: gr.Column(visible=True),
            question_display: gr.Markdown(value=question_info),
            results_state: results,
            result_card_1: card_updates["result_card_1"],
            pref_btn_1: btn_updates["pref_btn_1"],
            result_card_2: card_updates["result_card_2"],
            pref_btn_2: btn_updates["pref_btn_2"],
            result_card_3: card_updates["result_card_3"],
            pref_btn_3: btn_updates["pref_btn_3"],
            result_card_4: card_updates["result_card_4"],
            pref_btn_4: btn_updates["pref_btn_4"]
        }
    
    def record_preference(model_index, question, output_length, results):
        """Record user preference for a specific model"""
        if not results or model_index >= len(results):
            return {
                input_section: gr.Column(visible=True),
                results_section: gr.Column(visible=False),
                error_msg: gr.Markdown(visible=False)
            }
        
        # Get selected model info
        selected_model = results[model_index]["model"]
        
        # Save preference using storage function with all results
        save_preference_to_storage(
            question=question,
            output_length=output_length,
            selected_model=selected_model,
            all_results=results
        )
        
        # Return to input screen
        return {
            input_section: gr.Column(visible=True),
            results_section: gr.Column(visible=False),
            error_msg: gr.Markdown(visible=False)
        }
    
    def go_back():
        """Return to input screen"""
        return {
            input_section: gr.Column(visible=True),
            results_section: gr.Column(visible=False),
            error_msg: gr.Markdown(visible=False)
        }
    
    # Event handlers
    compare_btn.click(
        fn=show_results,
        inputs=[question_input, output_length] + model_checkboxes,
        outputs=[error_msg, input_section, results_section, question_display, results_state,
                 result_card_1, pref_btn_1, result_card_2, pref_btn_2,
                 result_card_3, pref_btn_3, result_card_4, pref_btn_4]
    )
    
    back_btn.click(
        fn=go_back,
        outputs=[input_section, results_section, error_msg]
    )
    
    # Preference button handlers
    pref_btn_1.click(
        fn=lambda q, ol, r: record_preference(0, q, ol, r),
        inputs=[question_input, output_length, results_state],
        outputs=[input_section, results_section, error_msg]
    )
    
    pref_btn_2.click(
        fn=lambda q, ol, r: record_preference(1, q, ol, r),
        inputs=[question_input, output_length, results_state],
        outputs=[input_section, results_section, error_msg]
    )
    
    pref_btn_3.click(
        fn=lambda q, ol, r: record_preference(2, q, ol, r),
        inputs=[question_input, output_length, results_state],
        outputs=[input_section, results_section, error_msg]
    )
    
    pref_btn_4.click(
        fn=lambda q, ol, r: record_preference(3, q, ol, r),
        inputs=[question_input, output_length, results_state],
        outputs=[input_section, results_section, error_msg]
    )

if __name__ == "__main__":
    demo.launch(css=custom_css)
