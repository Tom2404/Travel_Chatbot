from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
import json
import os
import uuid
import time
# from openai import OpenAI
from dotenv import load_dotenv
from .models import ChatHistory, Destination, Hotel, Restaurant, Attraction

# 🔑 Tải biến môi trường từ file .env
load_dotenv()

# ✅ Khởi tạo OpenAI client với API Key (commented for now)
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 10  # Max requests per minute
RATE_LIMIT_WINDOW = 60   # Window in seconds

def rate_limit_check(request):
    """Simple rate limiting"""
    user_ip = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f"rate_limit_{user_ip}"
    
    current_requests = cache.get(cache_key, 0)
    if current_requests >= RATE_LIMIT_REQUESTS:
        return False
    
    cache.set(cache_key, current_requests + 1, RATE_LIMIT_WINDOW)
    return True

def validate_message(message):
    """Validate user input"""
    if not message or not isinstance(message, str):
        return False, "Tin nhắn không hợp lệ"
    
    message = message.strip()
    if len(message) < 1:
        return False, "Tin nhắn không được để trống"
    
    if len(message) > 1000:
        return False, "Tin nhắn quá dài (tối đa 1000 ký tự)"
    
    # Basic security check
    forbidden_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
    message_lower = message.lower()
    for pattern in forbidden_patterns:
        if pattern in message_lower:
            return False, "Tin nhắn chứa nội dung không được phép"
    
    return True, message

def index(request):
    """Trang chính của chatbot"""
    return render(request, "chatbot/index.html")

def test_view(request):
    """Test view để debug"""
    return HttpResponse("<h1>🎯 TEST VIEW WORKING!</h1>")

def get_travel_context():
    """Lấy thông tin du lịch từ database để bổ sung context cho AI"""
    # Use caching to improve performance
    cache_key = "travel_context"
    context = cache.get(cache_key)
    
    if context is None:
        context_parts = []

        # Lấy top destinations với optimization
        destinations = Destination.objects.select_related().filter(
            rating__gte=4.0
        ).order_by('-rating')[:10]
        
        if destinations:
            dest_info = "Điểm đến phổ biến: " + ", ".join(
                [f"{d.name} ({d.city}, {d.country})" for d in destinations]
            )
            context_parts.append(dest_info)

        # Lấy top hotels
        hotels = Hotel.objects.select_related('destination').filter(
            rating__gte=4.0
        ).order_by('-rating')[:5]
        
        if hotels:
            hotel_info = "Khách sạn đề xuất: " + ", ".join(
                [f"{h.name} ({h.destination.city})" for h in hotels]
            )
            context_parts.append(hotel_info)

        context = " | ".join(context_parts)
        # Cache for 1 hour
        cache.set(cache_key, context, 3600)

    return context

