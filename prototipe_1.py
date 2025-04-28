"""
fitgirl_direct_links.py
Author : Me
Python ≥ 3.10     pip install selenium undetected-chromedriver bs4 requests fake-useragent
Notes: Este prototipo funciona en parcialmente, hay que introducir la lista de enlaces manualmente
"""

from __future__ import annotations
import re, time, pathlib, contextlib
import requests, bs4
from fake_useragent import UserAgent

# ---------- small helpers ----------------------------------------------------
UA = UserAgent().chrome
HD = {"User-Agent": UA, "Referer": "https://fitgirl-repacks.site/"}
RX_JS_URL = re.compile(r'window\.open\(\s*["\']([^"\']+)["\']')  # grabs url in download()


def soup(url: str) -> bs4.BeautifulSoup:
    html = requests.get(url, headers=HD, timeout=30).text
    return bs4.BeautifulSoup(html, "html.parser")


# ---------- STEP-1 & 2 – FitGirl page ----------------------------------------
def get_mirror_pages(fg_url: str) -> list[str]:
    """Return every ‘mirror-page’ (e.g. fuckingfast.co / datanodes.cc …)."""
    page = soup(fg_url)
    mirrors: list[str] = []

    # The mirrors live inside every <a class="external" …> that sits below the
    # h3 “Download Mirrors (Direct Links)” list.  The markup is consistent on
    # every post (see result snippet) :contentReference[oaicite:0]{index=0}
    for h3 in page.select("h3"):
        if h3.get_text(strip=True).startswith("Download Mirrors (Direct Links)"):
            ul = h3.find_next("ul")
            if not ul:
                continue
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

# def get_mirror_pages():
#     mirrors = [
#         "https://fuckingfast.co/oclwwdxrbu7n#9-Bit_Armies_A_Bit_Too_Far_--_fitgirl-repacks.site_--_.part1.rar",
#         "https://fuckingfast.co/cpz8d3inbozt#9-Bit_Armies_A_Bit_Too_Far_--_fitgirl-repacks.site_--_.part2.rar",
#         "https://fuckingfast.co/gfaupe2iyx66#9-Bit_Armies_A_Bit_Too_Far_--_fitgirl-repacks.site_--_.part3.rar",
#         "https://fuckingfast.co/m70bei3gh874#9-Bit_Armies_A_Bit_Too_Far_--_fitgirl-repacks.site_--_.part4.rar",
#         "https://fuckingfast.co/m2uolu4yhtd6#9-Bit_Armies_A_Bit_Too_Far_--_fitgirl-repacks.site_--_.part5.rar",
#     ]
#     return mirrors


# ---------- STEP-3 – mirror page -> real link --------------------------------
def real_link(mirror_url: str) -> str | None:
    """Extract the *first* real file URL hidden in the JS download() fn."""
    try:
        s = soup(mirror_url)  # Cloudflare blocks? retry via Selenium
        print("s: ")
        print(s)
        js = s.find_all("script")[-2].string or ""
        print("js: ")
        print(js)
        m = RX_JS_URL.search(js)
        print("m: ")
        print(m)
        return m.group(1) if m else None
    except Exception as exc:  # you may want proper logging here
        print(f"[warn] {mirror_url} – {exc}")
        return None


# ---------- public façade -----------------------------------------------------
def fitgirl_direct_links(fg_post_url: str) -> list[str]:
    mirrors = get_mirror_pages(fg_post_url)
    # mirrors = get_mirror_pages()
    print(f"found {len(mirrors)} mirror pages")
    links = filter(None, (real_link(u) for u in mirrors), )
    return list(dict.fromkeys(links))  # de-dupe, preserve order


# ---------- demo --------------------------------------------------------------
if __name__ == "__main__":
    # url = "https://fitgirl-repacks.site/the-elder-scrolls-iv-oblivion-remastered/"
    url = "https://fitgirl-repacks.site/9-bit-armies-a-bit-too-far/"
    for link in fitgirl_direct_links(url):
        print(link)

# TODO: Estudiarme como bypasear la proteccion de cloudflare con selenium
