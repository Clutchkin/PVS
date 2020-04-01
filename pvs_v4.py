# Importování knihoven
import os
import urllib.request
from bs4 import BeautifulSoup
import shutil
import time
from tkinter import *
from win32_setctime import setctime
#pip install win32-setctime

"""
if os.path.exists(path):

os.path.isdir(path)
os.mkdir(path)

os.path.isfile(path)
"""

"""
Vstupy a proměnné.
pathFrom: Kořenová cesta k DB
pathTo: Cesta k nové DB
pathToUnknown: Cesta k DB s neznámými soubory
pathToBackUp: Cesta k zaloze všech souborů
listOfUknownFilePaths: cesta k txt souboru se záznami cest neznámých souborů ze známých severů

backUp = True / False

datum vzniku uložit do nového souboru
"""
pathFrom = "C:\Python\Test\Zdroj"

pathTo = "C:\Python\Test\Zdroj_redukovany"
pathToUnknown = "C:\Python\Test\Zdroj_neznamy"
pathToBackUp = "C:\Python\Test\Zdroj_zaloha"

listOfUknownFilePaths = "C:\Python\Test\list.txt"

backUp = True


"""
Funkce která redukuje obsah vybraného dokumentu (pageUrl).
Nejprve jsou odstraněny nesouvysející odkazy a následně separován nadpis a tělo zprávy.

Pravidla pro servery (datum platnosti):
    - BBC (29.1.2020)
    - The Guardian (30.1.2020)
"""
def getArticleReduction(pageUrl, dictUnknown, pathToUnknownList):
    # Vytvoření soup ze zadané cesty k souboru (pageUrl)
    page = urllib.request.urlopen('file:///' + str(pageUrl)).read()
    soup = BeautifulSoup(page, 'html.parser')

    """
        Funkce ověřující existenci složek a podsložek do kterých se ukládájí dokumenty
        TODO:
            -
    """
    def checkIsDir(corePath, splitPath):
        if os.path.isdir(corePath) == False:
            os.mkdir(corePath)
        if os.path.isdir(corePath + "\\" + str(splitPath[-4])) == False:
            os.mkdir(corePath + "\\" + str(splitPath[-4]))
        if os.path.isdir(corePath + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3])) == False:
            os.mkdir(corePath + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3]))
        if os.path.isdir(corePath + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3]) + "\\" + str(splitPath[-2])) == False:
            os.mkdir(corePath + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3]) + "\\" + str(splitPath[-2]))

    """
    Funkce ukládání článků ze známých serverů
    - Potřebná znalost struktury kořenového adresáře a jeho podsložek
        -Na základě rozložení původní cesty upravujeme délku ke kořenovému adresáři
        
    TODO:
        -vytváření cest způsobem ověřování zda daná podsložka existuje/neexistuje a pripadne ji nově vytvořit
    """
    def saveArticle(pathTo, result, server, known):
        # Rozložení cesty do list
        # ['C:', 'Python', 'Test', 'DB', 'Afrika', '2018', '04-April', '2018-04-05_02-00-35_0011.html']
        splitPath = os.path.normpath(pageUrl).split(os.path.sep)
        checkIsDir(pathTo,splitPath)
        # HTML tvorba cesty
        pathToFull = pathTo + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3]) + "\\" + str(splitPath[-2]) + "\\" + str(splitPath[-1])
        # URL tvorba cesty
        urlPathToFull = pathTo + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3]) + "\\" + str(splitPath[-2]) + "\\" + str(splitPath[-1]).replace('html', 'url')
        urlUrl = str(pageUrl).replace('html', 'url')
        # Uložení data vzniku souboru
        fileCreationTime = os.path.getctime(pageUrl)
        fileCreationTimeUrl = os.path.getctime(urlUrl)

        # Report
        print("Server: " + server)
        print("From: " + str(pageUrl))
        print("To: " + pathToFull)
        print("From: " + str(urlUrl))
        print("To: " + urlPathToFull)
        if backUp == True:
            print("Backup: ON")
        else:
            print("Backup: OFF")
        print("-----------------------------------------------------------")
        
        # Zálohování pokud konstanta backUp == True
        if backUp:  
            checkIsDir(pathToBackUp,splitPath)
            pathToFullBackUp = pathToBackUp + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3]) + "\\" + str(splitPath[-2]) + "\\" + str(splitPath[-1])
            urlPathToFullBackUp = pathToBackUp + "\\" + str(splitPath[-4]) + "\\" + str(splitPath[-3]) + "\\" + str(splitPath[-2]) + "\\" + str(splitPath[-1]).replace('html', 'url')
            shutil.copy(pageUrl, pathToFullBackUp)
            shutil.copy(urlUrl, urlPathToFullBackUp)
            setctime(pathToFullBackUp, fileCreationTime)
            setctime(urlPathToFullBackUp, fileCreationTimeUrl)
        # Ukládání HTML a URL
        if known:
            os.replace(urlUrl, urlPathToFull)
            with open(pathToFull, "w", encoding="utf-8") as x:
                x.write(result)
            os.remove(pageUrl)
        else:
            os.replace(pageUrl, pathToFull)
            os.replace(urlUrl, urlPathToFull)
        # Změna datumu vytvoření, upravení a otevření u nově vytvořených souborů
        setctime(pathToFull, fileCreationTime)
        setctime(urlPathToFull, fileCreationTimeUrl)
        os.utime(pathToFull, (fileCreationTime, fileCreationTime))
        os.utime(urlPathToFull, (fileCreationTimeUrl, fileCreationTimeUrl))

    """
    Funkce ukládání cesty souborů ze známých serverů, ale s neznámým obsahem, do textového souboru
        
    TODO:
        -
    """   
    def savePathOfUnknown():
        f=open(pathToUnknownList, "a+")
        f.write(pageUrl + "\n")

    """
    Seznam pravidel pro jednotlivé servery
    
    TODO:
        -přídaní pravidel pro další servery
        *kontrola zda je zfomátovaný obsah není prázdný pro případ změny struktury stránek severu
    TODELETE:
        -
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
        title = soup.find('title')
        reductionResult = "<html>" + str(title) + "<head></head><body>" + str(textHeadline) + str(textBody) + "</body></html>"
        # Ukládání textu
        if textBody is not None:
            saveArticle(pathTo ,reductionResult, "BBC News", known=True ) #(pathTo, result, server, known):
        else:
            saveArticle(pathToUnknown ,reductionResult, "BBC News (unknown)", known=False )
            dictUnknown["BBC News"] += 1
            savePathOfUnknown()

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
        title = soup.find('title')
        reductionResult = "<html>" + str(title) + "<head></head><body>" + str(textHeadline) + str(textUnderline) + str(textBody) + "</body></html>"
        # Ukládání textu
        # ***
        if textUnderline is not None:    
            saveArticle(pathTo ,reductionResult, "The Guardian", known=True ) #(pathTo, result, server, known):
        elif len(textBody) > 5:
            saveArticle(pathTo ,reductionResult, "The Guardian", known=True )
        else:
            saveArticle(pathToUnknown ,reductionResult, "The Guardian (unknown)", known=False )
            dictUnknown["The Guardian"] += 1
            savePathOfUnknown()

    # UN News
    elif str(soup.find("meta", property="og:site_name")).startswith('<meta content="UN News'):
        # Mazání nadbytečných částí u všech dokumentů
        for remove1 in soup.find_all("div", attrs={"class": "field field-name-field-news-topics field-type-entityreference field-label-hidden"}):
            remove1.decompose()

        # Extrakce nadpistu a textu u textové novinky
        textHeadline = soup.find("h1", attrs={"class": "story-title"})
        textBody = soup.find("div", attrs={"class": "content"})
        # Formátování konečného textu
        title = soup.find('title')
        reductionResult = "<html>" + str(title) + "<head></head><body>" + str(textHeadline) + str(textBody) + "</body></html>"
        # Ukládání
        if textBody is not None:
            saveArticle(pathTo ,reductionResult, "UN news", known=True ) #(pathTo, result, server, known):
        else:
            saveArticle(pathToUnknown ,reductionResult, "UN news (unknown)", known=False )
            dictUnknown["UN News"] += 1
            savePathOfUnknown()

    # Neznámý server
    else:
        saveArticle(pathToUnknown ,"", "Unknown", known=False )

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
Funkce tkinter pro uložení cest z rohraní a spuštění smyčky změnou proměnné isRunning z False na True.
"""
def setPaths():
    global pathFrom
    global pathTo
    global pathToUnknown
    global pathToBackUp
    global backUp
    global isRunning
    global r
    pathFrom = e1.get()
    pathTo = e2.get()
    pathToUnknown = e3.get()
    pathToBackUp = e4.get()


    isRunning = True
    r.destroy()

