with open("schema.py", "w") as f:
    f.write('''
from typing import List, Optional
from pydantic import BaseModel, Field

class PropertyMeasurementExtract(BaseModel):
    temperature_celsius: Optional[float] = Field(default=None)
    ionic_conductivity_s_cm: Optional[float] = Field(default=None)
    ionic_conductivity_raw: Optional[str] = Field(default=None)
    activation_energy_ev: Optional[float] = Field(default=None)
    electronic_conductivity_s_cm: Optional[float] = Field(default=None)
    interfacial_resistance_ohm_cm2: Optional[float] = Field(default=None)
    stability_window_volts: Optional[float] = Field(default=None)
    measurement_method: Optional[str] = Field(default=None)

class MaterialExtract(BaseModel):
    chemical_formula: str
    normalized_formula: Optional[str] = Field(default=None)
    electrolyte_family: Optional[str] = Field(default=None)
    crystal_structure: Optional[str] = Field(default=None)
    synthesis_method: Optional[str] = Field(default=None)
    sintering_temperature_c: Optional[float] = Field(default=None)
    sintering_time_hours: Optional[float] = Field(default=None)
    relative_density_percent: Optional[float] = Field(default=None)
    measurements: List[PropertyMeasurementExtract] = Field(default_factory=list)

class PaperExtractionResult(BaseModel):
    title: str
    doi: Optional[str] = Field(default=None)
    authors: Optional[str] = Field(default=None)
    publication_year: Optional[int] = Field(default=None)
    journal: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    materials: List[MaterialExtract] = Field(default_factory=list)
''')
