import google.generativeai as genai
import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

os.environ["GEMINI_API_KEY"] = "AIzaSyBrGN6AipqQoMkCiU7u5YNaH73hoYSAUuU"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


class GraphState(TypedDict):
    prompt: Optional[str] = None
    classification: Optional[str] = None
    response: Optional[str] = None

def classify_text(prompt):
    response = model.generate_content(
        f"classify intent of given input as code_generator or a non_code_generator? Output just the class name. Input:{prompt}",
    ).text
    return str(response).strip()


def classify_text_node(state):
    prompt = state.get("prompt", "").strip()
    classification = classify_text(prompt)
    return {"classification": classification}


def handle_non_code_generator(state):
    return {"response": "I am not a code generator."}


def handle_code_generator(state):
    prompt = state.get("prompt", "").strip()
    response = str(generate_code(prompt))
    return {"response": response}


def exit_node(state):
    current_response = state.get("response", "")
    return {"response": f"{current_response}"}


def generate_code(prompt):
    response = model.generate_content(
        prompt,
    ).text
    return response


def decide_next_node(state):
    classification = state.get("classification")
    if classification == "code_generator":
        return "code_generator"
    elif classification == "non_code_generator":
        return "non_code_generator"
    else:
        raise ValueError(f"Unknown classification: {classification}")



if __name__ == "__main__":
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("classify_text", classify_text_node)
    workflow.add_node("handle_non_code_generator", handle_non_code_generator)
    workflow.add_node("handle_code_generator", handle_code_generator)
    workflow.add_node("exit_node", exit_node)

    # Set entry point
    workflow.set_entry_point("classify_text")

    # Define edges
    # workflow.add_edge("handle_non_code_generator", "exit_node")
    workflow.add_edge("handle_non_code_generator", END)
    workflow.add_edge("handle_code_generator", "exit_node")
    workflow.add_edge("exit_node", END)

    # Add conditional edges
    workflow.add_conditional_edges(
        "classify_text",
        decide_next_node,
        {
            "code_generator": "handle_code_generator",
            "non_code_generator": "handle_non_code_generator",
        },
    )

    # Compile and invoke the app
    app = workflow.compile()
    # result = app.invoke(
    #     {"prompt": "Generate a Python function that returns the sum of two numbers."}
    # )
    result = app.invoke(
        {"prompt": "Hi How are you?"}
    )

    # print(result.get("response"))
    print(result)
    # app.invoke(
    #     {"prompt": "Hi How are you?"}
    # )

    # print(app.get_graph().draw_ascii())