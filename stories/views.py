from django.shortcuts import render, get_object_or_404
from .models import Story, Chapter, Audio, Category, Comment
from django.http import JsonResponse
from .models import Rating
import requests
from django.http import JsonResponse
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Value, Max, Prefetch
from django.db.models.functions import Coalesce
from .models import ReadingHistory
def story_list(request):
    now = timezone.now()
    stories = Story.objects.annotate(
        total_views=Coalesce(Sum('chapters__views'), Value(0)),
        latest_chap=Max('chapters__created_at')
    ).prefetch_related(
        Prefetch(
            'chapters',
            queryset=Chapter.objects.order_by('-created_at'),
            to_attr='latest_chaps'   # 🔥 cái này mới là thứ HTML cần
        )
    ).order_by('-total_views')
    categories = Category.objects.all()

    # 🔥 TOP NGÀY
    top_day = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=1)
    ).annotate(
        total_views=Sum('chapters__views')
    ).order_by('-total_views')[:10]

    # 🔥 TOP TUẦN
    top_week = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=7)
    ).annotate(
        total_views=Sum('chapters__views')
    ).order_by('-total_views')[:10]

    # 🔥 TOP THÁNG
    top_month = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=30)
    ).annotate(
        total_views=Sum('chapters__views')
    ).order_by('-total_views')[:10]

    # 🔥 TRUYỆN MỚI (QUAN TRỌNG)
    new_updates = Story.objects.annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    return render(request, 'stories/story_list.html', {
        'stories': stories,
        'all_categories': categories,
        'top_day': top_day,
        'top_week': top_week,
        'top_month': top_month,
        'new_updates': new_updates,
    })

from django.db.models import Avg

def story_detail(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    chapters = story.chapters.all()
    now = timezone.now()  

    # 🔥 TOP TRUYỆN (sau này sẽ nâng cấp)
    top_day = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=1)
    ).annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_week = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=7)
    ).annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_month = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=30)
    ).annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    # ✅ TÍNH VIEW THẬT (tổng từ chapter)
    total_views = sum(ch.views for ch in chapters)
    story.views = total_views
    if story.views != total_views:
        story.views = total_views
        story.save()

    # ✅ RATING
    avg_rating = story.ratings.aggregate(avg=Avg('score'))['avg'] or 0

    # ✅ CHECK FOLLOW
    is_following = False
    if request.user.is_authenticated:
        is_following = story.followers.filter(id=request.user.id).exists()
    # ✅ COMMENT
    comments = story.comments.all().order_by('-created_at')

    return render(request, 'stories/story_detail.html', {
        'story': story,
        'chapters': chapters,
        'avg_rating': round(avg_rating, 1),
        'is_following': is_following,
        'comments': comments,
        'top_day': top_day,
        'top_week': top_week,
        'top_month': top_month,
    })
from django.shortcuts import render, get_object_or_404
from gtts import gTTS
from django.core.files import File
import os


def chapter_detail(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    chapter.views += 1
    chapter.save()
    if request.user.is_authenticated:
        ReadingHistory.objects.update_or_create(
            user=request.user,
            story=chapter.story,
            defaults={
                'chapter': chapter
            }
        )

    # audio (có hoặc không)
    audio = Audio.objects.filter(chapter=chapter).first()

    # chap trước
    prev_chapter = Chapter.objects.filter(
        story=chapter.story,
        number__lt=chapter.number
    ).order_by('-id').first()

    # chap sau
    next_chapter = Chapter.objects.filter(
        story=chapter.story,
        number__gt=chapter.number
    ).order_by('id').first()
    suggested_stories = Story.objects.exclude(
        id=chapter.story.id
    ).order_by('-views')[:6]

    return render(request, 'stories/chapter_detail.html', {
        'chapter': chapter,
        'story': chapter.story,
        'audio_url': audio.file.url if audio else None,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'suggested_stories': suggested_stories,
    })
from django.db.models import Q

def search_stories(request):
    query = request.GET.get('q')

    results = Story.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    ) if query else []

    return render(request, 'stories/search_results.html', {
        'stories': results,
        'search_query': query,
        'all_categories': Category.objects.all()
    })
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

# View Đăng ký
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Đăng ký thành công!")
            return redirect("login")
        else:
            messages.error(request, "Đăng ký thất bại!")

    else:
        form = UserCreationForm()

    return render(request, "stories/register.html", {"form": form})

# View Đăng nhập
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("story_list")
    else:
        form = AuthenticationForm()

    return render(request, "stories/login.html", {"form": form})


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Bạn đã đăng xuất thành công!")
    return redirect("story_list")
from django.http import JsonResponse

def search_ajax(request):
    query = request.GET.get('q', '')
    data = []

    if query:
        stories = Story.objects.filter(title__icontains=query)[:5]
        for story in stories:
            data.append({
                'id': story.id,
                'title': story.title,
            })

    return JsonResponse(data, safe=False)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def add_comment(request, story_id):
    if request.method == "POST":
        content = request.POST.get('content')

        if content:
            Comment.objects.create(
                user=request.user,
                story_id=story_id,
                content=content
            )

    return redirect('story_detail', story_id=story_id)

