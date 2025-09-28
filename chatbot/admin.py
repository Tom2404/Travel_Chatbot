from django.contrib import admin
from .models import Destination, Hotel, Restaurant, Attraction, ChatHistory

# Register your models here.

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'average_cost', 'rating')
    list_filter = ('country', 'rating')
    search_fields = ('name', 'city', 'country')
    ordering = ('-rating',)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'star_rating', 'price_per_night', 'rating')
    list_filter = ('star_rating', 'destination__country')
    search_fields = ('name', 'destination__name', 'destination__city')
    ordering = ('-rating',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'cuisine_type', 'price_range', 'rating')
    list_filter = ('cuisine_type', 'price_range', 'destination__country')
    search_fields = ('name', 'cuisine_type', 'destination__name')
    ordering = ('-rating',)

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'category', 'entry_fee', 'rating')
    list_filter = ('category', 'destination__country')
    search_fields = ('name', 'destination__name', 'category')
    ordering = ('-rating',)

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user_message', 'session_id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
