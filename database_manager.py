import sqlite3
import pandas as pd
from tyre import Tyre


class DatabaseManager:
    """Handles all database operations for tyre data."""
    
    def __init__(self, db_name: str = 'tyres.db'):
        self.db_name = db_name
    
    def init_db(self) -> None:
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tyres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT,
            name TEXT,
            brand TEXT,
            size TEXT,
            price REAL,
            type TEXT,
            wet_grip TEXT,
            fuel_efficiency TEXT,
            load_index INTEGER,
            speed_rating TEXT,
            electric INTEGER,
            self_seal INTEGER,
            run_flat INTEGER,
            noise_reduction INTEGER,
            seasonality TEXT
        )''')
        conn.commit()
        conn.close()
    
    def save_tyre(self, tyre: Tyre) -> None:
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''INSERT INTO tyres (
            website, name, brand, size, price, type, wet_grip, fuel_efficiency,
            load_index, speed_rating, electric, self_seal, run_flat, noise_reduction, seasonality
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            tyre.website,
            tyre.name,
            tyre.brand,
            tyre.size,
            tyre.price,
            tyre.type.value if tyre.type else None,
            tyre.wet_grip.value if tyre.wet_grip else None,
            tyre.fuel_efficiency.value if tyre.fuel_efficiency else None,
            tyre.load_index,
            tyre.speed_rating.value if tyre.speed_rating else None,
            1 if tyre.electric else (0 if tyre.electric is False else None),
            1 if tyre.self_seal else (0 if tyre.self_seal is False else None),
            1 if tyre.run_flat else (0 if tyre.run_flat is False else None),
            1 if tyre.noise_reduction else (0 if tyre.noise_reduction is False else None),
            tyre.seasonality.value if tyre.seasonality else None,
        ))
        conn.commit()
        conn.close()
    
    def export_to_csv(self, csv_name: str = 'tyres_export.csv') -> None:
        """Export database contents to CSV file."""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query('SELECT * FROM tyres', conn)
        df.to_csv(csv_name, index=False)
        conn.close()
