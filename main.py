import os
import json
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from scientific_events_scraper import ScientificEventsScraper


def extract_content(file):
    diretorio = "ok"
    with open(f"{diretorio}/{file}", "r", encoding="utf-8") as json_file:
        conteudo = json.load(json_file)
    return conteudo


if __name__ == "__main__":
    diretorio = "artigos"
    extr = ScientificEventsScraper("")

    # Processing each JSON file in the directory
    for file in os.listdir(diretorio):
        try:
            if file.endswith(".json"):
                with open(f"{diretorio}/{file}", "r", encoding="utf-8") as json_file:
                    urls_to_extract = json.load(json_file)
                urls_to_extract["conteudo"] = extr.extract_text_from_pdf(
                    urls_to_extract["link"]
                )
                with open(f"{diretorio}/{file}", "w", encoding="utf-8") as json_file:
                    json.dump(urls_to_extract, json_file, indent=2, ensure_ascii=False)
                os.rename(f"{diretorio}/{file}", f"{diretorio}/ok/{file}")
        except Exception as e:
            print(f"Error processing {file}: {e}")

    # Using multiprocessing to extract content from all JSON files in parallel
    with Pool(cpu_count()) as executor:
        result = executor.map(extract_content, os.listdir("ok"))

    # Writing the extracted content to result.json
    with open("result.json", "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=2, ensure_ascii=False)
