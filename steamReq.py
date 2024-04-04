import aiohttp
import asyncio
from bs4 import BeautifulSoup

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


async def getLinksFromSteam(name, cookies):
    name = name.replace(' ', '+')
    allLinks = []
    links, nLinks = await getLinksFromSteamFirst(name, cookies)
    allLinks += links
    aioTasks = []
    for page in range(2, nLinks // 20 + 2):
        aioTasks.append(asyncio.create_task(getLinksFromSteamPage(name, page, cookies)))
    for links in await asyncio.gather(*aioTasks):
        allLinks += links
    return allLinks


async def getLinksFromSteamPage(name, page, cookies):
    sessionId = cookies['sessionid']
    async with aiohttp.ClientSession(cookies=cookies) as session:
        resp = await session.get(
            f'https://steamcommunity.com/search/SearchCommunityAjax?text={name}&filter=users&sessionid={sessionId}&steamid_user=false&page={page}')
        jsn = await resp.json()
        html = jsn['html']
        soup = BeautifulSoup(html, features='lxml')
        r = []
        for a in soup.find_all(class_="searchPersonaName"):
            r.append(a['href'])
        return r


async def getLinksFromSteamFirst(name, cookies):
    sessionId = cookies['sessionid']
    async with aiohttp.ClientSession(cookies=cookies) as session:
        resp = await session.get(
            f'https://steamcommunity.com/search/SearchCommunityAjax?text={name}&filter=users&sessionid={sessionId}&steamid_user=false&page=1')
        jsn = await resp.json()
        html = jsn['html']
        soup = BeautifulSoup(html, features='lxml')
        r = []
        for a in soup.find_all(class_="searchPersonaName"):
            r.append(a['href'])
        return r, jsn['search_result_count']


async def getDataFromSteam(url, i=0):
    data = [url]
    nicks = []
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            page = await resp.text()
            # with open('temp.html', 'w', encoding='utf-8') as f:
            #     f.write(page)
            soup = BeautifulSoup(page, features="lxml")
            try:
                try:
                    data.append(
                        soup.find(class_="profile_summary").text.replace('\n', '').replace('\t', '').replace('\r', ''))
                    nc = soup.find(class_="header_real_name ellipsis")
                    name = nc.find(name='bdi').text
                    nc.bdi.decompose()
                    loc = nc.text.replace('	', '').replace(' ', '').replace('\n', '').replace('\xa0', '').replace(
                        '\r', '')
                    data.append(loc)
                    data.append(name)
                except:
                    data = [url]
                    if soup.find(class_="profile_private_info"):
                        data.append('!!! Профиль скрыт')
                        data += ['', '']
                    else:
                        data.append('!!! Произошла неожиданная ошибка')
                        data += ['', '']
                resp = await session.get(url + '/ajaxaliases')
                for j in await resp.json():
                    nicks.append(j['newname'])
            except:
                data = [url]
                if soup.find(id="message").find(name='h3').text == 'The specified profile could not be found.':
                    data.append('!!! Произошла ошибка на стороне Steam')
                    data.append('Профиль не найден')
                    data.append('')
                else:
                    data.append('!!! Произошла неожиданная ошибка')
                    data += ['', '']
        while len(nicks) < 10:
            nicks.append('')
        return data + nicks
    except Exception as err:
        if i < 3:
            return await getDataFromSteam(url, i + 1)
        else:
            data = [url]
            data.append('!!! Произошла ошибка')
            data.append(str(err))
            data += ['', '', '', '', '', '', '', '', '', '', '']
            return data


async def getDataByNick(name):
    cookies = await getSessionId()
    links = await getLinksFromSteam(name, cookies)
    allData = []
    aioTasks = []
    for l in links:
        aioTasks.append(asyncio.create_task(getDataFromSteam(l)))
    for prof in await asyncio.gather(*aioTasks):
        allData.append(prof)
    return allData


if __name__ == "__main__":
    allData = asyncio.run(getDataByNick('Тут ник'))
    for data in allData:
        print(data)