@require_http_methods(["POST"])
def chat(request):
    """Chat endpoint với bảo mật và validation tốt hơn"""
    try:
        # Rate limiting check
        if not rate_limit_check(request):
            return JsonResponse({
                "reply": "Quá nhiều yêu cầu. Vui lòng thử lại sau 1 phút.",
                "error": "rate_limit_exceeded"
            }, status=429)

        # Parse and validate JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "reply": "Dữ liệu không hợp lệ.",
                "error": "invalid_json"
            }, status=400)

        user_message = data.get("message", "")

        # Validate message
        is_valid, validated_message = validate_message(user_message)
        if not is_valid:
            return JsonResponse({
                "reply": validated_message,
                "error": "validation_failed"
            }, status=400)

        user_message = validated_message

        # Tạo session ID nếu chưa có
        session_id = request.session.get("chat_session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["chat_session_id"] = session_id

        # Record start time for response measurement
        start_time = time.time()

        # Lấy context từ database
        travel_context = get_travel_context()

        # Prompt cho chatbot
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
- Xuống dòng đúng cách, đúng chỗ

THÔNG TIN BỔ SUNG: {travel_context}

Câu hỏi: {user_message}

Hãy trả lời một cách chi tiết, hữu ích và thân thiện:"""

        prompt = base_prompt.format(
            travel_context=travel_context if travel_context else "Chưa có dữ liệu cụ thể",
            user_message=user_message,
        )

        # ✅ Gọi GPT-4o với timeout và error handling (temporarily disabled)
        try:
            # For now, return a simple response
            reply = f"Xin chào! Tôi đã nhận được câu hỏi: '{user_message}'. Hiện tại hệ thống AI đang được thiết lập. Vui lòng thử lại sau khi OpenAI API được cấu hình đầy đủ."
            
            # Original OpenAI code (commented):
            # response = client.chat.completions.create(
            #     model="gpt-4o",
            #     messages=[{"role": "user", "content": prompt}],
            #     max_tokens=800,
            #     temperature=0.7,
            #     timeout=30  # 30 second timeout
            # )
            # reply = response.choices[0].message.content
        except Exception as openai_error:
            print(f"OpenAI API Error: {str(openai_error)}")
            reply = "Xin lỗi, hệ thống AI tạm thời không khả dụng. Vui lòng thử lại sau."

        # Calculate response time
        response_time = time.time() - start_time

        # Lưu vào lịch sử chat
        try:
            ChatHistory.objects.create(
                session_id=session_id,
                user_message=user_message,
                bot_response=reply,
                response_time=response_time,
                user=request.user if request.user.is_authenticated else None,
            )
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            # Continue even if saving fails

        return JsonResponse({
            "reply": reply,
            "response_time": round(response_time, 2)
        })

    except Exception as e:
        error_msg = "Xin lỗi, có lỗi xảy ra với hệ thống. Vui lòng thử lại sau."
        print(f"Error in chat view: {str(e)}")

        # Vẫn lưu lỗi vào lịch sử chat để dễ tra
        try:
            session_id = request.session.get("chat_session_id", str(uuid.uuid4()))
            ChatHistory.objects.create(
                session_id=session_id,
                user_message=user_message if 'user_message' in locals() else "Unknown",
                bot_response=f"ERROR: {str(e)}",
                user=request.user if request.user.is_authenticated else None,
            )
        except:
            pass

        return JsonResponse({
            "reply": error_msg,
            "error": "internal_server_error"
        }, status=500)

def chat_history(request):
    """API để lấy lịch sử chat với pagination"""
    session_id = request.session.get("chat_session_id")
    if not session_id:
        return JsonResponse({"history": [], "total": 0})

    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))
    
    history_queryset = ChatHistory.objects.filter(
        session_id=session_id
    ).order_by("timestamp")
    
    paginator = Paginator(history_queryset, per_page)
    history_page = paginator.get_page(page)
    
    history_data = [
        {
            "user_message": chat.user_message,
            "bot_response": chat.bot_response,
            "timestamp": chat.timestamp.strftime("%H:%M"),
            "response_time": chat.response_time,
        }
        for chat in history_page
    ]

    return JsonResponse({
        "history": history_data,
        "total": paginator.count,
        "page": page,
        "has_next": history_page.has_next(),
        "has_previous": history_page.has_previous()
    })

@require_http_methods(["POST"])
def clear_chat(request):
    """Clear chat history for current session"""
    session_id = request.session.get("chat_session_id")
    if session_id:
        ChatHistory.objects.filter(session_id=session_id).delete()
        return JsonResponse({"success": True, "message": "Đã xóa lịch sử chat"})
    return JsonResponse({"success": False, "message": "Không có phiên chat"})

def search_destinations(request):
    """Search destinations API"""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({"results": []})
    
    destinations = Destination.objects.filter(
        Q(name__icontains=query) |
        Q(city__icontains=query) |
        Q(country__icontains=query) |
        Q(description__icontains=query)
    ).select_related().order_by('-rating')[:10]
    
    results = [
        {
            "id": dest.id,
            "name": dest.name,
            "city": dest.city,
            "country": dest.country,
            "description": dest.description[:200] + "..." if len(dest.description) > 200 else dest.description,
            "rating": dest.rating,
            "average_cost": float(dest.average_cost),
            "best_time": dest.best_time_to_visit
        }
        for dest in destinations
    ]
    
    return JsonResponse({"results": results, "count": len(results)})

def search_hotels(request):
    """Search hotels API"""
    query = request.GET.get('q', '').strip()
    destination_id = request.GET.get('destination_id')
    
    hotels_queryset = Hotel.objects.select_related('destination')
    
    if query:
        hotels_queryset = hotels_queryset.filter(
            Q(name__icontains=query) |
            Q(destination__name__icontains=query) |
            Q(destination__city__icontains=query)
        )
    
    if destination_id:
        hotels_queryset = hotels_queryset.filter(destination_id=destination_id)
    
    hotels = hotels_queryset.order_by('-rating')[:10]
    
    results = [
        {
            "id": hotel.id,
            "name": hotel.name,
            "destination": f"{hotel.destination.city}, {hotel.destination.country}",
            "star_rating": hotel.star_rating,
            "price_per_night": float(hotel.price_per_night),
            "rating": hotel.rating,
            "amenities": hotel.amenities.split(',') if hotel.amenities else []
        }
        for hotel in hotels
    ]
    
    return JsonResponse({"results": results, "count": len(results)})
