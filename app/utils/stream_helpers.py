"""
Stream URL helper utilities for parsing, validation, and token expiration handling
"""

import re
import time
from typing import Optional, Dict, Tuple, Any
from urllib.parse import parse_qs, urlparse, urlencode
import logging

logger = logging.getLogger(__name__)


class StreamTokenExpiration:
    """Handles stream token expiration checking and validation"""

    @staticmethod
    def extract_expiry_timestamp(url: str) -> Optional[int]:
        """
        Extract expiry timestamp from stream URL
        
        Stream URLs typically have format:
        - https://example.com/stream?sign=xxx&t=1234567890
        
        Args:
            url: Full stream URL with potential expiration token
            
        Returns:
            Expiry timestamp (unix epoch) or None if not found
        """
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # Look for common expiration parameter names
            for param_name in ['t', 'expire', 'expiry', 'expires_at', 'expires']:
                if param_name in params:
                    expiry_str = params[param_name][0]
                    try:
                        return int(expiry_str)
                    except (ValueError, IndexError):
                        logger.warning(f"Could not parse expiry timestamp from {param_name}={expiry_str}")
                        continue
            
            return None
        except Exception as e:
            logger.error(f"Error extracting expiry timestamp from URL: {e}")
            return None

    @staticmethod
    def is_expired(url: str, buffer_seconds: int = 300) -> bool:
        """
        Check if stream URL token has expired
        
        Args:
            url: Full stream URL with potential expiration token
            buffer_seconds: Buffer time in seconds before actual expiration to consider invalid
                          Default 5 minutes
                          
        Returns:
            True if expired or about to expire, False otherwise
        """
        expiry = StreamTokenExpiration.extract_expiry_timestamp(url)
        
        if expiry is None:
            # No expiry found, assume it's valid
            logger.warning(f"No expiry timestamp found in URL, assuming valid")
            return False
        
        current_time = int(time.time())
        is_expired = current_time >= (expiry - buffer_seconds)
        
        if is_expired:
            logger.info(f"Stream URL expired: current_time={current_time}, expiry={expiry}, buffer={buffer_seconds}s")
        
        return is_expired

    @staticmethod
    def get_remaining_validity_seconds(url: str) -> Optional[int]:
        """
        Get remaining validity time for stream URL
        
        Args:
            url: Full stream URL with potential expiration token
            
        Returns:
            Remaining seconds until expiration, or None if no expiry found
        """
        expiry = StreamTokenExpiration.extract_expiry_timestamp(url)
        
        if expiry is None:
            return None
        
        current_time = int(time.time())
        remaining = expiry - current_time
        
        return max(0, remaining)  # Don't return negative values