@login_required
def rate_story(request, story_id):
    if request.method == "POST":
        score = int(request.POST.get('score'))

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            story_id=story_id,
            defaults={'score': score}
        )

        avg = Rating.objects.filter(story_id=story_id).aggregate(avg=Avg('score'))['avg']

        return JsonResponse({
            'success': True,
            'avg': round(avg, 1)
        })
    
from .models import Chapter, Audio
from django.core.files.base import ContentFile
import urllib.request
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def tts_fpt(request):
    if request.method == "POST":
        data = json.loads(request.body)

        chapter_id = data.get("chapter_id")
        voice = data.get("voice", "banmai")

        chapter = Chapter.objects.get(id=chapter_id)

        # 🔥 1. CHECK ĐÃ CÓ AUDIO CHƯA
        audio = Audio.objects.filter(
            chapter=chapter,
            voice=voice
        ).first()

        if audio and audio.file:
            return JsonResponse({
                "cached": True,
                "url": audio.file.url
            })

        # 🔥 2. CHƯA CÓ → GỌI API
        text = chapter.content[:2000]

        url = "https://api.fpt.ai/hmi/tts/v5"

        headers = {
            "api-key": "dpZN67ihsxQt0xQC8RVf1QD9N73IP3TA",
            "voice": voice,
            "format": "mp3"
        }

        response = requests.post(
            url,
            data=text.encode('utf-8'),
            headers=headers
        )

        result = response.json()
        audio_url = result.get("async")

        if not audio_url:
            return JsonResponse({"error": "TTS failed"})

        # 🔥 3. TẢI FILE VỀ
        file_data = urllib.request.urlopen(audio_url).read()

        file_name = f"chapter_{chapter.id}_{voice}.mp3"

        # 🔥 4. LƯU DB
        audio = Audio.objects.create(
            chapter=chapter,
            voice=voice
        )

        audio.file.save(file_name, ContentFile(file_data))

        return JsonResponse({
            "cached": False,
            "url": audio.file.url
        })
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

@login_required
def follow_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    if request.user in story.followers.all():
        story.followers.remove(request.user)
    else:
        story.followers.add(request.user)

    return redirect('story_detail', story_id=story.id)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.db.models import Max

@login_required
def followed_stories(request):
    stories = request.user.followed_stories.all()
    now = timezone.now()

    # DAY
    top_day_ids = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=1)
    ).values('id').distinct().annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_day_map = {s.id: s for s in Story.objects.filter(
        id__in=[x['id'] for x in top_day_ids]
    )}

    top_day = [top_day_map[x['id']] for x in top_day_ids]

    # WEEK
    top_week_ids = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=7)
    ).values('id').distinct().annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_week_map = {s.id: s for s in Story.objects.filter(
        id__in=[x['id'] for x in top_week_ids]
    )}

    top_week = [top_week_map[x['id']] for x in top_week_ids]

    # MONTH
    top_month_ids = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=30)
    ).values('id').distinct().annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_month_map = {s.id: s for s in Story.objects.filter(
        id__in=[x['id'] for x in top_month_ids]
    )}

    top_month = [top_month_map[x['id']] for x in top_month_ids]

    return render(request, 'stories/followed.html', {
        'stories': stories,
        'top_day': top_day,
        'top_week': top_week,
        'top_month': top_month,
    })

def reading_history(request):

    histories = []
    now = timezone.now()

    if request.user.is_authenticated:
        histories = ReadingHistory.objects.filter(
            user=request.user
        ).select_related('story', 'chapter').order_by('-last_read')

    # 🔥 TOP DAY
    top_day_ids = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=1)
    ).values('id').distinct().annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_day_map = {s.id: s for s in Story.objects.filter(
        id__in=[x['id'] for x in top_day_ids]
    )}
    top_day = [top_day_map[x['id']] for x in top_day_ids]

    # 🔥 TOP WEEK
    top_week_ids = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=7)
    ).values('id').distinct().annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_week_map = {s.id: s for s in Story.objects.filter(
        id__in=[x['id'] for x in top_week_ids]
    )}
    top_week = [top_week_map[x['id']] for x in top_week_ids]

    # 🔥 TOP MONTH
    top_month_ids = Story.objects.filter(
        chapters__created_at__gte=now - timedelta(days=30)
    ).values('id').distinct().annotate(
        latest_chap=Max('chapters__created_at')
    ).order_by('-latest_chap')[:10]

    top_month_map = {s.id: s for s in Story.objects.filter(
        id__in=[x['id'] for x in top_month_ids]
    )}
    top_month = [top_month_map[x['id']] for x in top_month_ids]

    return render(request, 'stories/history.html', {
        'histories': histories,
        'top_day': top_day,
        'top_week': top_week,
        'top_month': top_month,
    })
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.db.models import Value

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)

    stories = Story.objects.filter(categories=category).annotate(
        total_views_sum=Coalesce(Sum('chapters__views'), Value(0)),
        chapter_count=Count('chapters')
    ).prefetch_related('chapters')

    top_stories = Story.objects.annotate(
        total_views_sum=Coalesce(Sum('chapters__views'), Value(0))
    ).order_by('-total_views_sum')[:10]

    return render(request, 'stories/category.html', {
        'category': category,
        'stories': stories,
        'top_stories': top_stories,
    })