from typing import TypedDict, Optional
import google.generativeai as genai
from django.conf import settings
from . import utils

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


class PromptState(TypedDict):
    prompt: Optional[str] = None
    classification: Optional[str] = None
    response: Optional[str] = None
    success: Optional[bool] = False
    test_case: Optional[str] = None
    execution_result: Optional[str] = None
    failure: Optional[str] = None
    error: Optional[str] = None
    accuracy: Optional[float] = 0.0
    count: Optional[int] = 0
    best_code: Optional[str] = None
    best_accuracy: Optional[float] = 0.0
    best_code_execution_result: Optional[str] = None


class StateManager:

    @staticmethod
    def classify_text(prompt):
        response = StateManager.request_to_gemini(
            f"classify intent of given input as code_generator or a non_code_generator? Output just the class name. Input:{prompt}",
        )
        return str(response).strip()

    @staticmethod
    def classify_text_node(state):
        prompt = state.get("prompt", "").strip()
        classification = StateManager.classify_text(prompt)
        return {"classification": classification}

    @staticmethod
    def handle_non_code_generator(state):
        return {"response": "I am a code generator. Please check Prompt.", "success": False}

    @staticmethod
    def handle_code_generator(state):
        prompt = state.get("prompt", "").strip()
        response = str(StateManager.generate_code(prompt))
        return {"response": response, "success": True, "count": 0}

    @staticmethod
    def exit_mode(state):
        current_response = state.get("response", "")
        return {"response": f"{current_response}"}

    @staticmethod
    def generate_code(prompt):
        response = StateManager.request_to_gemini(
            prompt + ". Give me only function code nothing else."
        )
        return response

    @staticmethod
    def decide_next_node(state):
        classification = state.get("classification")
        if classification == "code_generator":
            return "code_generator"
        elif classification == "non_code_generator":
            return "non_code_generator"
        else:
            return "exit_mode"

    @staticmethod
    def decide_execute_code(state):
        accuracy = state.get("accuracy", 0.0)
        print(f'count ----> {state["count"]}')
        if accuracy == 0.0:
            return "regenerate_mode"
        elif state["count"] >= 5:
            return "exit_mode"
        elif accuracy >= 90.0:
            return "exit_mode"
        else:
            return "improve_mode"

    @staticmethod
    def generate_test_case(state):
        code = state.get("response", "")
        test_case = StateManager.request_to_gemini(
            f"Give me corresponding function of unit tests for the given code. Which I add in testcase suite nothing else not any command section. Test class name will be 'RunnerTestCases'.Code:\n {code}"
        )
        return {"test_case": test_case, "success": True}

    @staticmethod
    def execute_code(state):
        test_case = state.get("test_case", "")
        generate_code = state.get("response", "")
        execution_result, accuracy = utils.execute_codes(generate_code, test_case)
        count = state["count"] + 1

        print("--------------------DEBUGGING-------------------")
        print(f"Result ---> {execution_result}, Accuracy ---> {accuracy}")
        print("--------------------DEBUGGING-------------------")

        if accuracy > state.get("best_accuracy", 0.0):
            return {
                "execution_result": str(execution_result),
                "accuracy": accuracy,
                "count": count,
                "failure": str(execution_result.failures),
                "error": str(execution_result.errors),
                "best_code": generate_code,
                "best_accuracy": accuracy,
                "best_code_execution_result": str(execution_result),
            }
        else:
            return {
                "execution_result": str(execution_result),
                "accuracy": accuracy,
                "count": count,
                "failure": str(execution_result.failures),
                "error": str(execution_result.errors),
                "best_code": state.get("best_code", ""),
                "best_accuracy": state.get("best_accuracy", 0.0),
                "best_code_execution_result": state.get("best_code_execution_result", ""),
            }

    @staticmethod
    def improve_code(state):
        code = state.get("response", "").strip()
        test_result = state.get("execution_result", "")
        test_cases = state.get("test_case", "")
        response = StateManager.request_to_gemini(
            f"Improve the code for increase accuracy.And give me only function code nothing else. \nCode :\n{code}.\n Testcase result: {test_result},\n Testcases: {test_cases}. \nFailures:\n{state.get('failure')},\nErrors:\n{state.get('error')}"
        )
        return {"response": response, "success": True}

    @staticmethod
    def request_to_gemini(prompt):
        response = model.generate_content(prompt).text
        return response
