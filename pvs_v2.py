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
pathToBackUp = "C:\Python/Test/DB_backup/"

backUp = True


"""
Funkce která redukuje obsah vybraného dokumentu (pageUrl).
Nejprve jsou odstraněny nesouvysející odkazy a následně separován nadpis a tělo zprávy.

Pravidla pro servery (datum platnosti):
    - BBC (29.1.2020)
    - The Guardian (30.1.2020)
"""
def getArticleReduction(pageUrl, dictUknown):
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
    def saveKnownArticle(url, result,server):
        # Rozložení cesty do list
        # ['C:', 'Python', 'Test', 'DB', 'Afrika', '2018', '04-April', '2018-04-05_02-00-35_0011.html']
        splitPath = os.path.normpath(url).split(os.path.sep) 
        # HTML tvorba cesty
        pathToFull = pathTo + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1])
        # URL tvorba cesty
        urlPathToFull = pathTo + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1]).replace('html', 'url')
        urlUrl = str(url).replace('html', 'url')

        # Report
        print("Server:" + server)
        print("From: " + str(url))
        print("To: " + pathToFull)
        print("From: " + str(urlUrl))
        print("To: " + urlPathToFull)
        if backUp == True:
            print("Backup: ON")
        else:
            print("Backup: OFF")
        print("-----------------------------------------------------------")

        # Zálohování pokud konstanta backUp == True
        if backUp == True:  
            pathToFullBackUp = pathToBackUp + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1])
            urlPathToFullBackUp = pathToBackUp + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1]).replace('html', 'url')
            shutil.copy(url, pathToFullBackUp)
            shutil.copy(urlUrl, urlPathToFullBackUp)
        # URL ukladani
        os.replace(urlUrl, urlPathToFull)
        # HTML ukladani
        with open(pathToFull, "w", encoding="utf-8") as f:
            f.write(result)
        os.remove(url)

    """
    Funkce ukládání článků z neznámých serverů
        
    TODO:
        -
    """    
    def saveUknownArticle(server):
        # Rozložení cesty do listu
        # ['C:', 'Python', 'Test', 'DB', 'Afrika', '2018', '04-April', '2018-04-05_02-00-35_0011.html']
        splitPath = os.path.normpath(pageUrl).split(os.path.sep)
        # HTML cesta
        pathToFull = pathToUnknown + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1])
        # URL cesta
        urlPathToFull = pathToUnknown + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1]).replace('html', 'url')
        urlUrl = str(pageUrl).replace('html', 'url')

        # Report
        print("Server: Uknown " + server)
        print("From: " + str(pageUrl))
        print("To: " + str(pathToFull))
        print("From: " + str(urlUrl))
        print("To: " + urlPathToFull)
        if backUp == True:
            print("Backup: ON")
        else:
            print("Backup: OFF")
        print("-----------------------------------------------------------")

        # Zálohování pokud konstanta backUp == True
        if backUp == True:  
            pathToFullBackUp = pathToBackUp + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1])
            urlPathToFullBackUp = pathToBackUp + str(splitPath[-4]) + "/" + str(splitPath[-3]) + "/" + str(splitPath[-2]) + "/" + str(splitPath[-1]).replace('html', 'url')
            shutil.copy(pageUrl, pathToFullBackUp)
            shutil.copy(urlUrl, urlPathToFullBackUp)
        # URL ukládání
        os.replace(pageUrl, pathToFull)
        # HTML ukládání
        os.replace(urlUrl, urlPathToFull)

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
    # BBC News
    if str(soup.find("meta", property="og:site_name")).startswith('<meta content="BBC News'):
        # Mazání nadbytečných částí u všech dokumentů
        for link in soup.select("li.story-body__list-item > a"):
            #if not link.parent == None:
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

        # Extrakce nadpisu (textové a video zprávy)
        textHeadline = soup.find("h1", attrs={"class": "story-body__h1"})
        if textHeadline is None:
            textHeadline = soup.find("h1", attrs={"vxp-media__headline"})
        # Extrakce obsahu zprávy (textové a video zprávy)
        textBody = soup.find("div", attrs={"class": "story-body__inner"})
        if textBody is None:
            textBody = soup.find("div", attrs={"vxp-media__summary"})
        # Formátování konečného textu
        reductionResult = str(textHeadline) + str(textBody)
        # Ukládání textu
        if textBody is not None:
            saveKnownArticle(pageUrl,reductionResult, "BBC News")
        else:
            saveUknownArticle("BBC News")
            dictOfUnknown["BBC News"] += 1

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

        # Extrakce nadpisu
        textHeadline = soup.find("h1", attrs={"class": "content__headline"})
        # Extrakce podnadpisu
        textUnderline = soup.find("div", attrs={"class": "content__standfirst"})
        # Extrakce obsahu zprávy
        textBody = soup.find("div", attrs={"class": "content__article-body from-content-api js-article__body"})
        if textBody is None:
            textBody = str(" ")
            for i in soup.find_all("div", attrs={"class": "gallery__caption"}):
                textBody += str(i)

        # Formátování konečného textu
        reductionResult = str(textHeadline) + str(textUnderline) + str(textBody)
        # Ukládání textu
        if str(textBody) != " " and textUnderline is not None:
            saveKnownArticle(pageUrl,reductionResult, "The Guardian")
        else:
            saveUknownArticle("The Guardian")
            dictOfUnknown["The Guardian"] += 1

    # UN News
    elif str(soup.find("meta", property="og:site_name")).startswith('<meta content="UN News'):
        # Mazání nadbytečných částí u všech dokumentů
        for remove1 in soup.find_all("div", attrs={"class": "field field-name-field-news-topics field-type-entityreference field-label-hidden"}):
            remove1.decompose()

        # Extrakce nadpistu a textu u textové novinky
        textHeadline = soup.find("h1", attrs={"class": "story-title"})
        textBody = soup.find("div", attrs={"class": "content"})
        # Formátování konečného textu
        reductionResult = str(textHeadline) + str(textBody)
        # Ukládání
        if textBody is not None:
            saveKnownArticle(pageUrl,reductionResult, "UN News")
        else:
            saveUknownArticle("UN news")
            dictOfUnknown["UN News"] += 1

    # Neznámý server
    else:
        saveUknownArticle("")

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
    articleNumber = 0
    dictOfUnknown = {
    "BBC News": 0,
    "The Guardian": 0,
    "UN News": 0
    }
    for i in getListOfFiles(pathFrom):
        # Podmínka zda je dokument (pathFrom) ve formátu .HTML/.HTM
        # Pokud "pravda" je aplikována funkce getArticleReduction
        if i.endswith('.html' or '.htm'):
            articleNumber += 1
            print("Article number: " + str(articleNumber))
            getArticleReduction(i,dictOfUnknown)
        # Pokud soubor není html nebo url vytvoří cestu k souboru, ale neprobíhá manimupalace
        elif not i.endswith('.url'):
            print("File type: unknown")
            print("From: " + str(i))
            print("-----------------------------------------------------------")

    print("Task finished.")
    print("Number of articles: " + str(articleNumber))
    print("Uknown formats from known sites")
    print("BBC News: " + str(dictOfUnknown["BBC News"]))
    print("The Guardian: " + str(dictOfUnknown["The Guardian"]))
    print("UN News: " + str(dictOfUnknown["UN News"]))
    print("-----------------------------------------------------------")

    time.sleep(60)
