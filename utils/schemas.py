from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class DocumentClass(BaseModel):
    """A standarside schema for all indexed content, regardless of source."""
    page_content: str=Field(description="the cleaned content for embeddings.")
    text: str=Field(description="the original text from sources")
    source: str=Field(description="EG: 'Youtube' | 'reddit' | 'google search'")
    time_stamp: str=Field(description=" The creation date/time, mandatory for trend analysis.")
    engagement_score: int=Field(default=0,description="Numerical value used for weighting (e.g., likes/upvotes)")
    relevance_tag: str=Field(default="neutral",description="Initial tag(e.g., product_focused, irrelevant)")
    source_url: Optional[str]=None
    author_id: Optional[str]=None
    extra_metadata: Dict[str,Any]= Field(default_factory=dict,description="for storing video titles, subreddits, etc.")