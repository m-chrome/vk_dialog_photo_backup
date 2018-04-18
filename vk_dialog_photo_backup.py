from argparse import ArgumentParser
from datetime import datetime
from getpass import getpass
from urllib import request, error
from urllib.parse import urlsplit
import json
import os
import sys

from vk_api import VkApi
from vk_api import AuthError

FIRST_NAME = "first_name"
LAST_NAME = "last_name"
ID = "id"
DUMP = "dump"
PHOTO = "photo"
USER = "user"
TITLE = "title"
DEST_DATA = "dest_data"
NEXT_FROM = "next_from"
ITEMS = "items"
ATTACHMENT = "attachment"
DATE = "date"
URL = "url"
PHOTO_SIZES = ('photo_2560', 'photo_1280', 'photo_807', 'photo_604', 'photo_130', 'photo_75')
PROHIBITED_FN_CHARS = ('/', '\\', '|', '?', '{', '}', '=', '%', '&', '*', '<', '>', '$')


class Photo:
    def __init__(self, url, date):
        self.__url = url
        self.__date = date
        self.is_downloaded = False
        self.name = self.__make_name()

    def __make_name(self):
        url_path = urlsplit(url=self.__url).path
        url_name = url_path.split('/')[-1]
        datetime_part = datetime.fromtimestamp(self.__date).strftime("%Y%m%d_%H%M%S")
        return datetime_part + "_" + url_name

    def download(self, outdir):
        full_path = os.path.join(outdir, self.name)
        file = open(full_path, "wb")
        print("Download photo from url:", self.__url)
        try:
            photo_bytes = request.urlopen(self.__url).read()
            file.write(photo_bytes)
            self.is_downloaded = True
            print("Photo", self.name, "successfully downloaded" + '\n')
        except error.URLError:
            print("Problem with ", self.name + " download\n")
        file.close()


def get_args():
    parser = ArgumentParser(description="VK dialog photo dumper")
    parser.add_argument("-i", "--id", type=str, required=True, help="VK user or chat id")
    return parser.parse_args()


def authorize(login, password):
    print("VK authorization")
    print("Authorization attempt")
    vk_session = VkApi(login=login, password=password)
    try:
        vk_session.auth(reauth=True, token_only=True)
    except AuthError as ae:
        print(ae)
        sys.exit(1)
    print("Success")
    return vk_session


def get_photos(api, vk_id):
    start_from = ""
    count = 200
    photos = []
    while True:
        response = api.messages.getHistoryAttachments(peer_id=vk_id, start_from=start_from,
                                                      count=count, media_type=PHOTO)
        photos += response.get(ITEMS)
        start_from = response.get(NEXT_FROM)
        if start_from is None:
            break
    return photos


def search_high_res_link(photo_dict):
    for size in PHOTO_SIZES:
        if size in photo_dict.keys():
            return photo_dict.get(size)


def parse_photos(photos):
    parsed_photos = []
    for photo in photos:
        attach = photo.get(ATTACHMENT)
        photo_dict = attach.get(PHOTO)
        photo = {
            DATE: photo_dict.get(DATE),
            URL: search_high_res_link(photo_dict)
        }
        parsed_photos.append(photo)
    return parsed_photos


def main():
    args = get_args()

    login = input("Login: ")
    password = getpass(prompt="Password: ")

    vk_session = authorize(login, password)
    api = vk_session.get_api()

    print("Backup prepare")
    is_chat = False
    vk_id = args.id
    if vk_id.find('c') == -1:
        vk_id = int(vk_id)
        friend = api.users.get(user_ids=vk_id)[0]
        backup_name = "_{}_{}".format(friend.get(FIRST_NAME), friend.get(LAST_NAME))
        dst_debug = friend
    else:
        is_chat = True
        vk_id = int(vk_id[1:])
        chat = api.messages.getChat(chat_id=vk_id)
        backup_name = "_chat_{}".format(chat.get(TITLE))
        dst_debug = chat

    for ch in PROHIBITED_FN_CHARS:
        backup_name = backup_name.replace(ch, "_")
    backup_path = os.path.join(os.getcwd(), datetime.today().strftime("%Y%m%d_%H%M%S") + backup_name)

    os.makedirs(backup_path)

    user_file_path = os.path.join(backup_path, "{}.json".format(DEST_DATA))
    with open(user_file_path, 'w', encoding="utf8") as file:
        file.write(json.dumps(dst_debug, ensure_ascii=False, indent=4))

    print("Photo prepare")
    photo_dir = os.path.join(backup_path, PHOTO)
    os.makedirs(photo_dir)

    print("Backup photos")
    if is_chat:
        vk_id += 2000000000

    photos = get_photos(api, vk_id)
    photos = parse_photos(photos)

    print("Download photos")
    for photo in photos:
        ph_obj = Photo(photo.get(URL), photo.get(DATE))
        ph_obj.download(photo_dir)

    print("All {} photos were downloaded".format(len(photos)))


if __name__ == "__main__":
    main()
