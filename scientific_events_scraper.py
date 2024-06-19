import json
import requests
import pdfplumber
from io import BytesIO
from bs4 import BeautifulSoup
from unsafe_adapter import UnsafeAdapter


class ScientificEventsScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.mount("https://", UnsafeAdapter())

    def get_soup(self, url):
        res = self.session.get(url)
        return BeautifulSoup(res.text, "html.parser")

    def get_years(self, url, specific_year=None):
        soup = self.get_soup(url)
        years = []
        for link in soup.find_all("a"):
            year = link.get("href").split("/")[-1]
            if specific_year:
                if specific_year == year:
                    years.append(
                        {"year": year, "link": self.base_url + link.get("href")}
                    )
            else:
                years.append({"year": year, "link": self.base_url + link.get("href")})
        return years

    def get_events(self, years):
        events = []
        for year in years:
            soup = self.get_soup(year["link"])
            for link in soup.find_all("a"):
                href = link.get("href")
                if href and link.string:
                    events.append(
                        {
                            "event": link.string,
                            "year": year["year"],
                            "link": self.base_url + href,
                        }
                    )
        return events

    def get_areas(self, events):
        areas = []
        for event in events:
            soup = self.get_soup(event["link"])
            for link in soup.find_all("a"):
                if link.get("href") and link.get("class"):
                    for l in link.children:
                        if l.string and len(l.string) > 5:
                            areas.append(
                                {
                                    "event": event["event"],
                                    "year": event["year"],
                                    "area": l.string,
                                    "link": self.base_url + link.get("href"),
                                }
                            )
        return areas

    def get_papers(self, areas):
        papers = []
        for area in areas:
            soup = self.get_soup(area["link"])
            for link in soup.find_all("a"):
                if link.string and link.get("class") and len(link.string) > 5:
                    papers.append(
                        {
                            "id": link.get("id"),
                            "paper": link.string.strip(),
                            "area": area["area"],
                            "year": area["year"],
                            "event": area["event"],
                            "link": f"{self.base_url}/encontroscientificos/trabalho/{link.get('id')}",
                        }
                    )
        return papers

    def get_complete_papers(self, papers):
        complete_papers = []
        for paper in papers:
            soup = self.get_soup(paper["link"])
            for link in soup.find_all("a"):
                if link.string == "Trabalho completo":
                    paper["link"] = link.get("href")
                    complete_papers.append(paper)
        return complete_papers

    def extract_text_from_pdf(self, url):
        response = self.session.get(url)
        pdf_file = BytesIO(response.content)
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text

    def get_complete_text(self, papers):
        for paper in papers:
            paper["content"] = self.extract_text_from_pdf(paper["link"])
        return papers

    def save_to_json(self, data, filename):
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)
        print(f"Data saved to '{filename}'.")

    def run(self, specific_year=None):
        url = f"{self.base_url}/encontroscientificos/"
        years = self.get_years(url, specific_year)
        events = self.get_events(years)
        areas = self.get_areas(events)
        papers = self.get_papers(areas)
        complete_papers = self.get_complete_papers(papers)
        result = self.get_complete_text(complete_papers)
        self.save_to_json(result, "result.json")
