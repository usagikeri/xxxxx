import requests
from bs4 import BeautifulSoup as bs
import subprocess
import shlex
import time
import random
import sys
import os

from settings import member, headers

args = sys.argv
member_name = member[args[1]]


def page_get(url):
    response = requests.get(url, headers=headers)
    soup = bs(response.content, 'lxml')
    pages = soup.findAll('div', attrs={'class': 'paginate'})
    return int([x.text.replace('\xa0', '') for x in pages[0].findAll('a')][-2])


def img_get(member_name, max_page):
    imgurl_list = []
    for i in range(1, max_page):
        url = 'http://blog.nogizaka46.com/{}/?p={}'.format(member_name, i)
        response = requests.get(url, headers=headers)
        soup = bs(response.content, 'lxml')
        imgurl_list += [i.attrs['src'] for i in soup.findAll('img') if i.attrs['src'].startswith('http://img.nogizaka46.com/blog')]
        time.sleep(0.5 + random.randint(1, 5)/10)

    return set(imgurl_list)


def dl_img(member_name, img_list):
    os.makedirs(member_name) 
    os.chdir(member_name)
    commnnd = 'wget ' + ' '.join(img_list)
    subprocess.call(shlex.split(commnnd))

def jpeg_renam(member_name):
    std, err = subprocess.Popen('pwd',stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    pwd = std.decode('utf-8').rstrip('\n').rsplit('/',1)[-1]
    if not pwd == member_name:
        os.chdir(member_name)
    file_list = os.listdir('.')

    for i in file_list:
        if not i.endswith(('.jpeg', 'png', 'gif')):
            x, y = i.rsplit('.', 1)
            os.rename(i, y+x)

if __name__ == '__main__':
    url = 'http://blog.nogizaka46.com/{}'.format(member_name)

    max_page = page_get(url)
    imgurl_list = img_get(member_name, max_page)
    dl_img(member_name, imgurl_list)
    jpeg_renam(member_name)
