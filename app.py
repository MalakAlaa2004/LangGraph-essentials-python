import os
import sys
import gradio as gr

# Import the sales assistant graph directly
from deepAgentCourse.5_sales_assistant import graph

# Session tracking state
session_thread = {"configurable": {"thread_id": "huggingface-sales-thread"}}

def handle_customer_query(query, chat_history):
    if not query.strip():
        return "", chat_history, "No query entered.", "Pending", "N/A", "Awaiting input..."

    chat_history = chat_history or []
    
    # 1. Initialize deal state
    initial_state = {
        "customer_query": query,
        "inventory_checked": False,
        "quote_calculated": 0.0,
        "manager_approved": False,
        "response": "",
        "logs": []
    }
    
    # 2. Invoke graph up to the interrupt gate
    print(f"--- HF Invoking Graph for Query: '{query}' ---")
    result = graph.invoke(initial_state, session_thread)
    
    # Check the state after pause
    state_values = graph.get_state(session_thread).values
    
    logs_str = "\n".join([f"• {log}" for log in state_values.get("logs", [])])
    quote_val = f"${state_values.get('quote_calculated', 0.0):,.2f}"
    inventory_status = "Checked (Available) ✅" if state_values.get("inventory_checked") else "Pending"
    manager_status = "Awaiting Manager Approval ⏳"
    
    bot_reply = "Your request has been received. Since a pricing override/discount was requested, the deal has been paused and is currently awaiting manager validation."
    chat_history.append((query, bot_reply))
    
    return "", chat_history, logs_str, manager_status, quote_val, inventory_status

def approve_and_resume(chat_history):
    chat_history = chat_history or []
    
    # Check current state to ensure there is a paused thread
    state_values = graph.get_state(session_thread).values
    if not state_values:
        return chat_history, "No active deal thread found. Please submit a query first.", "N/A", "N/A", "N/A"
        
    # 1. Update state with manager approval
    print("--- HF: Manager Approved. Resuming Graph ---")
    graph.update_state(session_thread, {"manager_approved": True})
    
    # 2. Resume graph
    res = graph.invoke(None, session_thread)
    
    final_logs = "\n".join([f"• {log}" for log in res.get("logs", [])])
    quote_val = f"${res.get('quote_calculated', 0.0):,.2f}"
    inventory_status = "Checked (Available) ✅" if res.get("inventory_checked") else "Pending"
    manager_status = "Approved ✅"
    
    bot_reply = f"Invoice compiled! Total: {quote_val}. The contract is signed and ready."
    chat_history.append(("Manager Action: Approve Deal", bot_reply))
    
    return chat_history, final_logs, manager_status, quote_val, inventory_status

# Define Gradio Theme and Layout
with gr.Blocks(theme=gr.themes.Soft(), title="B2B Sales Assistant Hub") as demo:
    gr.Markdown("# 🤖 B2B Tech Sales Assistant Simulator")
    gr.Markdown("Interact with the sales assistant agent. Request pricing updates, and simulate the manager approval flow.")
    
    with gr.Row():
        # Chat column
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Conversation Logs", height=400)
            query_input = gr.Textbox(
                label="Customer message", 
                placeholder="e.g. I want to buy the Cloud Suite, but I need a 15% discount.",
                lines=2
            )
            
            with gr.Row():
                submit_btn = gr.Button("Send Message", variant="primary")
                approve_btn = gr.Button("Approve Deal (Manager Loop)", variant="success")
                
        # Telemetry / State column
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Live Agent State Telemetry")
            quote_display = gr.Label(value="N/A", label="Calculated Quote Value")
            inventory_display = gr.Label(value="N/A", label="CRM Inventory Check")
            manager_display = gr.Label(value="Awaiting Input...", label="Sales Manager Status")
            
            gr.Markdown("### 📝 Internal Node Logs")
            logs_display = gr.Textbox(
                label="Execution steps",
                value="Awaiting graph execution...",
                lines=8,
                interactive=False
            )

    # Wire actions
    submit_btn.click(
        fn=handle_customer_query,
        inputs=[query_input, chatbot],
        outputs=[query_input, chatbot, logs_display, manager_display, quote_display, inventory_display]
    )
    
    approve_btn.click(
        fn=approve_and_resume,
        inputs=[chatbot],
        outputs=[chatbot, logs_display, manager_display, quote_display, inventory_display]
    )

if __name__ == "__main__":
    demo.launch()
