from django.shortcuts import render
import requests
import random
from user_agents import parse
from django.http import JsonResponse

def index(request):
    #--------------- GLOBAL VARIABLE -----------
    ismoviesearched = "no"
    searchedmovieurl = ""
    videourl = []
    API_KEY = "1feb329b"
    #-------------------------------------------

    search_text = request.GET.get('searchtext', '')  # Get search text if available, otherwise default to empty string
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
                ismoviesearched = "no"  # Set to "no" to use the videourl loop in the template
                # Get the number of seasons from OMDb data
                total_seasons = int(data.get("totalSeasons", 1))  # Default to 1 if not available

                # Fetch episode counts for each season dynamically
                episodes_per_season = {}
                for season in range(1, total_seasons + 1):
                    season_url = f"http://www.omdbapi.com/?i={imdbid}&Season={season}&apikey={API_KEY}"
                    season_response = requests.get(season_url)
                    season_data = season_response.json()
                    if season_data.get("Response") == "True":
                        episodes = len(season_data.get("Episodes", []))
                        episodes_per_season[season] = episodes
                    else:
                        episodes_per_season[season] = 10  # Fallback to 10 episodes if API call fails

                # Collect all possible episode URLs
                base_url = "https://vidsrc.xyz/embed/tv"
                all_episodes = []
                for season, num_episodes in episodes_per_season.items():
                    for episode in range(1, num_episodes + 1):
                        video_url = f"{base_url}?imdb={imdbid}&season={season}&episode={episode}"
                        all_episodes.append(video_url)

                # Select 10 random episodes (or fewer if there aren't enough episodes)
                videourl = random.sample(all_episodes, min(10, len(all_episodes)))

    # If no search, proceed with default or selected series
    if not search_text:
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
            "friends":"tt0108778",
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

        # Default selected series
        default_series = [
            "family-guy",
            "american-dad",
            "south-park",
        ]
        selected_series = request.GET.getlist('series') or default_series

        # Create a list to hold all video URLs for selected series
        for series in selected_series:
            imdb_id = series_ids.get(series)
            if imdb_id:  # Ensure the series exists in series_ids
                # Fetch total seasons for the series
                series_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={API_KEY}"
                series_response = requests.get(series_url)
                series_data = series_response.json()
                total_seasons = int(series_data.get("totalSeasons", 1)) if series_data.get("Response") == "True" else 1

                # Fetch episode counts for each season
                episodes_per_season = {}
                for season in range(1, total_seasons + 1):
                    season_url = f"http://www.omdbapi.com/?i={imdb_id}&Season={season}&apikey={API_KEY}"
                    season_response = requests.get(season_url)
                    season_data = season_response.json()
                    if season_data.get("Response") == "True":
                        episodes = len(season_data.get("Episodes", []))
                        episodes_per_season[season] = episodes
                    else:
                        episodes_per_season[season] = 10  # Fallback to 10 episodes if API call fails

                # Collect all episode URLs for the series
                for season, num_episodes in episodes_per_season.items():
                    for episode in range(1, num_episodes + 1):
                        video_url = f"{base_url}?imdb={imdb_id}&season={season}&episode={episode}"
                        videourl.append(video_url)

        # Shuffle and select up to 12 random video URLs
        videourl = random.sample(videourl, min(12, len(videourl)))

    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'videos': videourl})

    # Determine if iPhone to adjust sandbox attribute
    user_agent = parse(request.META['HTTP_USER_AGENT'])
    is_iphone = 'iPhone' in request.META['HTTP_USER_AGENT']
    sandbox_attr = "allow-same-origin allow-scripts" if is_iphone else None

    context = {
        'videourl': videourl,  # Send the video URLs to the template
        'sandbox_attr': sandbox_attr,
        'ismoviesearched': ismoviesearched,
        'searchedmovieurl': searchedmovieurl
    }
    return render(request, 'index.html', context)

def watchvideo(request, videourl, sandbox_attr):
    context = {
        'videourl': videourl,  # Send the single video URL to the template
        'sandbox_attr': sandbox_attr if sandbox_attr != "Empty" else "",
    }
    return render(request, 'watchvideo.html', context)