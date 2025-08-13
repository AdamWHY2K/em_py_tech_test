import re
from typing import Dict, Optional
from tyre import Seasonality, TyreType, Grade, SpeedRating


class TyreDataParser:
    """Handles parsing and conversion of tyre data."""
    
    @staticmethod
    def parse_seasonality(season_text: Optional[str]) -> Optional[Seasonality]:
        if not season_text:
            return None
        season_lower = season_text.lower()
        if season_lower.startswith('summer'):
            return Seasonality.SUMMER
        elif season_lower.startswith('winter'):
            return Seasonality.WINTER
        elif 'all' in season_lower:
            return Seasonality.ALL_SEASON
        return None
    
    @staticmethod
    def parse_tyre_type(type_text: Optional[str]) -> Optional[TyreType]:
        """Parse tyre type from text."""
        if not type_text:
            return None
        
        type_lower = type_text.lower()
        if type_lower in {'van'}:
            return TyreType.VAN
        elif type_lower in {'4x4', 'suv'}:
            return TyreType.FOUR_BY_FOUR
        return TyreType.CAR
    
    @staticmethod
    def parse_grade(grade_text: Optional[str]) -> Optional[Grade]:
        if not grade_text:
            return None
        
        match = re.search(r'\b([A-E])\b', grade_text.strip().upper())
        return Grade(match.group(1)) if match else None
    
    @staticmethod
    def parse_load_index_and_speed_rating(data: Dict, size: Optional[str]) -> tuple[int, Optional[SpeedRating]]:
        load_index = 0
        speed_rating = None
        
        # Try to get from explicit fields first
        if data.get('load_index') and str(data.get('load_index')).isdigit():
            load_index = int(data.get('load_index'))
        
        if data.get('speed_rating'):
            sr_text = data.get('speed_rating').strip().upper()
            if sr_text in SpeedRating.__members__:
                speed_rating = SpeedRating[sr_text]
        
        # Fallback to parsing from size string
        if (not load_index or not speed_rating) and size:
            match = re.search(r'\b(\d{2,3})([A-Z])\b', size)
            if match:
                if not load_index:
                    try:
                        load_index = int(match.group(1))
                    except ValueError:
                        load_index = 0
                if not speed_rating:
                    sr_text = match.group(2).strip().upper()
                    if sr_text in SpeedRating.__members__:
                        speed_rating = SpeedRating[sr_text]
        
        return load_index, speed_rating
    
    @staticmethod
    def parse_boolean_features(data: Dict) -> Dict[str, bool]:
        return {
            'electric': str(data.get('electric', '')).lower() == 'yes',
            'self_seal': str(data.get('selfseal', '')).lower() == 'yes',
            'run_flat': str(data.get('runflat', '')).lower() == 'yes',
            'noise_reduction': str(data.get('noisereduction', '')).lower() == 'yes',
        }
