from tools.youtube import search_videos, get_video_comments
from typing import List, Dict, Any

def youtube_tool(topic: str, max_videos: int = 5) -> List[Dict[str, Any]]:
    """Tool to search YouTube videos by topic and fetch their comments."""
    videos = search_videos(topic, max_videos)
    all_comments = []
    try:
        for video in videos:
            video_id = video['id']
            video_title = video['title']
            comments = get_video_comments(video_id, video_title)
            all_comments.extend(comments)
        return all_comments
    except Exception as e:
        print(f"Error in youtube_tool: {e}")
        return []