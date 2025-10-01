from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import UserProfile
import json

def register_view(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tạo UserProfile cho user mới
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Tài khoản {username} đã được tạo thành công!')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'chatbot/register.html', {'form': form})

def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin!')
            return render(request, 'chatbot/login.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Chào mừng {username}!')
            return redirect('index')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
    
    return render(request, 'chatbot/login.html')

def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('index')

@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """User profile management"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update profile
        preferred_language = request.POST.get('preferred_language', 'vi')
        travel_preferences = request.POST.get('travel_preferences', '')
        
        profile.preferred_language = preferred_language
        profile.travel_preferences = travel_preferences
        profile.save()
        
        messages.success(request, 'Hồ sơ đã được cập nhật!')
        return redirect('profile')
    
    context = {
        'profile': profile,
        'user': request.user
    }
    return render(request, 'chatbot/profile.html', context)

@login_required
def user_chat_history(request):
    """Get chat history for logged in user"""
    from .models import ChatHistory
    
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 50))
    
    # Get all chat history for this user
    from django.core.paginator import Paginator
    
    history_queryset = ChatHistory.objects.filter(
        user=request.user
    ).order_by('-timestamp')
    
    paginator = Paginator(history_queryset, per_page)
    history_page = paginator.get_page(page)
    
    history_data = [
        {
            "session_id": chat.session_id,
            "user_message": chat.user_message,
            "bot_response": chat.bot_response,
            "timestamp": chat.timestamp.strftime("%d/%m/%Y %H:%M"),
            "response_time": chat.response_time,
        }
        for chat in history_page
    ]

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            "history": history_data,
            "total": paginator.count,
            "page": page,
            "has_next": history_page.has_next(),
            "has_previous": history_page.has_previous()
        })
    
    context = {
        'history': history_page,
        'paginator': paginator
    }
    return render(request, 'chatbot/user_history.html', context)