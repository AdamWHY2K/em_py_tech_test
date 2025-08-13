import re
import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from database_manager import DatabaseManager
from tyre import Tyre
from tyre_data_parser import TyreDataParser


class NationalTyresScraper:
    """Web scraper specifically for www.national.co.uk tyre data."""
    
    WEBSITE = 'www.national.co.uk'
    # Seconds
    REQUEST_TIMEOUT = 5
    SCRAPE_TIMEOUT = 3

    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.parser = TyreDataParser()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; TyreScraper/1.0)'
        }
    
    def _build_url(self, tyre_params: Dict[str, int]) -> str:
        return (f'https://www.national.co.uk/tyres-search/'
                f'{tyre_params["width"]}-{tyre_params["aspect_ratio"]}-{tyre_params["rim_size"]}')
    
    def _extract_tyre_display_data(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract all tyre data from parent divs with class 'tyreDisplay'.
        Uses data-* attributes and child tyreresult divs.
        """
        results = []
        for tyrediv in soup.find_all('div', class_='tyreDisplay'):
            details = self._extract_single_tyre_data(tyrediv)
            results.append(details)
        return results
    
    def _extract_single_tyre_data(self, tyrediv) -> Dict:
        """Extract data from a single tyre display div."""
        details = {}
        
        # Extract all data-* attributes
        for attr, value in tyrediv.attrs.items():
            if attr.startswith('data-'):
                details[attr[5:]] = value
        
        # Find the tyreresult child for more details
        tyreresult = tyrediv.find('div', class_='tyreresult')
        if tyreresult:
            self._extract_tyreresult_data(tyreresult, details)

        if 'price' in details:
            try:
                details['price'] = float(details['price'])
            except (ValueError, TypeError):
                pass
        
        return details
    
    def _extract_tyreresult_data(self, tyreresult, details: Dict) -> None:
        pattern = tyreresult.find('a', class_='pattern_link')
        if pattern:
            details['pattern'] = pattern.get_text(strip=True)

        self._extract_size_info(tyreresult, details)
        self._extract_load_speed_info(tyreresult, details)
        self._extract_fitment_features(tyreresult, details)

        details_div = tyreresult.find('div', class_='details')
        if details_div:
            details['details_text'] = details_div.get_text(separator=' ', strip=True)
    
    def _extract_size_info(self, tyreresult, details: Dict) -> None:
        for p in tyreresult.find_all('p'):
            txt = p.get_text(strip=True)
            if re.match(r'\d{3}/\d{2} R\d{2}', txt):
                details['size'] = txt
                break
    
    def _extract_load_speed_info(self, tyreresult, details: Dict) -> None:
        for p in tyreresult.find_all('p'):
            text = p.get_text()
            if 'Load Index:' in text:
                val = p.find_all('span', class_='red')
                if val:
                    details['load_index'] = val[0].get_text(strip=True)
            if 'Speed Rating:' in text:
                val = p.find_all('span', class_='red')
                if val:
                    details['speed_rating'] = val[0].get_text(strip=True)
    
    def _extract_fitment_features(self, tyreresult, details: Dict) -> None:
        fitments = []
        for img in tyreresult.find_all('img', class_='fitment'):
            title = img.get('title')
            if title:
                fitments.append(title.strip())
        if fitments:
            details['fitment'] = ', '.join(fitments)
    
    def _convert_to_tyre_object(self, data: Dict) -> Tyre:
        # Mandatory fields
        name = data.get('pattern')
        brand = data.get('brand')
        size = data.get('size')
        price_raw = data.get('price')
        self._validate_mandatory_fields(name, brand, size, price_raw, data)

        # Process validated mandatory fields
        brand = brand.title()
        price = float(price_raw)
        
        # Parse optional fields
        seasonality = self.parser.parse_seasonality(data.get('tyre-season'))
        tyre_type = self.parser.parse_tyre_type(data.get('tyre-type')) if data.get('tyre-type') else None
        wet_grip = self.parser.parse_grade(data.get('grip', ''))
        fuel_efficiency = self.parser.parse_grade(data.get('fuel', ''))
        
        load_index, speed_rating = self.parser.parse_load_index_and_speed_rating(data, size)
        boolean_features = self.parser.parse_boolean_features(data)
        
        # Convert load_index to None if invalid/missing
        if load_index <= 0:
            load_index = None
        
        return Tyre(
            # Mandatory fields
            website=self.WEBSITE,
            brand=brand,
            name=name,
            size=size,
            price=price,
            # Optional fields
            seasonality=seasonality,
            type=tyre_type,
            wet_grip=wet_grip,
            fuel_efficiency=fuel_efficiency,
            speed_rating=speed_rating,
            load_index=load_index,
            electric=boolean_features.get('electric'),
            self_seal=boolean_features.get('self_seal'),
            run_flat=boolean_features.get('run_flat'),
            noise_reduction=boolean_features.get('noise_reduction'),
        )
    
    def _validate_mandatory_fields(self, name: str, brand: str, size: str, price_raw: str, data: Dict) -> None:
        missing_fields = []

        if not name or name.strip() == '':
            missing_fields.append('name/pattern')

        if not brand or brand.strip() == '':
            missing_fields.append('brand')
        
        if not size or size.strip() == '':
            missing_fields.append('size')
        
        if not price_raw or price_raw == '':
            missing_fields.append('price')
        else:
            try:
                price_float = float(price_raw)
                if price_float <= 0:
                    missing_fields.append('price (must be > 0)')
            except (ValueError, TypeError):
                missing_fields.append('price (invalid format)')
        
        if missing_fields:
            raise ValueError(f"Missing mandatory fields: {', '.join(missing_fields)}. Data: {data}")
    
    def scrape_tyres(self, tyre_params: Dict[str, int]) -> None:
        """Scrape tyres for given parameters and save to database."""
        base_url = self._build_url(tyre_params)
        
        try:
            response = requests.get(base_url, headers=self.headers, timeout=self.REQUEST_TIMEOUT)
            print(f"Sleeping for {self.SCRAPE_TIMEOUT} seconds so we don't abuse the site")
            time.sleep(self.SCRAPE_TIMEOUT)
            
            if response.status_code != 200:
                print(f"Failed to fetch data for {tyre_params} (Status: {response.status_code})")
                return
            
            soup = BeautifulSoup(response.content, "html.parser")
            results = self._extract_tyre_display_data(soup)
            
            for data in results:
                try:
                    tyre = self._convert_to_tyre_object(data)
                    self.db_manager.save_tyre(tyre)
                except (ValueError, TypeError, KeyError) as e:
                    print(f"Error processing tyre data: {e}")
                    continue
            
            print(f"Scraped {len(results)} tyres for {tyre_params}\n")
            
        except requests.RequestException as e:
            print(f"Request failed for {tyre_params}: {e}")
        except (ValueError, TypeError) as e:
            print(f"Data processing error for {tyre_params}: {e}")
