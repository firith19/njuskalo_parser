# -*- coding: utf-8 -*-
import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
import send_gmail


# loads dictionary from a file
def loadDictionaryFromFile(filename):
    if not os.path.exists(filename):
        f = open(filename, "w+")
    if os.stat(filename).st_size == 0:
        return {}
    with open(filename) as json_file:
        json_data = json.load(json_file)
    return json.loads(json_data)


# saves dictionary to a file
def saveDictionaryToAFile(filename, dictToSave):
    with open(filename, 'w') as outfile:
        json_data = json.dumps(dictToSave, ensure_ascii=False)
        json.dump(json_data, outfile)


# saves the page content (string) to a file, overwrites previous content
def saveToFile(page_content, filename):
    with open(filename, 'w') as file:
        file.write(page_content)


# check if the response contains captcha
def checkIfCaptcha(file):
    with open('njuskalo_content', 'r') as file:
        for line in file:
            if "captcha" in line:
                return True
        return False


# request the page and parse it with a relevant function
def genericRequestPageAndParseIt(url, dict, checkRelevantContentFunction, parseFunction):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    #s = requests.session()
    #s.config['keep_alive'] = False

    # request the page
    r = requests.get(url, headers=headers)

    # save the content to a file
    saveToFile(r.content, 'njuskalo_content')

    if(checkIfCaptcha(file)):
        print("Captcha again!")
    else:
        #print("Finally, a good response!")
        if (checkRelevantContentFunction(r.iter_lines())):
            dict.update(parseFunction(r.iter_lines()))
            return True
        else:
            return False


# sends email notification
def newAdsSendEmailNotification(src_address, dest_address, dNew):
    print("## Set up server...")
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        #print("## Start TLS...")
        #server.starttls()
    except:
        print 'Something went wrong...'
    print("## Login...")
    #server.login('dinko.matkovic@gmail.com', 'AksssUcA2010')
    server.login(src_address, 'AksssUcA2010')
    print("## Set up message...")
    msg = "Novi oglasi na Njuškalu!"
    msg_text = ''
    for link in dNew.values():
        msg_text += 'https://www.njuskalo.hr' + link + '\n'
    print("## Attach message...")
    msg.attach(MIMEText(msg_text, 'plain'))
    print("## Send email...")
    #server.sendmail('dinko.matkovic@gmail.com', 'dinko.matkovic@gmail.com', msg)
    server.sendmail(src_address, dest_address, msg)
    server.quit()


# check if there is content in this page
def newAdsPageContainsRelevantContent(content):
    for line in content:
        if "Njuškalo oglasi" in line:
            return True
    return False


# new ads -> find relevant content in the page
def newAdsParsePageGetRelevantContent(content):

    # flag that defines the iterator is inside wanted content
    inside_wanted_content = False
    # wanted content dictionary
    dWanted_content = {}

    for line in content:
        if "Njuškalo oglasi" in line and not "Vau Vau Njuškalo oglasi" in line:
            inside_wanted_content = True
            continue
        if "h3 class=\"block-standard-title\"" in line and "Istaknute novogradnje" in line:
            inside_wanted_content = False
        if inside_wanted_content:
            if "h3 class=\"entity-title\"" in line and "a name" in line and "nekretnine" in line:
                key = line.split("a name=\"")[1].split("\"")[0]
                value = line.split("href=\"")[1].split("\"")[0]
                dWanted_content[key] = value

    #print dWanted_content
    return dWanted_content


# scrapes main njuskalo page by url, saves new ads to json file and emails the file
def newAdsGetAll(main_url, json_filename):
    # load the existing dictionary from the file
    dWantedAds = loadDictionaryFromFile(json_filename)
    dOldWantedAds = loadDictionaryFromFile(json_filename)
    print(dWantedAds)
    # request and parse the first page
    genericRequestPageAndParseIt(main_url, dWantedAds, newAdsPageContainsRelevantContent, newAdsParsePageGetRelevantContent)
    # request and parse the other pages
    for i in range(2,1000):
        new_url = main_url + '&page=' + str(i)
        print(new_url)
        # if this page has content, the function returns True
        if not genericRequestPageAndParseIt(new_url, dWantedAds, newAdsPageContainsRelevantContent, newAdsParsePageGetRelevantContent):
            print("This is the end...")
            break
    print(dWantedAds)
    # find new ads
    dNewAds = {k:v for k,v in dWantedAds.items() if k not in dOldWantedAds}
    # TODO maknuti stare, neaktivne oglase iz postojeceg dictionarya
    print(dNewAds)
    if any(dNewAds):
        print("Sending email...")
        msgHtml = ''
        msgPlain = ''
        for k,v in dNewAds.items():
            msgHtml += 'https://www.njuskalo.hr' + v + '<br/>'
            msgPlain += 'https://www.njuskalo.hr' + v + '\n'
        print msgHtml
        print msgPlain
        send_gmail.SendMessage('dinko.matkovic@gmail.com',
                               'dinko.matkovic@gmail.com',
                               'Novi oglasi na Njuskalu -> ' + json_filename,
                               msgHtml,
                               msgPlain)
        '''
        send_gmail.SendMessage('dinko.matkovic@gmail.com',
                        'julija.vuljanko@gmail.com',
                       'Novi oglasi na Njuskalu -> ' + json_filename,
                       msgHtml,
                       msgPlain)
        '''
    # save the existing dictionary to a file
    saveDictionaryToAFile(json_filename, dWantedAds)

