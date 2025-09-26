from django.shortcuts import render
from django.http import JsonResponse
import json
import openai
# Create your views here.

openai.api_key = "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"
def home(request):
    return render(request, "chatbot/home.html")

def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            
            prompt = f"Bạn là chatbot du lịch. Người dùng hỏi: {user_message}. Hãy gợi ý các thông tin về địa điểm, món ăn, khách sạn, giá cả và các thông tin liên quan."
            
            response = openai.ChatCompletion.create(
                model = "gpt-4o",
                messages = [{role: "user", content: prompt}],
            )
            
            reply = response.choices[0].message["content"]
            return JsonResponse({"reply": reply})
        except Exception as e:
            return JsonResponse({"reply": f"Lỗi: {str(e)}"})
    else:   
        return JsonResponse({"reply": "Phương thức không hợp lệ."})