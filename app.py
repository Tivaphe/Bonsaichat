import os
import json
import uuid
import gradio as gr
from models_manager import MODELS, list_downloaded_models, download_model, get_model_file
from inference import engine

# Configuration
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "history")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(HISTORY_DIR, exist_ok=True)

# Helper functions
def load_session_history():
    sessions = []
    for f in sorted(os.listdir(HISTORY_DIR), reverse=True):
        if f.endswith(".json"):
            with open(os.path.join(HISTORY_DIR, f), "r") as file:
                try:
                    data = json.load(file)
                    sessions.append((data.get("id"), data.get("title", f)))
                except:
                    pass
    return sessions

def save_session(session_id, messages, title=None):
    if not title and messages:
        # messages is list of dicts
        first_msg = messages[0]["content"]
        title = first_msg[:30] + "..."
    elif not title:
        title = "New Conversation"

    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    with open(file_path, "w") as f:
        json.dump({"id": session_id, "title": title, "messages": messages}, f)

def delete_session(session_id):
    if not session_id:
        return gr.update()
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    return gr.update(choices=load_session_history(), value=None)

def rename_session(session_id, new_title):
    if not session_id or not new_title:
        return gr.update()
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        data["title"] = new_title
        with open(file_path, "w") as f:
            json.dump(data, f)
    return gr.update(choices=load_session_history(), value=session_id)

def load_session(session_id):
    if not session_id:
        return [], str(uuid.uuid4())
    messages = get_session_messages(session_id)
    return messages, session_id

def get_session_messages(session_id):
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f).get("messages", [])
    return []

# Gradio UI logic
def chatbot_response(message, history, model_name, temp, max_tokens, session_id):
    if not model_name:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "Please select a model first."})
        yield history
        return

    model_file = get_model_file(model_name)
    if not model_file:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"Model {model_name} not found. Please download it first."})
        yield history
        return

    # Load/Ensure model
    try:
        engine.load_model(model_file)
    except Exception as e:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"Error loading model: {str(e)}"})
        yield history
        return

    # Prepare messages
    history.append({"role": "user", "content": message})

    # Stream response
    full_response = ""
    history.append({"role": "assistant", "content": ""})

    try:
        response_stream = engine.chat_completion(
            messages=history[:-1], # pass all except the empty assistant msg
            temperature=temp,
            max_tokens=max_tokens,
            stream=True
        )

        for chunk in response_stream:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                full_response += content
                history[-1]["content"] = full_response
                yield history

        # Save session after completion
        save_session(session_id, history)
    except Exception as e:
        history[-1]["content"] = f"Error: {str(e)}"
        yield history

def handle_model_download(model_name):
    if not model_name:
        return gr.update(value="Please select a model."), gr.update()

    try:
        download_model(model_name)
        return gr.update(value=f"Model {model_name} downloaded successfully!"), gr.update(choices=list_downloaded_models())
    except Exception as e:
        return gr.update(value=f"Error downloading {model_name}: {str(e)}"), gr.update()

def start_new_chat():
    return [], str(uuid.uuid4())

# Build the Gradio app
with gr.Blocks(title="Bonsai Chat") as demo:
    session_id = gr.State(str(uuid.uuid4()))

    with gr.Row(elem_classes=["header-container"]):
        logo_path = os.path.join(ASSETS_DIR, "logo.svg")
        if os.path.exists(logo_path):
            gr.Image(logo_path, show_label=False, container=False, elem_classes=["header-logo"], height=48, width=48)
        gr.Markdown("# Bonsai Chat", elem_classes=["header-title"])

    with gr.Row():
        # Sidebar
        with gr.Column(scale=1, variant="panel", elem_classes=["sidebar"]):
            gr.Markdown("### Conversations")
            with gr.Row():
                history_dropdown = gr.Dropdown(label="History", choices=load_session_history(), interactive=True, scale=4)
                refresh_btn = gr.Button("🔄", scale=1)
            rename_input = gr.Textbox(label="Rename Session", placeholder="New title...")
            rename_btn = gr.Button("✏️ Rename", variant="secondary")
            new_chat_btn = gr.Button("🌿 New Chat", variant="primary")
            delete_chat_btn = gr.Button("🗑️ Delete", variant="secondary")

            gr.Markdown("---")
            gr.Markdown("### Model Settings")
            model_select = gr.Dropdown(label="Select Model", choices=list(MODELS.keys()), value="Bonsai-1.7B")
            download_btn = gr.Button("⬇️ Download Model")
            status_msg = gr.Markdown("")

            gr.Markdown("### Parameters")
            temp_slider = gr.Slider(0.1, 1.0, value=0.5, step=0.1, label="Temperature")
            max_tokens_slider = gr.Slider(128, 4096, value=2048, step=128, label="Max Tokens")

        # Main Chat Area
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(elem_id="chatbot", height=600)
            with gr.Row():
                msg_input = gr.Textbox(placeholder="Type your message here...", show_label=False, scale=8)
                submit_btn = gr.Button("Send", scale=1, variant="primary")

    # CSS and Theme (Gradio 5.x/6.x way)
    # Actually demo.css_paths was set in the first attempt, but Gradio 6.0 uses launch() parameters.
    # However, to keep it simple and compatible:

    # Event handlers
    def on_submit(message, history, model, temp, tokens, sid):
        return chatbot_response(message, history, model, temp, tokens, sid)

    submit_btn.click(on_submit, [msg_input, chatbot, model_select, temp_slider, max_tokens_slider, session_id], [chatbot])
    msg_input.submit(on_submit, [msg_input, chatbot, model_select, temp_slider, max_tokens_slider, session_id], [chatbot])

    download_btn.click(handle_model_download, [model_select], [status_msg, model_select])
    new_chat_btn.click(start_new_chat, None, [chatbot, session_id])

    def on_history_change(sid):
        messages, new_sid = load_session(sid)
        return messages, new_sid

    history_dropdown.change(on_history_change, [history_dropdown], [chatbot, session_id])
    refresh_btn.click(lambda: gr.update(choices=load_session_history()), None, [history_dropdown])
    delete_chat_btn.click(delete_session, [session_id], [history_dropdown]).then(start_new_chat, None, [chatbot, session_id])
    rename_btn.click(rename_session, [session_id, rename_input], [history_dropdown])

    # Reset input after submit
    submit_btn.click(lambda: "", None, [msg_input])
    msg_input.submit(lambda: "", None, [msg_input])

    # CSS Injection (Alternative way for Blocks)
    style_path = os.path.join(ASSETS_DIR, "style.css")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            demo.css = f.read()

if __name__ == "__main__":
    demo.launch()
