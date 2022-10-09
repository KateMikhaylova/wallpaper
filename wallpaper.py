import requests
import bs4
from PIL import Image

import datetime
import argparse
import sys

from typing import Optional, NoReturn, Dict, Union


def get_arguments() -> argparse.Namespace:
    """
    Gets arguments from command line
    :return: argparse.Namespace object, containing necessary arguments
    """
    my_parser = argparse.ArgumentParser(prog='wallpaper',
                                        usage='%(prog)s needed_year needed_month needed_size',
                                        description='Wallpaper download',
                                        epilog='Thank for usage!')

    my_parser.add_argument('Year', metavar='year', type=int, help='needed wallpaper release year')
    my_parser.add_argument('Month', metavar='month', type=int, help='needed wallpaper release month')
    my_parser.add_argument('Size', metavar='size', type=str, help='needed wallpaper size, format example 320x480')

    args = my_parser.parse_args()

    return args


def check_year_and_month(args: argparse.Namespace) -> Optional[NoReturn]:
    """
    Checks whether year and month are indicated correctly
    :param args: argparse.Namespace object, containing necessary arguments i.e. Year and Month
    :return: None if arguments are acceptable, otherwise script closes
    """
    if args.Year < 2010 or args.Month not in range(1, 13):
        print('Проверьте правильность ввода. Год должен быть 2010 или больше, месяц с 1 по 12')
        sys.exit()


def create_url(args: argparse.Namespace) -> str:
    """
    Determines url of wallpaper article for parsing
    :param args: argparse.Namespace object, containing necessary arguments i.e. Year and Month
    :return: url for parsing
    """
    BASE_URL = 'https://www.smashingmagazine.com/'
    MONTHS = {'01': 'january', '02': 'february', '03': 'march', '04': 'april', '05': 'may', '06': 'june', '07': 'july',
              '08': 'august', '09': 'september', '10': 'october', '11': 'november', '12': 'december'}

    if args.Month != 1:
        url_year = args.Year
        url_month = str(args.Month - 1)
        if len(url_month) == 1:
            url_month = '0' + url_month
    else:
        url_year = args.Year - 1
        url_month = '12'

    if len(str(args.Month)) == 1:
        url_text_month = MONTHS['0' + str(args.Month)]
    else:
        url_text_month = MONTHS[str(args.Month)]

    final_url = f'{BASE_URL}{url_year}/{url_month}/desktop-wallpaper-calendars-{url_text_month}-{args.Year}'

    return final_url


def get_links(args: argparse.Namespace, url: str) -> Union[Dict[str, str], NoReturn]:
    """
    Creates dict with future files names and links for download of file
    :param args: argparse.Namespace object, containing necessary arguments i.e. Size
    :param url: url for parsing
    :return: dict with name: link structure. If url does not exist, script closes
    """
    response = requests.get(url)

    if response.status_code == 404:
        print('Ошибка. Либо страницы за этот месяц в принципе не существует, либо она названа не по типовому шаблону')
        sys.exit()

    soup = bs4.BeautifulSoup(response.text, features='html.parser')
    article_content = soup.find(id="article__content")
    links = article_content.find_all('a')

    links_dict = {}

    for link in links:
        if link.text == args.Size:
            if link.attrs.get('title') is not None:
                file_name = ''.join(
                    [letter for letter in ' '.join(link.attrs['title'].split()[0:-2]) if letter not in '*|:"<>?/\\'])
                if file_name not in links_dict:
                    links_dict[file_name] = link.attrs['href']
                else:
                    links_dict[file_name + '-2'] = link.attrs['href']
            else:
                file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                if file_name not in links_dict:
                    links_dict[file_name] = link.attrs['href']
                else:
                    links_dict[file_name + '-2'] = link.attrs['href']

    if not links_dict:
        print('''Обои не найдены. Проверьте правильность ввода размера. 
Размер вводится в формате числоxчисло, например 320x480. x - в английской раскладке клавиатуры''')

    return links_dict


def save_wallpapers(links_dict: Dict[str, str]) -> None:
    """
    Saves found wallpapers to current directory
    :param links_dict: dict with name: link structure.
    :return: None
    """
    for name, link in links_dict.items():
        resp = requests.get(link, stream=True).raw
        img = Image.open(resp)
        img.save(f'{name}.png', 'png')


def run() -> None:
    """
    Runs the script
    :return: None
    """
    arguments = get_arguments()
    check_year_and_month(arguments)
    url = create_url(arguments)
    wallpaper_links = get_links(arguments, url)
    save_wallpapers(wallpaper_links)


if __name__ == '__main__':
    run()
