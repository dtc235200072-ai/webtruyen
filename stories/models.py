from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Story(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True) # Để blank=True để tự động tạo
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)
    author = models.CharField(max_length=100, blank=True, default="Đang cập nhật")
    views = models.PositiveIntegerField(default=0)  # tổng view truyện

    followers = models.ManyToManyField(
        User,
        related_name="followed_stories",
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="chapters"
    )
    number = models.PositiveIntegerField("Số chương")
    title = models.CharField("Tiêu đề", max_length=255)
    content = models.TextField("Nội dung")

    class Meta:
        ordering = ["number"]
        unique_together = ("story", "number")

    def __str__(self):
        return f"Chương {self.number}: {self.title}"

class Audio(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="audios"
    )
    voice = models.CharField(max_length=50)
    file = models.FileField(upload_to='audio/', blank=True, null=True)

    def __str__(self):
        return f"{self.chapter.id} - {self.voice}"
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="ratings")
    score = models.IntegerField()  # 1 -> 5

    class Meta:
        unique_together = ('user', 'story')

    def __str__(self):
        return f"{self.user} - {self.story} ({self.score})"
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="comments")

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.story}"
    
class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)

    last_read = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'story')