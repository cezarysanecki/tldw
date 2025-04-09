import requests
from bs4 import BeautifulSoup


class ArticleContentExtractor:

    def __init__(self, url):
        self.soup = None

        try:
            response = requests.get(url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error while downloading page content: {e}")
            raise e
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise e

    def run(self):
        return {
            "title": self.__find_title(),
            "content": self.__find_content()
        }

    def __find_title(self):
        if self.soup.find('h1'):
            print("Found 'h1' element")
            title = self.soup.find('h1').get_text()
        else:
            print("Not found title element on page")
            raise Exception(f'Title not found')
        return title.strip()


    def __find_content(self):
        content = ""
        if self.soup.find('article'):
            print("Found 'article' element")
            texts = self.soup.find('article').find_all('p')
            content = "\n".join([p.get_text() for p in texts])
        elif self.soup.find(class_="article-body"):
            print("Found 'article-body' class element")
            texts = self.soup.find(class_="article-body").find_all('p')
            content = "\n".join([p.get_text() for p in texts])
        else:
            print("Not found article element on page")
            pass
        return content.strip()