class URLNormalizer:
    """Normalizes and parses page URLs to extract slug and subject_id"""

    @staticmethod
    def normalize_full_url(page_url: str) -> Dict[str, Any]:
        """
        Normalize various URL formats and extract slug and subject_id
        
        Accepts:
        - Full URL: https://moviebox.ph/detail/slug-name?id=123
        - Relative with query: /detail/slug-name?id=123
        - Relative: detail/slug-name?id=123
        - Just ID: 123
        
        Args:
            page_url: Page URL in any accepted format
            
        Returns:
            Dict with keys:
            - normalized_url: The normalized relative URL
            - slug: Extracted slug from URL
            - subject_id: Subject ID from query parameter
            - valid: Boolean indicating if URL is valid
            - error: Error message if invalid
            
        Example:
            >>> URLNormalizer.normalize_full_url("https://moviebox.ph/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440")
            {
                "normalized_url": "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440",
                "slug": "boyfriend-on-demand-hindi-OXFhFpXHnc6",
                "subject_id": "5203417860348986440",
                "valid": True,
                "error": None
            }
        """
        if not page_url or not isinstance(page_url, str):
            return {
                "normalized_url": None,
                "slug": None,
                "subject_id": None,
                "valid": False,
                "error": "page_url is required and must be a string"
            }
        
        try:
            raw = page_url.strip()
            
            # Parse URL components
            parsed = urlparse(raw)
            
            # Extract slug and subject_id
            slug = None
            subject_id = None
            normalized_url = None
            
            if parsed.scheme and parsed.netloc:
                # Full URL provided
                path = parsed.path
                query = parsed.query
                
                # Extract slug from path (e.g., /detail/slug-name)
                path_match = re.match(r"/detail/([^/?]+)", path)
                if path_match:
                    slug = path_match.group(1)
                
                # Extract subject_id from query
                if query:
                    query_params = parse_qs(query)
                    if 'id' in query_params:
                        subject_id = query_params['id'][0]
                
                # Rebuild normalized URL
                if slug:
                    normalized_url = f"/detail/{slug}"
                    if subject_id:
                        normalized_url += f"?id={subject_id}"
            else:
                # Relative URL or ID only
                if raw.startswith("/"):
                    raw = raw[1:]
                
                if raw.isdigit():
                    # Just an ID
                    subject_id = raw
                    normalized_url = f"/detail/{subject_id}?id={subject_id}"
                    slug = subject_id
                else:
                    # Relative URL with potential query
                    if "?" in raw:
                        path_part, query_part = raw.split("?", 1)
                    else:
                        path_part = raw
                        query_part = ""
                    
                    # Extract slug from path
                    path_match = re.match(r"detail/([^/?]+)", path_part)
                    if path_match:
                        slug = path_match.group(1)
                    else:
                        # Invalid path format
                        return {
                            "normalized_url": None,
                            "slug": None,
                            "subject_id": None,
                            "valid": False,
                            "error": f"Could not extract slug from URL path: {path_part}"
                        }
                    
                    # Extract subject_id from query
                    if query_part:
                        query_params = parse_qs(query_part)
                        if 'id' in query_params:
                            subject_id = query_params['id'][0]
                    
                    # Rebuild normalized URL
                    normalized_url = f"/detail/{slug}"
                    if subject_id:
                        normalized_url += f"?id={subject_id}"
            
            if not slug:
                return {
                    "normalized_url": None,
                    "slug": None,
                    "subject_id": None,
                    "valid": False,
                    "error": "Could not extract slug from page_url"
                }
            
            return {
                "normalized_url": normalized_url,
                "slug": slug,
                "subject_id": subject_id,
                "valid": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error normalizing URL {page_url}: {e}")
            return {
                "normalized_url": None,
                "slug": None,
                "subject_id": None,
                "valid": False,
                "error": f"Error parsing URL: {str(e)}"
            }

    @staticmethod
    def build_streaming_source_url(slug: str) -> str:
        """
        Build correct streaming source URL for 123movienow.cc API
        
        Args:
            slug: Content slug from normalized URL
            
        Returns:
            Constructed streaming source URL
            
        Example:
            >>> URLNormalizer.build_streaming_source_url("boyfriend-on-demand-hindi-OXFhFpXHnc6")
            "https://123movienow.cc/spa/videoPlayPage/movies/boyfriend-on-demand-hindi-OXFhFpXHnc6"
        """
        return f"https://123movienow.cc/spa/videoPlayPage/movies/{slug}"


class EpisodeParser:
    """Parses and maps episode identifiers"""

    @staticmethod
    def parse_episode_id(episode_id: str) -> Optional[Dict[str, int]]:
        """
        Parse episode ID to extract season and episode numbers
        
        Args:
            episode_id: Episode ID in format s{season}e{episode} (e.g., s1e2)
            
        Returns:
            Dict with 'season' and 'episode' keys, or None if invalid format
            
        Example:
            >>> EpisodeParser.parse_episode_id("s1e2")
            {"season": 1, "episode": 2}
        """
        pattern = r"s(\d+)e(\d+)"
        match = re.match(pattern, episode_id.lower())
        
        if match:
            return {
                "season": int(match.group(1)),
                "episode": int(match.group(2))
            }
        
        logger.warning(f"Invalid episode_id format: {episode_id}")
        return None

    @staticmethod
    def format_episode_id(season: int, episode: int) -> str:
        """
        Format season and episode numbers into standard episode ID
        
        Args:
            season: Season number
            episode: Episode number
            
        Returns:
            Formatted episode ID (e.g., s1e2)
        """
        return f"s{season}e{episode}"

    @staticmethod
    def create_episode_map(seasons_data: list) -> Dict[str, Dict[str, Any]]:
        """
        Create mapping from episode_id to episode metadata
        
        Args:
            seasons_data: List of season dicts with structure:
                {
                    "season_number": 1,
                    "episode_count": 10,
                    "episodes": [
                        {"id": "s1e1", "title": "...", ...},
                        ...
                    ]
                }
        
        Returns:
            Dict mapping episode_id to episode metadata
            
        Example:
            >>> seasons = [{"season_number": 1, "episodes": [{"id": "s1e1", "title": "Pilot"}]}]
            >>> EpisodeParser.create_episode_map(seasons)
            {
                "s1e1": {"title": "Pilot", ...}
            }
        """
        episode_map = {}
        
        for season in seasons_data:
            if 'episodes' in season:
                for episode in season['episodes']:
                    if 'id' in episode:
                        episode_map[episode['id']] = episode
        
        return episode_map
