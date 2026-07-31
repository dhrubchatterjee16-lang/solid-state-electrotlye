with open("db.py", "w") as f:
    f.write('''
import sqlite3
import pandas as pd
from schema import PaperExtractionResult

class SSEDatabase:
    def __init__(self, db_path: str = "sse_research.db"):
        self.db_path = db_path.replace("sqlite:///", "")
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                title TEXT, doi TEXT, authors TEXT, publication_year INTEGER, journal TEXT, summary TEXT, raw_markdown TEXT, status TEXT DEFAULT 'SUCCESS', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT, paper_id INTEGER NOT NULL, chemical_formula TEXT NOT NULL, normalized_formula TEXT, electrolyte_family TEXT, crystal_structure TEXT, synthesis_method TEXT, sintering_temperature_c REAL, sintering_time_hours REAL, relative_density_percent REAL, FOREIGN KEY (paper_id) REFERENCES papers (id)
            )""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT, material_id INTEGER NOT NULL, temperature_celsius REAL, ionic_conductivity_s_cm REAL, ionic_conductivity_raw TEXT, activation_energy_ev REAL, electronic_conductivity_s_cm REAL, interfacial_resistance_ohm_cm2 REAL, stability_window_volts REAL, measurement_method TEXT, FOREIGN KEY (material_id) REFERENCES materials (id)
            )""")
            conn.commit()

    def save_paper_extraction(self, filename: str, raw_md: str, extraction: PaperExtractionResult) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO papers (filename, title, doi, authors, publication_year, journal, summary, raw_markdown) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (filename, extraction.title, extraction.doi, extraction.authors, extraction.publication_year, extraction.journal, extraction.summary, raw_md[:50000] if raw_md else ""))
            paper_id = cursor.lastrowid

            for mat in extraction.materials:
                cursor.execute("INSERT INTO materials (paper_id, chemical_formula, normalized_formula, electrolyte_family, crystal_structure, synthesis_method, sintering_temperature_c, sintering_time_hours, relative_density_percent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (paper_id, mat.chemical_formula, mat.normalized_formula, mat.electrolyte_family, mat.crystal_structure, mat.synthesis_method, mat.sintering_temperature_c, mat.sintering_time_hours, mat.relative_density_percent))
                material_id = cursor.lastrowid

                for meas in mat.measurements:
                    cursor.execute("INSERT INTO measurements (material_id, temperature_celsius, ionic_conductivity_s_cm, ionic_conductivity_raw, activation_energy_ev, electronic_conductivity_s_cm, interfacial_resistance_ohm_cm2, stability_window_volts, measurement_method) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (material_id, meas.temperature_celsius, meas.ionic_conductivity_s_cm, meas.ionic_conductivity_raw, meas.activation_energy_ev, meas.electronic_conductivity_s_cm, meas.interfacial_resistance_ohm_cm2, meas.stability_window_volts, meas.measurement_method))
            conn.commit()
            return paper_id

    def is_file_processed(self, filename: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM papers WHERE filename = ? AND status = 'SUCCESS'", (filename,))
            return cursor.fetchone()[0] > 0

    def export_flattened_df(self) -> pd.DataFrame:
        query = """
            SELECT p.filename, p.title AS paper_title, p.publication_year, p.journal, m.chemical_formula, m.normalized_formula, m.electrolyte_family, m.crystal_structure, m.synthesis_method, m.sintering_temperature_c, m.relative_density_percent, meas.temperature_celsius, meas.ionic_conductivity_s_cm, meas.ionic_conductivity_raw, meas.activation_energy_ev, meas.interfacial_resistance_ohm_cm2, meas.stability_window_volts
            FROM papers p JOIN materials m ON p.id = m.paper_id LEFT JOIN measurements meas ON m.id = meas.material_id
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)
''')
