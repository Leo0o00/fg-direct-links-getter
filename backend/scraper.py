import traceback

import bs4
import concurrent.futures
import re
import requests
import undetected_chromedriver as uc
from cache import cache

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service as BraveService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.by import By
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FitGirlScraper/1.0; +https://example.com/)"
}


@cache.memoize(timeout=30)
def _soup(url: str) -> bs4.BeautifulSoup:
    html = requests.get(url, headers=HEADERS, timeout=30).text
    print(url)
    return bs4.BeautifulSoup(html, "html.parser")
    # try:
    #     # return bs4.BeautifulSoup(html, "html.parser")
    #     options = webdriver.ChromeOptions()
    #     options.add_experimental_option("detach", True)
    #     options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #     options.add_experimental_option('useAutomationExtension', False)
    #     options.add_argument("--headless")
    #     options.add_argument("--disable-blink-features=AutomationControlled")
    #     options.add_argument('--disable-extensions')
    #     options.add_argument('--no-sandbox')
    #     options.add_argument('--disable-infobars')
    #     options.add_argument('--disable-dev-shm-usage')
    #     options.add_argument('--disable-browser-side-navigation')
    #     options.add_argument('--disable-gpu')
    #
    #     # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    #     #
    #     # driver.execute_script(f"window.open({url}, '_blank')")
    #     # time.sleep(25)
    #     # driver.switch_to.window(driver.window_handles[1])
    #     #
    #     # driver.switch_to.frame(0)
    #     #
    #     # driver.find_element(By.XPATH, '//*[@id="challenge-stage"]/div/label/input').click()
    #     # driver = uc.Chrome(headless=True, use_subprocess=False)
    #     driver = webdriver.Chrome(service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))
    #
    #     try:
    #         driver.get(url)
    #         html = driver.page_source
    #         print("Downloaded Page: ")
    #         print(html)
    #         return bs4.BeautifulSoup(html, "html.parser")
    #     except Exception as e:
    #         print(f"[Error getting html from {url}]: {e}]")
    #     finally:
    #         driver.quit()
    # except Exception:
    #     # JS-only mirror: use headless Chrome
    #     # opts = Options()
    #     # opts.add_argument("--headless=new")  # modern headless :contentReference[oaicite:8]{index=8}
    #     # driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    #
    #     # options = webdriver.ChromeOptions()
    #     # options.add_experimental_option("detach", True)
    #     # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #     # options.add_experimental_option('useAutomationExtension', False)
    #     # options.add_argument("--disable-blink-features=AutomationControlled")
    #     # options.add_argument('--disable-extensions')
    #     # options.add_argument('--no-sandbox')
    #     # options.add_argument('--disable-infobars')
    #     # options.add_argument('--disable-dev-shm-usage')
    #     # options.add_argument('--disable-browser-side-navigation')
    #     # options.add_argument('--disable-gpu')
    #     #
    #     # driver = webdriver.Chrome(options=options)
    #     #
    #     # driver.execute_script("window.open('https://nowsecure.nl/', '_blank')")
    #     # time.sleep(25)
    #     # driver.switch_to.window(driver.window_handles[1])
    #     #
    #     # driver.switch_to.frame(0)
    #     #
    #     # driver.find_element(By.XPATH, '//*[@id="challenge-stage"]/div/label/input').click()
    #     #
    #     # try:
    #     #     driver.get(url)
    #     #     html = driver.page_source
    #     #     return bs4.BeautifulSoup(html, "lxml")
    #     # finally:
    #     #     driver.quit()
    #
    #     print(f"[FatalError: ]{Exception.__class__.__name__}: {traceback.format_exc()}")


# 1) Scrape the FitGirl post and collect every “Download Mirrors (Direct Links)” href.
# def mirror_links(post_url: str) -> list[str]:
#     soup = _soup(post_url)
#     # look for the H2 then take every <a> until the next header
#     h2 = soup.find(lambda tag: tag.name in ["h2", "strong"] and "Download Mirrors (Direct Links)" in tag.text)
#     links = []
#     for a in h2.find_all_next("a", href=True):
#         if a.name == "strong" or a.text.strip().startswith("•"):
#             continue  # skip eventual bullet chars
#         if a.find_parent(lambda p: p.name in ["h2", "h3"]):
#             break  # stop at next section
#         links.append(urljoin(post_url, a["href"]))
#     return links

def mirror_links(fg_url: str) -> list[str]:
    """Return every ‘mirror-page’ (e.g. fuckingfast.co / datanodes.cc …)."""
    page = _soup(fg_url)
    print(page)
    mirrors: list[str] = []

    # Aqui iteramos por los elementos de la pagina en busqueda de los enlaces de descarga del Filehoster FuckingFast
    # especificamente
    # TODO: Implementar la busqueda de todos los filehoster de descarga directa disponibles en la pagina

    # Buscar todas las etiquetas h3 de la pagina e itera sobre ellas
    for h3 in page.select("h3"):
        # Comprobar que el texto de la etiqueta diga "Download Mirrors (Direct Links)"
        # Si se cumple prosigue con las demas instrucciones, sino salta a la siguiente etiqueta h3
        if h3.get_text(strip=True).startswith("Download Mirrors (Direct Links)"):
            # Buscar la lista de Filehosters que le sigue marcada por una etiqueta ul
            ul = h3.find_next("ul")
            # Si no existe continua con el siguiete elemento h3 de la iteracion
            if not ul:
                continue
            # Si existe itera por la lista de Filehosters buscando la lista de enlaces de FuckingFast especificamente
            for li in ul.select("li"):
                a = li.select("a")
                if a[0].get_text(strip=True).startswith("Filehoster: FuckingFast"):
                    div = li.select("div")
                    interior_divs = div[0].select("div")
                    for div in interior_divs:
                        span = div.select("span")
                        if len(span) > 0:
                            continue
                        a = div.select("a")
                        if len(a) > 0:
                            for anchors in a:
                                mirrors.append(anchors["href"])
                continue
            break  # only the first mirrors block is needed
    return mirrors


# 2) On each mirror page, grab the direct URL hidden inside `window.open("…")`.
# _DIRECT_RE = re.compile(r'window\.open\("(?P<url>https?://[^"]+)"')-
_DIRECT_RE = re.compile(r'window\.open\(\s*["\']([^"\']+)["\']')  # grabs url in download()


# def direct_link(mirror_url: str) -> str | None:
#     soup = _soup(mirror_url)
#     for script in soup.find_all("script"):
#         m = _DIRECT_RE.search(script.string or "")
#         if m:
#             return m.group("url")
#     return None

def direct_link(mirror_url: str) -> str | None:
    """Extract the *first* real file URL hidden in the JS download() fn."""
    try:
        s = _soup(mirror_url)  # Cloudflare blocks? retry via Selenium
        # print("s: ")
        # print(s)
        js = s.find_all("script")[-2].string or ""
        # print("js: ")
        # print(js)
        m = _DIRECT_RE.search(js)
        # print("m: ")
        # print(m)
        return m.group(1) if m else None
    except Exception as exc:  # you may want proper logging here
        print(f"[warn] {mirror_url} – {exc}")
        return None


# 3) Orchestrator
def gather_direct_links(post_url: list[str]) -> list[str]:
    # mirrors = mirror_links(post_url)
    with concurrent.futures.ThreadPoolExecutor() as ex:
        # results = list(ex.map(direct_link, mirrors))
        results = list(ex.map(direct_link, post_url))
    return [r for r in results if r]
