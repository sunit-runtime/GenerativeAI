import google.generativeai as genai
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PromptForm
from .models import Prompt, TestResult, ResetPasswordRequest
from .utils import run_tests
from generativeaiproject import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from cryptography.fernet import Fernet
import datetime as dt
import ast

cipher_suite = Fernet(settings.key)

def submit_prompt(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        user = request.user
        form = PromptForm(request.POST)
        if form.is_valid():
            prompt = form.save(commit=False)
            prompt.user = user
            prompt.save()

            generate_code(prompt)

            return redirect("prompt_results", prompt_id=prompt.id)
    else:
        form = PromptForm()
    return render(request, "submit_prompt.html", {"form": form})


def generate_code(prompt):
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        code = model.generate_content(
            prompt.prompt_text + " give me only function code nothing else."
        ).text

        test_cases = model.generate_content(
            f"Give me corresponding function of unit tests for the given code. Give me only list of test case which we add in testcase suite nothing else not any command section.Test class name will be 'RunnerTestCases'. where code is {code}"
        ).text

    except Exception as e:
        print(f"Error generating code: {e}")
        return

    code = code.replace("```python", "").replace("```", "")
    test_cases = test_cases.replace("```python", "").replace("```", "")

    test_results, coverage_percent, code = run_tests(code, test_cases)

    TestResult.objects.create(
        prompt=prompt,
        test_output=str(test_results),
        coverage=coverage_percent,
        passed_tests=test_results.testsRun - len(test_results.failures),
        failed_tests=len(test_results.failures),
        code=code,
        test_cases=test_cases,
    )


def prompt_results(request, prompt_id):
    prompt = get_object_or_404(Prompt, id=prompt_id)
    results = TestResult.objects.filter(prompt=prompt).order_by("-created_at")
    return render(
        request, "prompt_results.html", {"prompt": prompt, "results": results}
    )


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("submit_prompt")
        else:
            return render(
                request,
                "Login.html",
                {"error": "Invalid credentials please try again."},
            )
    return render(request, "Login.html")


def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "Register.html",
                {"error": "Email already exists, please try again."},
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=firstname,
            last_name=lastname,
            email=email,
        )
        user.is_staff = True
        login(request, user)
        return redirect("submit_prompt")
    return render(request, "Register.html")


def user_logout(request):
    logout(request)
    return redirect("login")


def custom_page_not_found_view(request, exception):
    return render(request, "exception.html", {"exceptionType": "Not Found"}, status=404)


def custom_error_view(request):
    return render(
        request, "exception.html", {"exceptionType": "Server Error"}, status=500
    )


def custom_permission_denied_view(request, exception):
    return render(
        request, "exception.html", {"exceptionType": "Access Denied"}, status=403
    )


def custom_bad_request_view(request, exception):
    return render(
        request, "exception.html", {"exceptionType": "Bad Request"}, status=400
    )


@api_view(["POST"])
def send_email(request):
    email = request.POST.get("user_email")
    if not User.objects.filter(email=email).exists():
        return Response({"message": "Email not found", "status": "failed"}, status=400)
    encryptCode = password_reset_request(email)
    link = f"{settings.BASE_URL}/change-password/{encryptCode}"
    subject = "Reset Password Request"
    user = User.objects.get(email=email)
    message = f"""Hi {user.first_name},\n\nYour Password Reset Link.
    \nLink : {link}
    \n\nThanks,\nGenerative AI Team"""
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
    return Response(
        {"message": "Email sent successfully", "status": "success"}, status=200
    )


def password_reset_request(email):
    user = User.objects.get(email=email)
    data = str([user.pk, email, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")])
    encrypted_data = encrypt_data(data)

    if ResetPasswordRequest.objects.filter(userEmail=email).exists():
        new_request = ResetPasswordRequest.objects.get(userEmail=email)
        new_request.encryptCode = encrypted_data
        new_request.user = user
        new_request.verified = False
    else:
        new_request = ResetPasswordRequest(
            userEmail=email, encryptCode=encrypted_data, user=user, verified=False
        )
    new_request.save()

    return encrypted_data


def new_password(request, token):
    requestData = ResetPasswordRequest.objects.get(encryptCode=token)
    decrypt_info = ast.literal_eval(decrypt_data(bytes(token, "utf-8")))
    if requestData.verified:
        return render(
            request,
            "changePassword.html",
            {"error": "Invalid Link, Please try again.", "access": False},
        )
    if request.method == "POST":
        password = request.POST.get("password")
        confirmPassword = request.POST.get("re-password")
        if password == confirmPassword:
            user = User.objects.get(pk=decrypt_info[0])
            user.set_password(password)
            user.save()
            requestData.verified = True
            requestData.save()
            return redirect("login")
        else:
            return render(
                request,
                "changePassword.html",
                {
                    "error": "Password and Confirm Password should be same",
                    "access": True,
                },
            )
    return render(request, "changePassword.html", {"access": True})


def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode("utf-8"))
    return str(encrypted_data)[2:-1]


def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode("utf-8")
