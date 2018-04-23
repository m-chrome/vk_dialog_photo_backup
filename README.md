# vk_dialog_photo_backup

## Description

This is a simple Python script for downloading photos from friend or group chat.

## Requirements

* Python 3 only;
* Installed dependencies: aiohttp, vk_api.

  `pip install aiohttp, vk_api`

## Usage

python3 vk_dialog_photo_backup.py --id **<friend|chat>**

where id is:
* friend vk id (example: get friend id 1234567890 from url https://vk.com/im?sel=1234567890);
* chat vk id (example: get chat id c123 from url https://vk.com/im?sel=c123).
