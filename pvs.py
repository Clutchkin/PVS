# Importování knihoven
import os
import urllib.request
from bs4 import BeautifulSoup
import shutil
import time

"""
Vstupy a proměnné.
pathFrom: Kořenová cesta k DB
pathTo: Cesta k nové DB
pathToUnknown: Cesta k DB s neznámými soubory
"""
pathFrom = "C:\Python/Test/DB/"
pathTo = "C:\Python/Test/DB_nova/"
pathToUnknown = "C:\Python/Test/DB_nezname/"
pathToCopy = "C:\Python/Test/DB_copy/"
articleNumber = 0

"""
Funkce která redukuje obsah vybraného dokumentu (pageUrl).
Nejprve jsou odstraněny nesouvysející odkazy a následně separován nadpis a tělo zprávy.

Pravidla pro servery (datum platnosti):
    - BBC (29.1.2020)
    - The Guardian (30.1.2020)
"""


def getArticleReduction(pageUrl):
    # Vytvoření soup ze zadané cesty k souboru (pageUrl)
    page = urllib.request.urlopen('file:///' + str(pageUrl)).read()
    soup = BeautifulSoup(page, 'html.parser')

    """
    Funkce ukládání článků ze známých serverů
    - Potřebná znalost struktury kořenového adresáře a jeho podsložek
        -Na základě rozložení původní cesty upravujeme délku ke kořenovému adresáři

    TODO:
        -vytváření cest způsobem ověřování zda daná podsložka existuje/neexistuje a pripadne ji nově vytvořit
    """

    def saveKnownArticle(url, result, server):
        # Ukládání textu
        splitPath = os.path.normpath(url).split(
            os.path.sep)  # ['C:', 'Python', 'Test', 'DB', 'Afrika', '2018', '04-April', '2018-04-05_02-00-35_0011.html']
        # HTML tvorba cesty
        pathToFull = pathTo + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(
            splitPath[-1])
        pathToFullCopy = pathToCopy + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(
            splitPath[-2]) + "/" + str(splitPath[-1])
        # URL tvorba cesty
        urlPathToFull = pathTo + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(
            splitPath[-1]).replace('html', 'url')
        urlPathToFullCopy = pathToCopy + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(
            splitPath[-2]) + "/" + str(splitPath[-1]).replace('html', 'url')
        urlUrl = str(url).replace('html', 'url')

        # Report
        print("Server:" + server)
        print("From: " + str(url))
        print("To: " + pathToFull)
        print("From: " + str(urlUrl))
        print("To: " + urlPathToFull)
        print("-----------------------------------------------------------")

        # URL ukladani
        shutil.copy(urlUrl, urlPathToFullCopy)
        os.replace(urlUrl, urlPathToFull)
        # HTML ukladani
        with open(pathToFull, "w", encoding="utf-8") as f:
            f.write(result)
        shutil.copy(url, pathToFullCopy)
        os.remove(url)

    """
    Seznam pravidel pro jednotlivé servery

    TODO:
        -přídaní pravidel pro další servery
        -kontrola zda je zfomátovaný obsah není prázdný pro případ změny struktury stránek severu
    TODELETE:
        -print(splitPath)
        -print(splitPath[-4])
        -shutil
    """
    # BBC
    if str(soup.find("meta", property="og:site_name")).startswith('<meta content="BBC News'):
        # Mazání nadbytečných částí u všech dokumentů
        for link in soup.select("li.story-body__list-item > a"):
            # if not link.parent == None:
            if link.parent is not None:
                link.parent.decompose()
        for remove1 in soup.select("figure.media-landscape"):
            remove1.decompose()
        for remove2 in soup.select("div.player-with-placeholder__caption"):
            remove2.decompose()
        for remove3 in soup.select("span.off-screen"):
            remove3.decompose()
        for remove4 in soup.find_all("div", attrs={"class": "social-embed"}):
            remove4.decompose()
        for remove5 in soup.find_all("div", attrs={"class": "bbc-news-vj-embed-wrapper"}):
            remove5.decompose()
        for remove6 in soup.find_all("figure", attrs={"class": "media-with-caption"}):
            remove6.decompose()

        # Extrakce nadpistu a textu u textové novinky
        textHeadline = soup.find("h1", attrs={"class": "story-body__h1"})
        textBody = soup.find("div", attrs={"class": "story-body__inner"})

        # Extrakce nadpisu a textu u video novinky
        videoHeadline = soup.find("h1", attrs={"vxp-media__headline"})
        videoBody = soup.find("div", attrs={"vxp-media__summary"})

        # Formátování konečného textu rozdílné pro textové zprávy a pro video novinky
        if videoBody is None:
            reductionResult = str(textHeadline) + str(textBody)
        else:
            reductionResult = str(videoHeadline) + str(videoBody)

        # Ukládání textu
        saveKnownArticle(pageUrl, reductionResult, "BBC News")
    # The Guardian
    elif str(soup.find("meta", attrs={"name": "application-name"})).startswith('<meta content="The Guardian'):
        for link in soup.select("li > a"):
            # if not link.parent == None:
            if link.parent is not None:
                link.parent.decompose()
        # Mazání nadbytečných částí u všech dokumentů
        for remove1 in soup.find_all("figure", attrs={"class": "element-atom"}):
            remove1.decompose()
        for remove2 in soup.find_all("aside", attrs={"class": "element"}):
            remove2.decompose()
        for remove3 in soup.find_all("div", attrs={"class": "submeta"}):
            remove3.decompose()
        for remove4 in soup.find_all("figure", attrs={"class": "element"}):
            remove4.decompose()
        for remove5 in soup.find_all("div", attrs={"class": "idt2"}):
            remove5.decompose()

        # Extrakce nadpistu a textu u textové novinky
        textHeadline = soup.find("h1", attrs={"class": "content__headline"})
        textUnderline = soup.find("div", attrs={"class": "content__standfirst"})
        textBody = soup.find("div", attrs={"class": "content__article-body from-content-api js-article__body"})
        textGallery = str(" ")
        for i in soup.find_all("div", attrs={"class": "gallery__caption"}):
            textGallery += str(i)

        # Formátování konečného textu rozdílné pro textové zprávy a pro video novinky
        if textBody is not None:
            reductionResult = str(textHeadline) + str(textUnderline) + str(textBody)
        elif len(textGallery) > 1:
            reductionResult = str(textHeadline) + str(textUnderline) + str(textGallery)
        else:
            reductionResult = str(textHeadline) + str(textUnderline)

        # Ukládání textu
        saveKnownArticle(pageUrl, reductionResult, "The Guardian")
    # UN News
    elif str(soup.find("meta", property="og:site_name")).startswith('<meta content="UN News'):
        # Mazání nadbytečných částí u všech dokumentů
        for remove1 in soup.find_all("div", attrs={
            "class": "field field-name-field-news-topics field-type-entityreference field-label-hidden"}):
            remove1.decompose()

        # Extrakce nadpistu a textu u textové novinky
        textHeadline = soup.find("h1", attrs={"class": "story-title"})
        textBody = soup.find("div", attrs={"class": "content"})

        # Formátování konečného textu
        reductionResult = str(textHeadline) + str(textBody)

        # Ukládání textu
        saveKnownArticle(pageUrl, reductionResult, "UN news")
    # Neznámý server
    else:
        # Ukládání textu
        splitPath = os.path.normpath(pageUrl).split(os.path.sep)
        # HTML
        pathToFull = pathToUnknown + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(
            splitPath[-2]) + "/" + str(splitPath[-1])
        pathToFullCopy = pathToCopy + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(
            splitPath[-2]) + "/" + str(splitPath[-1])
        # URL
        urlPathToFull = pathToUnknown + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(
            splitPath[-2]) + "/" + str(splitPath[-1]).replace('html', 'url')
        urlPathToFullCopy = pathToCopy + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(
            splitPath[-2]) + "/" + str(splitPath[-1]).replace('html', 'url')
        urlUrl = str(pageUrl).replace('html', 'url')

        # Report
        print("Server: Uknown")
        print("From: " + str(pageUrl))
        print("To: " + str(pathToFull))
        print("From: " + str(urlUrl))
        print("To: " + urlPathToFull)
        print("-----------------------------------------------------------")

        shutil.copy(pageUrl, pathToFullCopy)
        os.replace(pageUrl, pathToFull)

        shutil.copy(urlUrl, urlPathToFullCopy)
        os.replace(urlUrl, urlPathToFull)


