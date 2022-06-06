from DataAbstraction.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper
from bs4 import BeautifulSoup

from Persistence.RaceCardPersistence import RaceCardsPersistence


class WinTimeFactory:

    def __init__(self):
        self.__scraper = get_scraper()
        self.__base_results_url = "https://t.attheraces.com/results"

    def get_win_time(self, race_card: RaceCard) -> float:
        results_url = f"{self.__base_results_url}/{race_card.datetime.date()}"
        result_doc = self.__scraper.request_html(results_url)
        article = self.__find_article_of_race_card(result_doc, race_card)
        win_time_text = self.__find_win_time_text(article)

        return self.__win_time_text_to_seconds(win_time_text)

    def __find_article_of_race_card(self, result_doc: str, race_card: RaceCard):
        soup = BeautifulSoup(result_doc, 'html.parser')

        for link in soup.find_all('a', href=True):
            if self.__link_corresponds_to_race_card(link, race_card):
                return link.findParent("article")

    def __find_win_time_text(self, article) -> str:
        win_time_div = [div for div in article.find_all("div") if "Win Time" in div.next_element.text][0]
        win_time_start_idx = self.__find_win_time_start_idx(win_time_div.text)
        win_time_end_idx = win_time_div.text.find("s") + 1

        return win_time_div.text[win_time_start_idx:win_time_end_idx]

    def __link_corresponds_to_race_card(self, link, race_card: RaceCard) -> bool:
        if f"/racecard/{race_card.title}" not in link['href']:
            return False

        if "button" in link["class"]:
            return False

        link_number = int(link.findPrevious().text)

        return link_number == race_card.number

    def __find_win_time_start_idx(self, div_text: str) -> int:
        for i, c in enumerate(div_text):
            if c.isdigit():
                return i

    def __win_time_text_to_seconds(self, win_time_text: str) -> float:
        return self.__get_minutes_of_win_time(win_time_text) * 60 + self.__get_seconds_of_win_time(win_time_text)

    def __get_minutes_of_win_time(self, win_time_text: str) -> int:
        start_idx = 0
        end_idx = win_time_text.find("m")

        return int(win_time_text[start_idx:end_idx])

    def __get_seconds_of_win_time(self, win_time_text: str) -> float:
        start_idx = win_time_text.find(" ") + 1
        end_idx = len(win_time_text) - 1

        return float(win_time_text[start_idx:end_idx])


def main():
    win_time_factory = WinTimeFactory()

    raw_races = RaceCardsPersistence("test_race_cards").load_raw()
    race_cards = [RaceCard(race_id, raw_races[race_id], remove_non_starters=False) for race_id in raw_races]

    win_time = win_time_factory.get_win_time(race_cards[1])
    print(win_time)


if __name__ == '__main__':
    main()
