from django.shortcuts import render, redirect
import requests
import random
from user_agents import parse
from django.http import JsonResponse
from .models import Comment, count_user  # Import Comment model
from django.views.decorators.csrf import csrf_exempt

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def termspage(request):
    context = {}
    return render(request, 'terms.html', context)

@csrf_exempt
def post_comment(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            print(data)
            text = data.get('text')
            parent_id = data.get('parent_id')
            if not text or len(text) > 500:
                return JsonResponse({'status': 'error', 'message': 'Comment text is required and must be 500 characters or less.'})
            
            parent = Comment.objects.get(id=parent_id) if parent_id else None
            
            comment = Comment.objects.create(
                text=text,
                parent=parent
            )
            
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def index(request):
    ip = get_client_ip(request)
    try:
        country = g.country(ip)['country_name']
    except:
        country = "Unknown"

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    device = parse(user_agent)
    device_type = 'Mobile' if device.is_mobile else 'Tablet' if device.is_tablet else 'Desktop'

    session_key = request.session.session_key or request.session.save() or request.session.session_key

    if not count_user.objects.filter(session_key=session_key).exists():
        count_user.objects.create(ip=ip, country=country, device=device_type, session_key=session_key)

    ismoviesearched = "no"
    searchedmovieurl = ""
    videourl = []
    API_KEY = "1feb329b"

    search_text = request.GET.get('searchtext', '')
    if search_text:
        url = f"http://www.omdbapi.com/?t={search_text}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get("Response") == "True":
            imdbid = data.get("imdbID", "")
            type_ = data.get("Type", "").lower()
            if type_ == "movie":
                ismoviesearched = "yes"
                searchedmovieurl = f"https://vidsrc.xyz/embed/movie/{imdbid}"
            elif type_ == "series":
                ismoviesearched = "no"
                total_seasons = int(data.get("totalSeasons", 1))
                episodes_per_season = {}
                for season in range(1, total_seasons + 1):
                    season_url = f"http://www.omdbapi.com/?i={imdbid}&Season={season}&apikey={API_KEY}"
                    season_response = requests.get(season_url)
                    season_data = season_response.json()
                    if season_data.get("Response") == "True":
                        episodes = len(season_data.get("Episodes", []))
                        episodes_per_season[season] = episodes
                    else:
                        episodes_per_season[season] = 10
                base_url = "https://vidsrc.xyz/embed/tv"
                all_episodes = []
                for season, num_episodes in episodes_per_season.items():
                    for episode in range(1, num_episodes + 1):
                        video_url = f"{base_url}?imdb={imdbid}&season={season}&episode={episode}"
                        all_episodes.append(video_url)
                videourl = random.sample(all_episodes, min(10, len(all_episodes)))

    if not search_text:
        base_url = "https://vidsrc.xyz/embed/tv"
        series_ids = {
            "south-park": "tt0121955",
            "american-dad": "tt0397306",
            "family-guy": "tt0182576",
            "rick-and-morty": "tt2861424",
            "bojack-horseman": "tt3398228",
            "the-simpsons": "tt0096697",
            "futurama": "tt0149460",
            "bobs-burgers": "tt1561755",
            "friends": "tt0108778",
            "the-office": "tt0386676",
            "how-i-met-your-mother": "tt0460649",
            "mr-bean": "tt0096657",
            "big-bang-theory": "tt0898266",
            "dexters-laboratory": "tt0115157",
            "johnny-bravo": "tt0118360",
            "cow-and-chicken": "tt0118289",
            "ed-edd-n-eddy": "tt0131636",
            "courage-the-cowardly-dog": "tt0220880",
            "grim-adventures-billy-mandy": "tt0292800",
            "codename-kids-next-door": "tt0312109",
            "spongebob-squarepants": "tt0206512",
            "tom-and-jerry": "tt0780438",
        }
        default_series = ["family-guy", "american-dad", "south-park"]
        selected_series = request.GET.getlist('series') or default_series
        for series in selected_series:
            imdb_id = series_ids.get(series)
            if imdb_id:
                series_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={API_KEY}"
                series_response = requests.get(series_url)
                series_data = series_response.json()
                total_seasons = int(series_data.get("totalSeasons", 1)) if series_data.get("Response") == "True" else 1
                episodes_per_season = {}
                for season in range(1, total_seasons + 1):
                    season_url = f"http://www.omdbapi.com/?i={imdb_id}&Season={season}&apikey={API_KEY}"
                    season_response = requests.get(season_url)
                    season_data = season_response.json()
                    if season_data.get("Response") == "True":
                        episodes = len(season_data.get("Episodes", []))
                        episodes_per_season[season] = episodes
                    else:
                        episodes_per_season[season] = 10
                for season, num_episodes in episodes_per_season.items():
                    for episode in range(1, num_episodes + 1):
                        video_url = f"{base_url}?imdb={imdb_id}&season={season}&episode={episode}"
                        videourl.append(video_url)
        videourl = random.sample(videourl, min(12, len(videourl)))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'videos': videourl})

    user_agent = parse(request.META['HTTP_USER_AGENT'])
    is_iphone = 'iPhone' in request.META['HTTP_USER_AGENT']
    sandbox_attr = "allow-same-origin allow-scripts" if is_iphone else None

    # Fetch comments for display
    comments = Comment.objects.filter(parent__isnull=True).prefetch_related('replies')

    context = {
        'videourl': videourl,
        'sandbox_attr': sandbox_attr,
        'ismoviesearched': ismoviesearched,
        'searchedmovieurl': searchedmovieurl,
        'comments': comments  # Add comments to context
    }
    return render(request, 'index.html', context)

def watchvideo(request, videourl, sandbox_attr):
    # Fetch comments for watchvideo page if needed
    comments = Comment.objects.filter(parent__isnull=True).prefetch_related('replies')
    
    context = {
        'videourl': videourl,
        'sandbox_attr': sandbox_attr if sandbox_attr != "Empty" else "",
        'comments': comments  # Add comments to context
    }
    return render(request, 'watchvideo.html', context)