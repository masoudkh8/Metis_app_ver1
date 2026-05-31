import logging
import requests
from typing import Optional, Any, Callable

logger = logging.getLogger(__name__)

def get_data_with_fallback(
    url: str, 
    fallback_query_func: Optional[Callable] = None, 
    timeout: int = 5,
    **request_kwargs
) -> Any:
    """
    Attempts to fetch data from a URL. If it fails (network error), 
    it falls back to a local database query or default data.
    
    Args:
        url: The external API URL.
        fallback_query_func: A function that returns local data if network fails.
        timeout: Request timeout in seconds.
        **request_kwargs: Additional arguments for requests.get (e.g., headers).
    
    Returns:
        The data from the URL or the fallback data.
    """
    try:
        logger.info(f"Attempting to fetch data from: {url}")
        response = requests.get(url, timeout=timeout, **request_kwargs)
        response.raise_for_status()  # Raise error for bad status codes (4xx, 5xx)
        logger.info("Successfully fetched external data.")
        return response.json()  # Or response.text depending on your needs
    
    except (requests.exceptions.ConnectionError, 
            requests.exceptions.Timeout, 
            requests.exceptions.RequestException) as e:
        
        logger.warning(f"Network error occurred: {e}. Switching to fallback mode.")
        
        if fallback_query_func:
            try:
                local_data = fallback_query_func()
                logger.info("Successfully loaded fallback data from local source.")
                return local_data
            except Exception as db_error:
                logger.error(f"Fallback mechanism also failed: {db_error}")
                return []  # Return empty list or default safe structure
        
        logger.warning("No fallback function provided. Returning empty dataset.")
        return []