"""
Smyčka finálního procesu, která rozpoznává zda je daná soubor formátu HTML/HTM a pokud ano provede proces redukce
(getArticleReduction). Pokud je soubor neznámeho formátu oznámí cestu k souboru, ale nemanipuluje s ním.
"""

r = Tk()
r.geometry('800x150')
r.configure(bg="red")
r.title('Reduction')
button = Button(r, text='Start',command=lambda *args: setPaths(),width="80")
button.grid(row=6, column=1)

Label(r, text='Path from:').grid(row=0,column=0)
Label(r, text='Path to:').grid(row=1,column=0)
Label(r, text='Path to (unknown):').grid(row=2,column=0)
Label(r, text='Path to (back up:)').grid(row=3,column=0)
Label(r, text='Backup YES(1)/NO(0):').grid(row=4,column=0)

e1 = Entry(r, textvariable=StringVar(r, value=pathFrom),width="100")
e2 = Entry(r, textvariable=StringVar(r, value=pathTo),width="100")
e3 = Entry(r, textvariable=StringVar(r, value=pathToUnknown),width="100")
e4 = Entry(r, textvariable=StringVar(r, value=pathToBackUp),width="100")

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e3.grid(row=2, column=1)
e4.grid(row=3, column=1)

isRunning = False
r.mainloop()

while isRunning:
    articleNumber = 0
    dictOfUnknown = {
    "BBC News": 0,
    "The Guardian": 0,
    "UN News": 0
    }
    listOfLoadedFiles = getListOfFiles(pathFrom)
    for i in listOfLoadedFiles:
        # Podmínka zda je dokument (pathFrom) ve formátu .HTML/.HTM
        # Pokud "pravda" je aplikována funkce getArticleReduction
        if i.endswith('.html' or '.htm'):
            articleNumber += 1
            percentCompleted = articleNumber / (len(listOfLoadedFiles)/2) * 100
            print("Article number: " + str(articleNumber) + "/" + str(format((len(listOfLoadedFiles)/2), '.0f')) + " (" + format(percentCompleted, '.2f') + " %)")
            getArticleReduction(i, dictOfUnknown, listOfUknownFilePaths)
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
    f=open(listOfUknownFilePaths, "a+")
    f.write("-----------------------------------------------------------")
    time.sleep(60)
