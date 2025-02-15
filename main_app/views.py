from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import random
from django.http import JsonResponse


from django.shortcuts import render
import random

from django.shortcuts import render
import random
from user_agents import parse

def index(request):
    # Define the base URL and IMDb IDs for all shows
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
        "big-bang-theory": "tt0898266"
    }

    # Define the number of episodes for each season for each series
    season_episodes = {
        "south-park": {season: 14 for season in range(1, 26)},
        "american-dad": {season: 18 for season in range(1, 20)},
        "family-guy": {season: 21 for season in range(1, 22)},
        "rick-and-morty": {1: 11, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10},
        "bojack-horseman": {1: 12, 2: 12, 3: 12, 4: 12, 5: 12, 6: 16},
        "the-simpsons": {season: 22 for season in range(1, 35)},
        "futurama": {1: 13, 2: 19, 3: 16, 4: 18, 5: 16, 6: 26, 7: 10},
        "bobs-burgers": {season: 20 for season in range(1, 14)},
        "friends": {season: 24 for season in range(1, 11)},
        "the-office": {season: 24 for season in range(1, 10)},
        "how-i-met-your-mother": {season: 22 for season in range(1, 10)},
        "mr-bean": {1: 14, 2: 13},
        "big-bang-theory": {season: 24 for season in range(1, 13)},
    }

    # Default selected series
    # Default selected series
    default_series = [
        "family-guy",
        "american-dad",
        "south-park",
    ]
    selected_series = request.GET.getlist('series') or default_series

    # Create a list to hold all video URLs for selected series
    videourl = []

    for series in selected_series:
        imdb_id = series_ids[series]
        for season, num_episodes in season_episodes[series].items():
            for episode in range(1, num_episodes + 1):
                video_url = f"{base_url}?imdb={imdb_id}&season={season}&episode={episode}"
                videourl.append(video_url)

    # Shuffle and select random video URLs
    selected_videos = random.sample(videourl, min(12, len(videourl)))

    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'videos': selected_videos})
    
    user_agent = parse(request.META['HTTP_USER_AGENT'])
    is_iphone = 'iPhone' in request.META['HTTP_USER_AGENT']  # Check if 'iPhone' is in the user agent string
    sandbox_attr = "allow-same-origin allow-scripts" if is_iphone else "Empty"
    context = {
        'videourl': selected_videos,  # Send the 12 random URLs to the template,
        'sandbox_attr': sandbox_attr,
    }
    return render(request, 'index.html', context)

def watchvideo(request, videourl, sandbox_attr):
    context = {
       'videourl': videourl,  # Send the 12 random URLs to the template,
        'sandbox_attr': sandbox_attr if sandbox_attr != "Empty" else "",
    }
    return render(request, 'watchvideo.html', context)
