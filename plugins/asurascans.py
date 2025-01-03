
from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus

from bs4 import BeautifulSoup

from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter
import re
import requests

class AsuraScansClient(MangaClient):

    base_url = urlparse("https://asuracomic.net/")
    search_url = base_url.geturl()
    search_param = 's'
    updates_url = base_url.geturl()

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def __init__(self, *args, name="AsuraScans", **kwargs):
        super().__init__(*args, name=name, headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        container = bs.find("div", {"class": "grid grid-cols-2 sm:grid-cols-2 md:grid-cols-5 gap-3 p-4"})

        cards = container.find_all("div", {"class": "flex h-[250px] md:h-[200px] overflow-hidden relative hover:opacity-60"})

        names = [containers.findChild('span', {'class': 'block text-[13.3px] font-bold'}).string.strip() for containers in container]
        l = "https://asuracomic.net/"
        url = [l + containers.get("href") for containers in container]
        images = [card.findNext("img").get("src") for card in cards]

        mangas = [MangaCard(self, *tup) for tup in zip(names, url, images)]

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        li = bs.findAll("h3", {"class": "text-sm text-white font-medium"})
        
        a = "https://asuracomic.net/series/"
        links = [a + containers.findNext("a").get("href") for containers in li]
        
        b = "Chapter "
        texts = [b + str(sub.split('/')[6]) for sub in links]
        
        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    async def updates_from_page(self):
        page = await self.get_url(self.updates_url)
        
        bs = BeautifulSoup(page, "html.parser")

        manga_items = bs.find_all("span", {"class": "text-[15px] font-medium hover:text-themecolor hover:cursor-pointer"})

        urls = dict()

        for manga_item in manga_items:
            manga_url =  urljoin(self.base_url.geturl(), manga_item.findNext("a").get("href"))

            if manga_url in urls:
                continue

            chapter_url = urljoin(self.base_url.geturl(), manga_item.findNext("span").findNext("a").get("href"))
            
            urls[manga_url] = chapter_url

        return urls

    async def pictures_from_chapters(self, data: bytes, response=None):
        soup = BeautifulSoup(data, 'html.parser')
        
        script_tags = soup.find_all("script") 
        scripts = [tag.text for tag in script_tags if "self.__next_f.push" in tag.text and "https://gg.asuracomic.net/storage/media" in tag.text and "url" in tag.text]
        
        pattern = r"https://gg\.asuracomic\.net/storage/media/\d+/conversions/[0-9A-Z]+(?:_result)?-optimized\.webp"
       
        images_url = re.findall(pattern, scripts[0])               
        return images_url

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        query = quote_plus(query)

        request_url = self.search_url

        if query:
            request_url += f'series?page=1&name={query}'

        content = await self.get_url(request_url)

        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:

        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        return self.chapters_from_page(content, manga_card)[(page - 1) * 20:page * 20]

    async def iter_chapters(self, manga_url: str, manga_name) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')

        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        for chapter in self.chapters_from_page(content, manga_card):
            yield chapter

    async def contains_url(self, url: str):
        return url.startswith(self.base_url.geturl())

    async def check_updated_urls(self, last_chapters: List[LastChapter]):
        updates = await self.updates_from_page()
        
        updated = []
        not_updated = []
        for lc in last_chapters:
            if lc.url in updates.keys():
                if updates.get(lc.url) != lc.chapter_url:
                    updated.append(lc.url)
                elif updates.get(lc.url) == lc.chapter_url:
                    not_updated.append(lc.url)
                
        return updated, not_updated
