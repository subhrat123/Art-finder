import re
import emoji
from datetime import datetime
from typing import Dict, Any

from .schemas import DocumentClass 

def clean_comment(text: str) -> str:
    """Performs comprehensive cleaning on raw, unstructured comment text."""
    if not text:
        return ""
    
    # 1. HTML Tag and URL Removal
    text = re.sub(r'<[^>]+>|http\S+|www\S+|\S+\.\S+', '', text, flags=re.MULTILINE)
    
    # 2. Emoji Removal
    text = emoji.replace_emoji(text, replace='')
    
    # 3. Punctuation/Symbol Removal and Normalization
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    
    # 4. Whitespace Cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_standard_document(
    raw_text: str, 
    source_name: str, 
    metadata: Dict[str, Any]
) -> DocumentClass:
    """
    Applies cleaning, determines initial tags, and returns a StandardDocument instance.
    """
    cleaned_text = clean_comment(raw_text)

    # 1. Determine Initial Relevance Tag (Cost-Effective Filter)
    if 'great video' in cleaned_text or 'subscribe' in cleaned_text or 'thanks' in cleaned_text:
        relevance_tag = 'irrelevant_chatter'
    else:
        relevance_tag = 'product_focused'

    # 2. Determine Engagement Score (FIX: Ensure string conversion) 
    # Get score, fallback to 0, then convert to string as required by Pydantic
    engagement_score_int = metadata.get('like_count', metadata.get('upvotes', 0))
    engagement_score = str(engagement_score_int)
    
    # 3. Determine Time Stamp (FIX: Ensure fallback is always an ISO string)
    try:
        time_stamp_raw = metadata.get('published_at', None)
        
        if isinstance(time_stamp_raw, datetime):
            # If it's already a datetime object, convert it to ISO string
            time_stamp = time_stamp_raw.isoformat()
        elif time_stamp_raw:
            # If it's a non-empty string, use it
            time_stamp = str(time_stamp_raw)
        else:
            # Fallback to current time as an ISO string
            time_stamp = datetime.now().isoformat()
            
    except Exception:
        time_stamp = datetime.now().isoformat() 
    
    return DocumentClass(
        page_content=cleaned_text,
        text=raw_text, 
        source=source_name,
        time_stamp=time_stamp,
        engagement_score=engagement_score,
        relevance_tag=relevance_tag,
        extra_metadata=metadata
    )