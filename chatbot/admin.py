from django.contrib import admin
from .models import Destination, Hotel, Restaurant, Attraction, ChatHistory, UserProfile

# Register your models here.

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'average_cost', 'rating', 'created_at')
    list_filter = ('country', 'rating', 'created_at')
    search_fields = ('name', 'city', 'country')
    ordering = ('-rating', '-created_at')
    date_hierarchy = 'created_at'

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'star_rating', 'price_per_night', 'rating', 'created_at')
    list_filter = ('star_rating', 'destination__country', 'created_at')
    search_fields = ('name', 'destination__name', 'destination__city')
    ordering = ('-rating', '-created_at')
    date_hierarchy = 'created_at'

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'cuisine_type', 'price_range', 'rating', 'created_at')
    list_filter = ('cuisine_type', 'price_range', 'destination__country', 'created_at')
    search_fields = ('name', 'cuisine_type', 'destination__name')
    ordering = ('-rating', '-created_at')
    date_hierarchy = 'created_at'

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'category', 'entry_fee', 'rating', 'created_at')
    list_filter = ('category', 'destination__country', 'created_at')
    search_fields = ('name', 'destination__name', 'category')
    ordering = ('-rating', '-created_at')
    date_hierarchy = 'created_at'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_language', 'created_at')
    list_filter = ('preferred_language', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'timestamp', 'response_time')
    list_filter = ('timestamp', 'user')
    search_fields = ('user_message', 'session_id', 'user__username')
    readonly_fields = ('timestamp', 'response_time')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