# request the page and parse it with a relevant function
def pricesRequestPageAndParseIt(id, url, dict, dictNew, checkRelevantContentFunction, parseFunction):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    #s = requests.session()
    #s.config['keep_alive'] = False

    # request the page
    r = requests.get(url, headers=headers)
    print(r.status_code)

    # save the content to a file
    saveToFile(r.content, 'njuskalo_content')

    if(checkIfCaptcha(file)):
        print("Captcha again!")
    else:
        #print("Finally, a good response!")
        if (checkRelevantContentFunction(r.iter_lines())):
            print('Usao u pricesParsePageGetRelevantContent za ' + url)
            parseFunction(r.iter_lines(), dict, dictNew, id, url)
            print('Izasao iz u pricesParsePageGetRelevantContent!')
            return True
        else:
            return False

# prices -> checks if this is the page has the relevant content
def pricesPageContainsRelevantContent(content):
    for line in content:
        if "Šifra oglasa" in line:
            return True
        return False

# prices -> parses ad to get the price in EUR
def pricesParsePageGetRelevantContent(content, dict, dictNew, id, url):
    price = 0.0
    for line in content:
        if "<span class=\"currency\">€</span>" in line:
            print("### " + line)
            price = line.split("<span class")[0]
            print("##### " + price)
            # check the current price in the dictionary
            oldPrice = dict.get(id)
            print("##### " + oldPrice)
            # if there is no entry, add it
            if oldPrice is None:
                dict[id] = price
            # if there is an entry, add difference to new dictionary and update the entry
            else:
                if oldPrice > price:
                    print(id + ' -> Cijena je pala s ' + oldPrice + '€ na ' + price + '€ !')
                    dictNew[url] = 'Cijena je pala s ' + oldPrice + '€ na ' + price + '€ !'
                else:
                    dictNew[url] = 'Cijena je porasla s ' + oldPrice + '€ na ' + price + '€ !'
                    print(id + ' -> Cijena je porasla s ' + oldPrice + '€ na ' + price + '€ !')
                dict[id] = price

# prices -> gets ad price from url
def pricesGetAdPrice(id, url, dAdPrices, dChangedPrices):
    #print("Usao u pricesRequestPageAndParseIt za " + url)
    pricesRequestPageAndParseIt(id, url, dAdPrices, dChangedPrices, pricesPageContainsRelevantContent, pricesParsePageGetRelevantContent)
    #print("Izasao iz pricesRequestPageAndParseIt!")


# prices -> checks for price changes for the file in the another corresponding _prices file and emails the differences
def pricesGetAll(json_filename):
    dAds = loadDictionaryFromFile(json_filename)
    dAdPrices = loadDictionaryFromFile(json_filename + '_prices')
    dChangedPrices = {}

    # iterate through items and check all prices
    for key,value in dAds.items():
        print('https://www.njuskalo.hr' + value)
        pricesGetAdPrice(key, 'https://www.njuskalo.hr' + value + '\n', dAdPrices, dChangedPrices)

    # save dictionary to the file
    saveDictionaryToAFile(json_filename + '_prices', dAdPrices)

    # email the changes in price
    if any(dChangedPrices):
        print("Sending email for changes prices...")
        msgHtml = ''
        msgPlain = ''
        for k,v in dChangedPrices.items():
            msgHtml += k + ' -> ' + v + '<br/>'
            msgPlain += k + ' -> ' + v + '\n'
        print msgHtml
        print msgPlain
        send_gmail.SendMessage('dinko.matkovic@gmail.com',
                               'dinko.matkovic@gmail.com',
                               'Promjena cijena na Njuškalu -> ' + json_filename,
                               msgHtml,
                               msgPlain)

### MAIN ###

# kuce 50k do 200k
newAdsGetAll('https://www.njuskalo.hr/prodaja-kuca/zagreb?price%5Bmin%5D=50000&price%5Bmax%5D=200000&adsWithImages=1', 'kuce_zg_50k_200k')
# zemljista 20k do 50k
newAdsGetAll('https://www.njuskalo.hr/prodaja-zemljista/zagreb?price%5Bmin%5D=20000&price%5Bmax%5D=50000&landTypeId=235', 'zemljista_zg_20k_50k')
# zemljista 50k do 100k
newAdsGetAll('https://www.njuskalo.hr/prodaja-zemljista/zagreb?price%5Bmin%5D=50000&price%5Bmax%5D=100000&landTypeId=235', 'zemljista_zg_50k_100k')
# stanovi 50k do 200k
newAdsGetAll('https://www.njuskalo.hr/prodaja-stanova/zagreb?price%5Bmin%5D=50000&price%5Bmax%5D=200000&mainArea%5Bmin%5D=80&mainArea%5Bmax%5D=150&adsWithImages=1','stanovi_zg_50k_200k')
# stanovi novogradnja 50k do 250k
newAdsGetAll('https://www.njuskalo.hr/prodaja-stanova/zagreb?price%5Bmin%5D=50000&price%5Bmax%5D=250000&mainArea%5Bmin%5D=80&mainArea%5Bmax%5D=150&adsWithImages=1&buildingInfo%5Bnew-building%5D=1','stanovi_novogradnja_zg_50k_250k')

#pricesGetAll('zemljista_zg_50k_100k')