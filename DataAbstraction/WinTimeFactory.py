from DataAbstraction.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper
from bs4 import BeautifulSoup


class WinTimeFactory:

    def __init__(self):
        self.__scraper = get_scraper()

    def get_win_time(self, race_card: RaceCard) -> float:
        result_doc = self.__scraper.request_html("https://t.attheraces.com/results/05-Jun-2022")
        soup = BeautifulSoup(result_doc, 'html.parser')

        #for b_elem in soup.find_all('b'):
        #    print(b_elem)

        for a in soup.find_all('a', href=True):
            if "/racecard/Goodwood" in a['href'] and "button" not in a["class"]:
                race_card_number = a.findPrevious().text
                if int(race_card_number) == 2:
                    article = a.findParent("article")
                    win_time_div = [div for div in article.find_all("div") if "Win Time" in div.next_element.text][0]
                    win_time_start_idx = self.__find_win_time_start_idx(win_time_div.text)
                    win_time_end_idx = win_time_div.text.find("s") + 1
                    print(win_time_div)
                    win_time_text = win_time_div.text[win_time_start_idx:win_time_end_idx]
                    print(win_time_text)
                    return self.__win_time_text_to_seconds(win_time_text)

        return -1

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
    win_time = win_time_factory.get_win_time(None)
    print(win_time)


if __name__ == '__main__':
    main()
