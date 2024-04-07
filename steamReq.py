import aiohttp
import asyncio
from bs4 import BeautifulSoup
import export

new_list = [['first', 'second'], ['third', 'four'], [1, 2, 3, 4, 5, 6]]


async def getSessionId():
    async with aiohttp.ClientSession() as session:
        resp = await session.get('https://steamcommunity.com/')
        r = resp.headers['set-cookie']
        cookie = {}
        for st in r.split(' ')[:1]:
            st = st.replace(';', '').split('=')
            if len(st) != 2:
                continue
            cookie[st[0]] = st[1]
        return cookie


async def getLinksFromSteam(name, cookies, match=0):
    links, nLinks = await getLinksFromSteamPage(name, 1, cookies, match=match)
    aioTasks = []
    aioTasks.append(getDataByLinks(links, name))
    for page in range(2, nLinks // 20 + 2):
        aioTasks.append(asyncio.create_task(getLinksFromSteamPage(name, page, cookies, match=match)))
    await asyncio.gather(*aioTasks)
    return nLinks


async def getLinksFromSteamPage(name, page, cookies, match=0):
    sessionId = cookies['sessionid']
    async with aiohttp.ClientSession(cookies=cookies) as session:
        lname = name.replace("+", "\\\\+").replace(" ", "+")
        resp = await session.get(
            f'https://steamcommunity.com/search/SearchCommunityAjax?text={lname}&filter=users&sessionid={sessionId}&steamid_user=false&page={page}')
        jsn = await resp.json()
        html = jsn['html']
        soup = BeautifulSoup(html, features='lxml')
        links = []
        for a in soup.find_all(class_="searchPersonaName"):
            if match == 0 or match == 1 and a.text.lower() == name.lower() or match == 2 and a.text == name:
                links.append(a['href'])
        if page != 1:
            await getDataByLinks(links, name)
        return links, jsn['search_result_count']


async def getPageFromSteam(url, i=0):
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            page = await resp.text()
        return page
    except Exception as err:
        if i < 3:
            return await getPageFromSteam(url, i + 1)
        else:
            print('error: getPageFromSteam ', url)
            print(err)
            return False


async def getNicksFromSteam(url, i=0):
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url + '/ajaxaliases')
            if '<!DOCTYPE html>' in await resp.text():
                return True
            jsn = await resp.json()
            jsn = await resp.json()
            return jsn
    except Exception as err:
        if i < 3:
            return await getNicksFromSteam(url, i + 1)
        else:
            print('error: getNicksFromSteam ', url)
            print(err)
            return False


async def getDataFromSteam(url, fName):
    print(url)
    data = [url]
    nicks = []
    page = await getPageFromSteam(url)
    soup = BeautifulSoup(page, features="lxml")
    if soup.find(id="message"):
        if soup.find(id="message").find(name='h3').text == 'The specified profile could not be found.':
            data.append('!!! Произошла ошибка на стороне Steam')
            data.append('Профиль не найден')
            data.append('')
    elif soup.find(class_="profile_private_info"):
        data.append('!!! Профиль скрыт')
        data += ['', '']
        jsn = await getNicksFromSteam(url)
        for j in jsn:
            nicks.append(j['newname'])
        while len(nicks) < 10:
            nicks.append('')
    else:
        data.append(
            soup.find(class_="profile_summary").text.replace('\n', '').replace('\t', '').replace('\r', ''))
        nc = soup.find(class_="header_real_name ellipsis")
        name = nc.find(name='bdi').text
        nc.bdi.decompose()
        loc = nc.text.replace('	', '').replace(' ', '').replace('\n', '').replace('\xa0', '').replace(
            '\r', '')
        data.append(loc)
        data.append(name)
        jsn = await getNicksFromSteam(url)
        for j in jsn:
            nicks.append(j['newname'])
        while len(nicks) < 10:
            nicks.append('')
    toTable = data + nicks
    export.toExcel(toTable, fName)
    return True


async def getPagesByLinks(links):
    aioTasks = []
    while True:
        for l in links:
            aioTasks.append(asyncio.create_task(getPageFromSteam(l)))
        check = await asyncio.gather(*aioTasks)
        if all(check):
            break
        else:
            for i in range(len(check) - 1, -1, -1):
                if not (check[i]):
                    links.pop(i)
    return True


async def getNicksByLinks(links):
    aioTasks = []
    while True:
        for l in links:
            aioTasks.append(asyncio.create_task(getNicksFromSteam(l)))
        check = await asyncio.gather(*aioTasks)
        if all(check):
            break
        else:
            for i in range(len(check) - 1, -1, -1):
                if not (check[i]):
                    print(i)
                    links.pop(i)
    return True


async def getDataByLinks(links, name):
    print(links)
    for l in links:
        await getDataFromSteam(l, name)
    return True
