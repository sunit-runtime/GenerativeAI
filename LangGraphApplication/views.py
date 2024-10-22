from LangGraphApplication.serializers import PromptSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from langgraph.graph import StateGraph, END
from .PromptState import PromptState, StateManager


@api_view(["GET"])
def test(request):
    return Response({"message": "Hello, world!"})


@api_view(["POST"])
def collect_input(request):
    serializer = PromptSerializer(data=request.data)
    if serializer.is_valid():
        prompt_data = serializer.validated_data
        try:
            response  = process_prompt(prompt_data["prompt"])
        except Exception as e:
            print(e)
            return Response({"response": f"Error: {e}"}, status=500)

        return Response({"response": response}, status=200)
    else:
        return Response(serializer.errors, status=400)


def process_prompt(prompt):
    app = __workflowInit__()
    result = app.invoke({"prompt": prompt})
    print(app.get_graph().draw_ascii())
    return result


def __workflowInit__():
    workflow = StateGraph(PromptState)

    workflow.add_node("classify_text", StateManager.classify_text_node)
    workflow.add_node(
        "handle_non_code_generator", StateManager.handle_non_code_generator
    )
    workflow.add_node("handle_code_generator", StateManager.handle_code_generator)
    workflow.add_node("generate_test_case", StateManager.generate_test_case)
    workflow.add_node("improve_code", StateManager.improve_code)
    workflow.add_node("execute_code", StateManager.execute_code)
    workflow.add_node("exit_mode", StateManager.exit_mode)

    workflow.set_entry_point("classify_text")
    workflow.add_edge("handle_non_code_generator", "exit_mode")
    workflow.add_edge("handle_code_generator", "generate_test_case")
    workflow.add_edge("generate_test_case", "execute_code")
    workflow.add_edge("improve_code", "execute_code")
    workflow.add_edge("exit_mode", END)

    workflow.add_conditional_edges(
        "classify_text",
        StateManager.decide_next_node,
        {
            "code_generator": "handle_code_generator",
            "non_code_generator": "handle_non_code_generator",
            "exit_mode": "exit_mode",
        },
    )

    workflow.add_conditional_edges(
        "execute_code",
        StateManager.decide_execute_code,
        {
            "exit_mode": "exit_mode",
            "improve_mode": "improve_code",
            "regenerate_mode": "generate_test_case",
        },
    )

    app = workflow.compile()
    return app
