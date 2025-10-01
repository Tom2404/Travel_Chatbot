from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError

# Create your models here.

class Destination(models.Model):
    """Model cho các điểm đến du lịch"""
    name = models.CharField(
        max_length=200, 
        verbose_name="Tên điểm đến",
        validators=[MinLengthValidator(2)]
    )
    country = models.CharField(
        max_length=100, 
        verbose_name="Quốc gia",
        validators=[MinLengthValidator(2)]
    )
    city = models.CharField(
        max_length=100, 
        verbose_name="Thành phố",
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(
        verbose_name="Mô tả",
        validators=[MinLengthValidator(10)]
    )
    best_time_to_visit = models.CharField(
        max_length=200, 
        verbose_name="Thời điểm tốt nhất"
    )
    average_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Chi phí trung bình/ngày (USD)",
        validators=[MinValueValidator(0.01)]
    )
    rating = models.FloatField(
        default=0, 
        verbose_name="Đánh giá",
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Điểm đến"
        verbose_name_plural = "Điểm đến"
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['country', 'city']),
        ]
    
    def clean(self):
        """Custom validation"""
        if self.rating < 0 or self.rating > 5:
            raise ValidationError("Rating phải từ 0 đến 5")
        if self.average_cost <= 0:
            raise ValidationError("Chi phí phải lớn hơn 0")
    
    def __str__(self):
        return f"{self.name}, {self.city}, {self.country}"

class Hotel(models.Model):
    """Model cho khách sạn"""
    name = models.CharField(
        max_length=200, 
        verbose_name="Tên khách sạn",
        validators=[MinLengthValidator(2)]
    )
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='hotels'
    )
    address = models.TextField(
        verbose_name="Địa chỉ",
        validators=[MinLengthValidator(5)]
    )
    star_rating = models.IntegerField(
        choices=[(i, f"{i} sao") for i in range(1, 6)], 
        verbose_name="Hạng sao",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    price_per_night = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Giá/đêm (USD)",
        validators=[MinValueValidator(0.01)]
    )
    amenities = models.TextField(
        verbose_name="Tiện nghi", 
        help_text="Các tiện nghi cách nhau bởi dấu phẩy"
    )
    rating = models.FloatField(
        default=0, 
        verbose_name="Đánh giá",
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Khách sạn"
        verbose_name_plural = "Khách sạn"
        indexes = [
            models.Index(fields=['destination', 'star_rating']),
            models.Index(fields=['rating']),
        ]
    
    def clean(self):
        """Custom validation"""
        if self.price_per_night <= 0:
            raise ValidationError("Giá phải lớn hơn 0")
        if self.rating < 0 or self.rating > 5:
            raise ValidationError("Rating phải từ 0 đến 5")
    
    def __str__(self):
        return f"{self.name} - {self.destination.city}"

class Restaurant(models.Model):
    """Model cho nhà hàng"""
    name = models.CharField(
        max_length=200, 
        verbose_name="Tên nhà hàng",
        validators=[MinLengthValidator(2)]
    )
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='restaurants'
    )
    cuisine_type = models.CharField(
        max_length=100, 
        verbose_name="Loại ẩm thực",
        validators=[MinLengthValidator(2)]
    )
    price_range = models.CharField(max_length=20, choices=[
        ('$', 'Bình dân'),
        ('$$', 'Trung bình'),
        ('$$$', 'Cao cấp'),
        ('$$$$', 'Sang trọng')
    ], verbose_name="Mức giá")
    specialty = models.TextField(
        verbose_name="Món đặc trưng",
        validators=[MinLengthValidator(5)]
    )
    rating = models.FloatField(
        default=0, 
        verbose_name="Đánh giá",
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Nhà hàng"
        verbose_name_plural = "Nhà hàng"
        indexes = [
            models.Index(fields=['destination', 'cuisine_type']),
            models.Index(fields=['rating']),
        ]
    
    def clean(self):
        """Custom validation"""
        if self.rating < 0 or self.rating > 5:
            raise ValidationError("Rating phải từ 0 đến 5")
    
    def __str__(self):
        return f"{self.name} - {self.cuisine_type}"

class Attraction(models.Model):
    """Model cho điểm tham quan"""
    name = models.CharField(
        max_length=200, 
        verbose_name="Tên điểm tham quan",
        validators=[MinLengthValidator(2)]
    )
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='attractions'
    )
    category = models.CharField(max_length=100, verbose_name="Loại hình", choices=[
        ('historical', 'Lịch sử'),
        ('natural', 'Thiên nhiên'),
        ('cultural', 'Văn hóa'),
        ('adventure', 'Phiêu lưu'),
        ('entertainment', 'Giải trí')
    ])
    description = models.TextField(
        verbose_name="Mô tả",
        validators=[MinLengthValidator(10)]
    )
    entry_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Giá vé (USD)",
        validators=[MinValueValidator(0)]
    )
    opening_hours = models.CharField(
        max_length=200, 
        verbose_name="Giờ mở cửa"
    )
    rating = models.FloatField(
        default=0, 
        verbose_name="Đánh giá",
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Điểm tham quan"
        verbose_name_plural = "Điểm tham quan"
        indexes = [
            models.Index(fields=['destination', 'category']),
            models.Index(fields=['rating']),
        ]
    
    def clean(self):
        """Custom validation"""
        if self.rating < 0 or self.rating > 5:
            raise ValidationError("Rating phải từ 0 đến 5")
        if self.entry_fee < 0:
            raise ValidationError("Giá vé không thể âm")
    
    def __str__(self):
        return f"{self.name} - {self.destination.city}"

class UserProfile(models.Model):
    """Mở rộng thông tin user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_language = models.CharField(
        max_length=10, 
        choices=[('vi', 'Tiếng Việt'), ('en', 'English')],
        default='vi'
    )
    travel_preferences = models.TextField(
        blank=True, 
        verbose_name="Sở thích du lịch"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"
    
    def __str__(self):
        return f"Profile của {self.user.username}"

class ChatHistory(models.Model):
    """Model lưu lịch sử chat"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(
        max_length=100, 
        verbose_name="ID phiên",
        db_index=True
    )
    user_message = models.TextField(
        verbose_name="Tin nhắn người dùng",
        validators=[MinLengthValidator(1)]
    )
    bot_response = models.TextField(verbose_name="Phản hồi bot")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")
    response_time = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Thời gian phản hồi (giây)"
    )
    
    class Meta:
        verbose_name = "Lịch sử chat"
        verbose_name_plural = "Lịch sử chat"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session_id', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
