import requests
from bs4 import BeautifulSoup as bs
import subprocess
import string
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
        imgurl_list += [i.attrs['src'] for i in soup.findAll('img')
                        if i.attrs['src'].startswith(
                                'http://img.nogizaka46.com/blog')]
        time.sleep(0.5 + random.randint(1, 5)/10)

    return set(imgurl_list)


def dl_img(member_name, img_list):
    os.makedirs(member_name, exist_ok=True)
    os.chdir(member_name)

    print('Downloading...')
    for img in img_list:
        res = requests.get(img, stream=True)
        if res.status_code == 200:
            orgname = img.split('/')[-1]
            random_string = generate_random_string() + '_'
            while os.path.exists(random_string + orgname):
                random_string = generate_random_string() + '_'

            filename = random_string + orgname
            with open(filename, 'wb') as f:
                f.write(res.content)
        else:
            print('Error occurred while downloading image from {}'.format(img),
                  file=sys.stderr)
    print('Complete')


def jpeg_renam(member_name):
    std, err = subprocess.Popen('pwd', stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE).communicate()
    pwd = std.decode('utf-8').rstrip('\n').rsplit('/', 1)[-1]
    if not pwd == member_name:
        os.chdir(member_name)
    file_list = os.listdir('.')

    for i in file_list:
        if not i.endswith(('.jpeg', 'png', 'gif')):
            x, y = i.rsplit('.', 1)
            os.rename(i, y+x)


def generate_random_string():
    source_char = string.ascii_lowercase + string.digits
    length = 30
    random_string = ''.join([random.choice(source_char)
                             for i in range(length)])
    return random_string


if __name__ == '__main__':
    url = 'http://blog.nogizaka46.com/{}'.format(member_name)

    max_page = page_get(url)
    imgurl_list = img_get(member_name, max_page)
    dl_img(member_name, imgurl_list)
    jpeg_renam(member_name)
