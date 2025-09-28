from django.shortcuts import render
from django.http import JsonResponse
import json
from openai import OpenAI
import os
import uuid
from .models import ChatHistory, Destination, Hotel, Restaurant, Attraction

# Khởi tạo OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def index(request):
    return render(request, "index.html")

def get_travel_context():
    """Lấy thông tin du lịch từ database để bổ sung context cho AI"""
    context = []
    
    # Lấy top destinations
    destinations = Destination.objects.filter(rating__gte=4.0)[:10]
    if destinations:
        dest_info = "Điểm đến phổ biến: " + ", ".join([f"{d.name} ({d.city}, {d.country})" for d in destinations])
        context.append(dest_info)
    
    return " | ".join(context)

def chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            
            if not user_message.strip():
                return JsonResponse({"reply": "Vui lòng nhập câu hỏi của bạn."})

            # Tạo session ID nếu chưa có
            session_id = request.session.get('chat_session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                request.session['chat_session_id'] = session_id

            # Lấy context từ database
            travel_context = get_travel_context()
            
            # Cải thiện prompt cho chatbot du lịch với context
            base_prompt = """Bạn là AI assistant chuyên về du lịch Việt Nam và quốc tế với kiến thức sâu rộng.
            
NHIỆM VỤ:
- Cung cấp thông tin chính xác, hữu ích về du lịch
- Gợi ý điểm đến, khách sạn, nhà hàng, hoạt động
- Tư vấn lịch trình, phương tiện, chi phí
- Chia sẻ kinh nghiệm thực tế

PHONG CÁCH:
- Thân thiện, nhiệt tình
- Trả lời chi tiết nhưng dễ hiểu
- Đưa ra gợi ý cụ thể, thực tế
- Sử dụng emoji phù hợp để sinh động

THÔNG TIN BỔ SUNG: {travel_context}

Câu hỏi: {user_message}

Hãy trả lời một cách chi tiết, hữu ích và thân thiện:"""

            prompt = base_prompt.format(
                travel_context=travel_context if travel_context else "Chưa có dữ liệu cụ thể",
                user_message=user_message
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )

            reply = response.choices[0].message.content
            
            # Lưu vào lịch sử chat
            ChatHistory.objects.create(
                session_id=session_id,
                user_message=user_message,
                bot_response=reply,
                user=request.user if request.user.is_authenticated else None
            )
            
            return JsonResponse({"reply": reply})

        except Exception as e:
            error_msg = "Xin lỗi, có lỗi xảy ra với hệ thống. Vui lòng thử lại sau."
            
            # Log error để debug (trong production nên dùng logging)
            print(f"Error in chat view: {str(e)}")
            
            # Vẫn lưu vào lịch sử chat để tracking
            try:
                session_id = request.session.get('chat_session_id', str(uuid.uuid4()))
                ChatHistory.objects.create(
                    session_id=session_id,
                    user_message=user_message,
                    bot_response=f"ERROR: {str(e)}",
                    user=request.user if request.user.is_authenticated else None
                )
            except:
                pass  # Ignore if can't save to history
            
            return JsonResponse({"reply": error_msg})
    else:
        return JsonResponse({"reply": "Phương thức không hợp lệ."})

def chat_history(request):
    """API để lấy lịch sử chat"""
    session_id = request.session.get('chat_session_id')
    if not session_id:
        return JsonResponse({"history": []})
    
    history = ChatHistory.objects.filter(session_id=session_id).order_by('timestamp')[:50]
    history_data = [{
        'user_message': chat.user_message,
        'bot_response': chat.bot_response,
        'timestamp': chat.timestamp.strftime('%H:%M')
    } for chat in history]
    
    return JsonResponse({"history": history_data})
