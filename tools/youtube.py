from importlib import metadata
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from googleapiclient.discovery import build

from utils.cleaner import create_standard_document
from utils.schemas import DocumentClass
from dotenv import load_dotenv

load_dotenv()
UTUBE_API_KEY = os.getenv("UTUBE_API_KEY")

client=build('youtube','v3',developerKey=UTUBE_API_KEY)

def search_videos(query: str,max_count:int) -> List[Dict[str,str]]:
    """Searches YouTube for videos matching the query and returns a list of video metadata."""
    try:
        request=client.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_count,
            relevanceLanguage='en'
        )
        response=request.execute()
        videos_data=[]
        for item in response.get('items', []):
            videos_data.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
            })
        return videos_data
    except Exception as e:
        print(f"Error during Youtube search: {e}")
        return []
    
def get_video_comments(video_id: str, video_title: str) -> List[DocumentClass]:
    """
    Fetches the first page (max 100) of Top-Level Comments ONLY.
    Guarantees returning a list, even on error (Fixes TypeError).
    """
    if not client: return []
    allDocuments: List[DocumentClass] = []
    
    try:
        # Request for the first page of comments
        request = client.commentThreads().list(
            part='snippet', # Replies part is not requested
            videoId=video_id,
            maxResults=100, 
            textFormat='plainText'
        )
        response = request.execute()
        
        for item in response.get('items',[]):
            # --- Process Top-Level Comment (TLC) ---
            tlc = item['snippet']['topLevelComment']
            tlc_snippet = tlc['snippet']
            
            comment_metadata={
                'like_count': tlc_snippet.get('likeCount',0),
                'published_at': tlc_snippet.get('publishedAt',''),
                'video_title': video_title,
                'is_reply': False,
                'author_name': tlc_snippet.get('authorDisplayName')
            }
            
            # Use the clean/standardize function
            doc = create_standard_document(
                raw_text=tlc_snippet['textDisplay'],
                source_name="youtube",
                metadata=comment_metadata
            )
            allDocuments.append(doc)

    except Exception as e:
        print(f"General error during comment fetching for video {video_id}: {e}") 
    return allDocuments