import os
import json
from scientific_events_scraper import ScientificEventsScraper

diretorio = "artigos"

if __name__ == "__main__":
    extr = ScientificEventsScraper("")
    for file in os.listdir(diretorio):
        try:
            if ".json" in file:
                with open(f"{diretorio}/{file}", "r", encoding="utf-8") as json_file:
                    urls_to_extract = json.load(json_file)
                urls_to_extract["conteudo"] = extr.extract_text_from_pdf(
                    urls_to_extract["link"]
                )
                with open(f"{diretorio}/{file}", "w", encoding="utf-8") as json_file:
                    json.dump(urls_to_extract, json_file, indent=2, ensure_ascii=False)
                os.rename(f"{diretorio}/{file}", f"{diretorio}/ok/{file}")
        except:
            continue
