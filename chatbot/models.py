from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Destination(models.Model):
    """Model cho các điểm đến du lịch"""
    name = models.CharField(max_length=200, verbose_name="Tên điểm đến")
    country = models.CharField(max_length=100, verbose_name="Quốc gia")
    city = models.CharField(max_length=100, verbose_name="Thành phố")
    description = models.TextField(verbose_name="Mô tả")
    best_time_to_visit = models.CharField(max_length=200, verbose_name="Thời điểm tốt nhất")
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Chi phí trung bình/ngày (USD)")
    rating = models.FloatField(default=0, verbose_name="Đánh giá")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Điểm đến"
        verbose_name_plural = "Điểm đến"
    
    def __str__(self):
        return f"{self.name}, {self.city}, {self.country}"

class Hotel(models.Model):
    """Model cho khách sạn"""
    name = models.CharField(max_length=200, verbose_name="Tên khách sạn")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    address = models.TextField(verbose_name="Địa chỉ")
    star_rating = models.IntegerField(choices=[(i, f"{i} sao") for i in range(1, 6)], verbose_name="Hạng sao")
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Giá/đêm (USD)")
    amenities = models.TextField(verbose_name="Tiện nghi", help_text="Các tiện nghi cách nhau bởi dấu phẩy")
    rating = models.FloatField(default=0, verbose_name="Đánh giá")
    
    class Meta:
        verbose_name = "Khách sạn"
        verbose_name_plural = "Khách sạn"
    
    def __str__(self):
        return f"{self.name} - {self.destination.city}"

class Restaurant(models.Model):
    """Model cho nhà hàng"""
    name = models.CharField(max_length=200, verbose_name="Tên nhà hàng")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='restaurants')
    cuisine_type = models.CharField(max_length=100, verbose_name="Loại ẩm thực")
    price_range = models.CharField(max_length=20, choices=[
        ('$', 'Bình dân'),
        ('$$', 'Trung bình'),
        ('$$$', 'Cao cấp'),
        ('$$$$', 'Sang trọng')
    ], verbose_name="Mức giá")
    specialty = models.TextField(verbose_name="Món đặc trưng")
    rating = models.FloatField(default=0, verbose_name="Đánh giá")
    
    class Meta:
        verbose_name = "Nhà hàng"
        verbose_name_plural = "Nhà hàng"
    
    def __str__(self):
        return f"{self.name} - {self.cuisine_type}"

class Attraction(models.Model):
    """Model cho điểm tham quan"""
    name = models.CharField(max_length=200, verbose_name="Tên điểm tham quan")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='attractions')
    category = models.CharField(max_length=100, verbose_name="Loại hình", choices=[
        ('historical', 'Lịch sử'),
        ('natural', 'Thiên nhiên'),
        ('cultural', 'Văn hóa'),
        ('adventure', 'Phiêu lưu'),
        ('entertainment', 'Giải trí')
    ])
    description = models.TextField(verbose_name="Mô tả")
    entry_fee = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Giá vé (USD)")
    opening_hours = models.CharField(max_length=200, verbose_name="Giờ mở cửa")
    rating = models.FloatField(default=0, verbose_name="Đánh giá")
    
    class Meta:
        verbose_name = "Điểm tham quan"
        verbose_name_plural = "Điểm tham quan"
    
    def __str__(self):
        return f"{self.name} - {self.destination.city}"

class ChatHistory(models.Model):
    """Model lưu lịch sử chat"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, verbose_name="ID phiên")
    user_message = models.TextField(verbose_name="Tin nhắn người dùng")
    bot_response = models.TextField(verbose_name="Phản hồi bot")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")
    
    class Meta:
        verbose_name = "Lịch sử chat"
        verbose_name_plural = "Lịch sử chat"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