"""
Funkce která získá seznam veškerých souborů a souborů v podsložkách v zadaném adresáři (pathFrom).
Seznam je následně uložen v listu (allFiles) s kompletní cestou k souboru.
"""


def getListOfFiles(dirName):
    # Vytvoří list souborů and podsložek
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Prolistování všemi záznamy
    for entry in listOfFile:
        # Vytvoření kompletní cesty k souboru
        fullPath = os.path.join(dirName, entry)
        # Pokud je vstup složka poté získá list souborů a podsložek
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


"""
Smyčka finálního procesu, která rozpoznává zda je daná soubor formátu HTML/HTM a pokud ano provede proces redukce
(getArticleReduction). Pokud je soubor neznámeho formátu oznámí cestu k souboru, ale nemanipuluje s ním.
"""
while True:
    for i in getListOfFiles(pathFrom):
        # Podmínka zda je dokument (pathFrom) ve formátu .HTML/.HTM
        # Pokud "pravda" je aplikována funkce getArticleReduction
        if i.endswith('.html' or '.htm'):
            articleNumber += 1
            print("Article number: " + str(articleNumber))
            getArticleReduction(i)
        # Pokud soubor není html nebo url vytvoří cestu k souboru, ale neprobíhá manimupalace
        elif not i.endswith('.url'):
            print("File type: unknown")
            print("From: " + str(i))
            print("-----------------------------------------------------------")

    print("Task finished.")
    print("Number of articles: " + str(articleNumber))
    print("-----------------------------------------------------------")

    articleNumber = 0
    # time.sleep(5)
