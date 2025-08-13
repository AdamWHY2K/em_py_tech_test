from database_manager import DatabaseManager
from national_tyres_scraper import NationalTyresScraper


class TyreScrapingOrchestrator:  
    def __init__(self, db_name: str = 'tyres.db', csv_name: str = 'tyres_export.csv'):
        self.db_manager = DatabaseManager(db_name)
        self.scraper = NationalTyresScraper(self.db_manager)
        self.csv_name = csv_name

        self.tyre_inputs = [
            {'width': 205, 'aspect_ratio': 55, 'rim_size': 16},
            {'width': 225, 'aspect_ratio': 50, 'rim_size': 16},
            {'width': 185, 'aspect_ratio': 16, 'rim_size': 14},
        ]
    
    def run_scraping_process(self) -> None:
        print("Initializing database...")
        self.db_manager.init_db()
        
        print("Starting scraping process...")
        for tyre_input in self.tyre_inputs:
            print(f"Scraping tyres for size {tyre_input['width']}/{tyre_input['aspect_ratio']} R{tyre_input['rim_size']}")
            self.scraper.scrape_tyres(tyre_input)
        
        print("Exporting to CSV...")
        self.db_manager.export_to_csv(self.csv_name)
        
        print(f"Scraping complete. Data saved to database and exported to {self.csv_name}.")
