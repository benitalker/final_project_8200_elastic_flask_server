from typing import Dict, Any, Optional, List
import folium
from toolz import curry

@curry
def create_popup_content(result: Dict[str, Any]) -> str:
    return f"""
    <b>{result.get('title', 'Untitled')}</b><br>
    Date: {result.get('publication_date', 'Unknown')}<br>
    Category: {result.get('category', 'Uncategorized')}<br>
    Location: {result.get('location', 'Unknown')}
    """

@curry
def is_valid_coordinates(coords: Dict[str, float]) -> bool:
    return (
        isinstance(coords, dict) and
        all(k in coords for k in ('lat', 'lon')) and
        -90 <= coords['lat'] <= 90 and
        -180 <= coords['lon'] <= 180
    )

@curry
def create_marker(
    folium_map: folium.Map,
    result: Dict[str, Any]
) -> Optional[folium.Marker]:
    coords = result.get('coordinates')
    if coords and is_valid_coordinates(coords):
        return folium.Marker(
            location=[coords['lat'], coords['lon']],
            popup=create_popup_content(result),
            icon=folium.Icon(color='red')
        ).add_to(folium_map)
    return None

def create_map_from_results(results: List[Dict[str, Any]]) -> str:
    m = folium.Map(location=[0, 0], zoom_start=2)
    list(map(create_marker(m), results))
    return m._repr_html_()