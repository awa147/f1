from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class EventCategory(models.Model):
    """活动分类"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # 用于前端图标
    
    class Meta:
        verbose_name = "活动分类"
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name

class CampusEvent(models.Model):
    """校园活动主表"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('canceled', '已取消'),
    ]
    
    title = models.CharField("活动标题", max_length=200)
    description = models.TextField("活动详情")
    category = models.ForeignKey(
        EventCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="分类"
    )
    location = models.CharField("地点", max_length=200)
    start_time = models.DateTimeField("开始时间")
    end_time = models.DateTimeField("结束时间")
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name="组织者"
    )
    capacity = models.PositiveIntegerField("最大人数", default=100)
    cover_image = models.ImageField(
        "封面图",
        upload_to='event_covers/',
        blank=True,
        null=True
    )
    status = models.CharField(
        "状态",
        max_length=20,
        choices=STATUS_CHOICES,
        default='published'
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    is_featured = models.BooleanField("推荐活动", default=False)
    
    class Meta:
        verbose_name = "校园活动"
        verbose_name_plural = verbose_name
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['status']),
        ]
        
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        """活动是否正在进行"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

class EventRegistration(models.Model):
    """活动报名表"""
    event = models.ForeignKey(
        CampusEvent,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name="活动"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        verbose_name="用户"
    )
    registration_time = models.DateTimeField("报名时间", auto_now_add=True)
    attended = models.BooleanField("已参加", default=False)
    feedback = models.TextField("反馈意见", blank=True)
    rating = models.PositiveSmallIntegerField(
        "评分",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "活动报名"
        verbose_name_plural = verbose_name
        unique_together = ('event', 'user')
        ordering = ['-registration_time']
        
    def __str__(self):
        return f"{self.user.username} 报名 {self.event.title}"

class BookmarkedEvent(models.Model):
    """活动收藏表"""
    event = models.ForeignKey(
        CampusEvent,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name="活动"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_bookmarks',
        verbose_name="用户"
    )
    created_at = models.DateTimeField("收藏时间", auto_now_add=True)
    
    class Meta:
        verbose_name = "收藏活动"
        verbose_name_plural = verbose_name
        unique_together = ('event', 'user')
        
    def __str__(self):
        return f"{self.user.username} 收藏 {self.event.title}"