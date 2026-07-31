with open("free_extractor.py", "w") as f:
    f.write(r'''
import re
from schema import PaperExtractionResult, MaterialExtract, PropertyMeasurementExtract

class FreeSSEInformationExtractor:
    def extract_from_markdown(self, markdown_text: str, filename: str) -> PaperExtractionResult:
        title_match = re.search(r'^#\s+(.+)$', markdown_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename.replace('.pdf', '')

        formula_pattern = r'\b(Li[0-9\.\-_A-Za-z]+O[0-9\.]*|Li[0-9\.\-_A-Za-z]+S[0-9\.]*|Li[0-9\.\-_A-Za-z]+Cl[0-9\.]*|Li[0-9\.\-_A-Za-z]+PO4[0-9\.]*)\b'
        matches = list(dict.fromkeys(re.findall(formula_pattern, markdown_text)))
        valid_formulas = [f for f in matches if len(f) > 4 and any(c.isdigit() for c in f)]
        if not valid_formulas:
            for k in ["LLZO", "LLZTO", "LGPS", "LATP", "LAGP", "LPS"]:
                if k in markdown_text: valid_formulas.append(k)

        cond_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:[x×\*]\s*10\^?([+-]?\d+))?\s*(mS|uS|S)\s*[\/·\s]*cm', markdown_text)
        ea_matches = re.findall(r'(\d+\.\d+)\s*eV', markdown_text)
        ea_val = float(ea_matches[0]) if ea_matches else None

        measurements = []
        for raw_val, exp, unit in cond_matches[:3]:
            val = float(raw_val)
            if exp: val *= (10 ** float(exp))
            if unit == "mS": val *= 1e-3
            elif unit == "uS": val *= 1e-6
            measurements.append(PropertyMeasurementExtract(temperature_celsius=25.0, ionic_conductivity_s_cm=val, ionic_conductivity_raw=f"{raw_val} {unit}/cm", activation_energy_ev=ea_val))

        materials = [MaterialExtract(chemical_formula=f, electrolyte_family="Solid Electrolyte", measurements=measurements if measurements else [PropertyMeasurementExtract(temperature_celsius=25.0)]) for f in valid_formulas[:5]]
        if not materials:
            materials.append(MaterialExtract(chemical_formula="Lithium Solid Electrolyte", electrolyte_family="Solid Electrolyte", measurements=measurements))
        return PaperExtractionResult(title=title, materials=materials)
''')
