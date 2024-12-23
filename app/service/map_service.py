import folium
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_map_from_results(results: List[Dict[str, Any]]) -> str:
    """
    Create a Folium map from search results.

    Args:
        results (List[Dict[str, Any]]): List of search results

    Returns:
        str: HTML representation of the map
    """
    m = folium.Map(location=[0, 0], zoom_start=2)
    logger.info(f"Creating map with {len(results)} results")

    # Filter out results without coordinates
    valid_results = [
        result for result in results
        if result.get('coordinates')
           and isinstance(result['coordinates'], dict)
           and 'lat' in result['coordinates']
           and 'lon' in result['coordinates']
    ]

    logger.info(f"Found {len(valid_results)} results with valid coordinates")

    for result in valid_results:
        try:
            coords = result['coordinates']
            lat = coords['lat']
            lon = coords['lon']

            # Validate coordinate values
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                logger.warning(f"Invalid coordinates for result: {result}")
                continue

            folium.Marker(
                location=[lat, lon],
                popup=f"""
                <b>{result.get('title', 'Untitled')}</b><br>
                Date: {result.get('publication_date', 'Unknown')}<br>
                Category: {result.get('category', 'Uncategorized')}<br>
                Location: {result.get('location', 'Unknown')}
                """,
                icon=folium.Icon(color='red')
            ).add_to(m)
        except Exception as e:
            logger.error(f"Error processing result: {result}. Error: {e}")

    return m._repr_html_()