with open("pipeline.py", "w") as f:
    f.write(r'''
import os, glob, argparse, pandas as pd
from db import SSEDatabase
from parser import ScientificPDFParser
from free_extractor import FreeSSEInformationExtractor
from fetcher import ScientificPaperFetcher

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--query", type=str, default="solid state electrolyte ionic conductivity")
    parser.add_argument("--max-papers", type=int, default=5)
    parser.add_argument("--input-dir", type=str, default="./papers")
    parser.add_argument("--db", type=str, default="sse_research.db")
    parser.add_argument("--export-csv", type=str)
    args = parser.parse_args()

    if args.export_csv:
        db = SSEDatabase(args.db)
        df = db.export_flattened_df()
        df.to_csv(args.export_csv, index=False)
        print(f"[OK] Exported {len(df)} records to {args.export_csv}")
        return

    if args.fetch:
        fetcher = ScientificPaperFetcher(download_dir=args.input_dir)
        fetcher.fetch_arxiv_papers(query=args.query, max_results=args.max_papers)

    db = SSEDatabase(args.db)
    pdf_parser = ScientificPDFParser()
    extractor = FreeSSEInformationExtractor()
    pdf_files = glob.glob(os.path.join(args.input_dir, "*.pdf"))

    print(f"Processing {len(pdf_files)} PDF papers...")
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        if db.is_file_processed(filename): continue
        try:
            text, engine = pdf_parser.parse_pdf(pdf_path)
            res = extractor.extract_from_markdown(text, filename)
            db.save_paper_extraction(filename, text, res)
            print(f" [OK] Parsed & Saved: {filename}")
        except Exception as e:
            print(f" [ERROR] Failed {filename}: {e}")

    df = db.export_flattened_df()
    print("\n=== EXTRACTED SSE RESEARCH DATABASE ===")
    print(df[['chemical_formula', 'electrolyte_family', 'temperature_celsius', 'ionic_conductivity_s_cm']].to_string())

if __name__ == "__main__":
    main()
''')
