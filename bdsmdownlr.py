from argparse import ArgumentParser
from bs4 import BeautifulSoup
import requests
import os


def get_input():
    parser = ArgumentParser()
    parser.add_argument("-b", "--blog",
                        type=str,
                        required=True,
                        dest="blog",
                        help="The bdsmlr blog to download"
                        )
    parser.add_argument("-u", "--email",
                        type=str,
                        required=True,
                        dest="email",
                        help="your bdsmlr email"
                        )
    parser.add_argument("-p", "--password",
                        type=str,
                        required=True,
                        dest="password",
                        help="your bdsmlr password"
                        )
    return parser.parse_args()


def download_blog(blog, email, password):
    reached_the_end = False
    page = 1

    with requests.Session() as session:
        login(session, email, password)

        while not reached_the_end:
            reached_the_end = not download_page(session, blog, page)
            if page % 5 == 0:
                print(f' downloaded {page} pages')
            page += 1
    print(f'\nFinished downloading: {blog}\n')


def download_page(session, blog, page):
    url = f'https://bdsmlr.com/blog/{blog}?latest=&page={page}'
    r = session.get(url)

    soup = BeautifulSoup(r.text, features="html.parser")
    posts = soup.find_all('div', {'class': 'post_content'})

    if not posts:
        print(f'Page {page} does not contain any images, probably reached the end.')
        return False

    for post in posts:
        download_post(blog, post)

    print('\t', end='')
    return True


def download_post(blog, post):
    try:
        post_id = post.find('i')['data-postid']
        image_urls = list(map(lambda tag: tag['href'], post.find_all('div', {'class': 'magnify'})))

        for index, imageUrl in enumerate(image_urls):
            filename = ''
            if len(image_urls) == 1:
                filename = os.path.join(blog, get_filename(post_id, imageUrl))
            else:
                filename = os.path.join(blog, get_filename(f'{post_id}-{index + 1}', imageUrl))
            if not os.path.exists(blog):
                os.makedirs(blog)
            download_image(imageUrl, filename)
    except Exception as e:
        #print(e)
        return
    print('|', end='')


def get_filename(postId, url):
    suffix = url.rsplit('.', 1)[1]
    return f'{postId}.{suffix}'


def download_image(url, filename):
    if not os.path.exists(filename):
        r_image = requests.get(url)
        with open(filename, 'wb') as file:
            file.write(r_image.content)


def login(session, email, password):
    r = session.get('https://bdsmlr.com/login')
    soup = BeautifulSoup(r.text, features="html.parser")
    token = soup.find('input', {'name': '_token'})['value']
    body = {
        '_token': token,
        'email': email,
        'password': password
    }
    p = session.post(
        'https://bdsmlr.com/login',
        data=body
    )
    print(f'Logged in as {email}\n')


if __name__ == '__main__':
    arguments = get_input()
    blog = arguments.blog

    print(f'\nDownloading {blog}\n')
    download_blog(blog, arguments.email, arguments.password)
