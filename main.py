from googleapiclient.discovery import build

# Replace with your actual API key
API_KEY = "AIzaSyArDHY2YMa0Sx0HIAxUKHTsFZY5ytBJi9U"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_youtube_videos(query, max_results=50):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )

    response = request.execute()
    
    videos = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = thumbnails.get("high", {}).get("url") or thumbnails.get("default", {}).get("url")

        video_data = {
            "videoId": item["id"]["videoId"],
            "title": snippet["title"],
            "channelTitle": snippet["channelTitle"],
            "publishTime": snippet["publishTime"],
            "description": snippet["description"],
            "thumbnail": thumbnail_url
        }
        videos.append(video_data)
    
    return videos

# Example usage
# query_text = "lofi music for study"
query_text = "High beat music for GYM"
results = search_youtube_videos(query_text)

for video in results:
    print(f"Title: {video['title']}")
    print(f"Video ID: {video['videoId']}")
    print(f"Channel: {video['channelTitle']}")
    print(f"Published on: {video['publishTime']}")
    print(f"Description: {video['description'][:100]}...")
    print(f"Thumbnail: {video['thumbnail']}")
    print(f"Link: https://www.youtube.com/watch?v={video['videoId']}")
    print("-" * 80)
