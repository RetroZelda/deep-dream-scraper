
import requests
import argparse
import shutil
import json
import sys
import os
from dataclasses import dataclass
from bs4 import BeautifulSoup
from lxml import html

global_source = "https://deepdreamgenerator.com"
global_page = "{url}/?page={num}"

# cookie data
global_cookie_laravel_session = "eyJpdiI6InFWb05QTVFPM1ZHcWlUUi9JYk1zWEE9PSIsInZhbHVlIjoiNkYyQ0d1S05Bc000ZWhCNXBYcWRqdUcvc05rNnlZeXh6OFJTcWlVUVZWdDgxTDU1YmFUdFZGalE3OXpUWE4yYWg1a2FsODRmME1Cdy9ZV2lTejFmL050NS9lbUZWSUw1SGRYSEtZVHNsM0Q3RG5YVjlmWjFWeU1CZVRVenF0Q2siLCJtYWMiOiJmMzhlZWIwMGI3MzJiOGQ2OGRjMGMxNDMxYTJhYWViMmM3NDU5ZTBmZWFmN2YyOGJjZWM1YmJkZWEwYmEyYjU5In0%3D"
global_cookie_XSRF_TOKEN = "eyJpdiI6IndEb2QzUHVwaGxZdDlFbWtVMEoxZEE9PSIsInZhbHVlIjoiT09UYXNiVmVQejlFaFZaalZDbVQvSTVUb0RLVW1ORUlrOXo5Nkk3dFdxSTF5UlNMVDJBTm01cmExRG5ud3F3ZHRoaEdHbXhmRnY1WTRrZ3Foem5OU0g1eFVTZEhPNldnNkVFQ3Q4N3k3UXphcDVFUnJMZ3hLbnJ2YXU4WUNFNUMiLCJtYWMiOiJjZmFiM2NiZjNkZTg2MjBmZTQ0NGFhZjBmOTE5NWI2MjM4MTdhOGQ0ZmI1YzgxMjU4NWQwZWRmYTlhYjViZmFkIn0%3D"
global_cookie_stripe_sid = "2e095426-9385-4b5e-862d-c1a4aeaa87a8cdf11b"
global_cookie_stripe_mid = "40eb5227-e7de-4e6e-8315-73fbb01e2c80baa6e3"

@dataclass
class ImageData:
    name : str
    url : str
    ext : str
    id : str

def ScrapeData(start_page, num_pages):
    cur_page = start_page
    pages_left = num_pages

    scraped_data = []

    while cur_page > 0 and pages_left > 0:

        cookies = {
            'laravel_session': global_cookie_laravel_session,
            'XSRF-TOKEN' : global_cookie_XSRF_TOKEN,
            '__stripe_sid' : global_cookie_stripe_sid,
            '__stripe_mid' : global_cookie_stripe_mid
            }

        page_to_scrape = global_page.format(url=global_source, num=cur_page)
        page_raw = requests.get(page_to_scrape, cookies=cookies)
       
        soup = BeautifulSoup(page_raw.text, 'html.parser')
        
        feed_objs = soup.find_all("div", {"class": "feed-object"})
        for feed_obj in feed_objs:
            img = feed_obj.find("img")
            
            # get the name
            sub_html = img.attrs['data-sub-html']
            subsoup = BeautifulSoup(sub_html, 'html.parser')
            name_data = subsoup.find("span")

            img_name = name_data.text.replace(u'\xa0', u' ').strip()
            img_url = img.attrs['data-src']
            dot_pos = img_url.rfind('.')
            img_ext = img_url[dot_pos + 1:]
            img_id = img_url[img_url.rfind('/') + 1: dot_pos]

            # trim versions from ext
            moar = img_ext.find('?')
            if moar >= 0:
                img_ext = img_ext[:moar]
            scraped_data.append(ImageData(img_name, img_url, img_ext, img_id))

        cur_page -= 1
        pages_left -= 1
    return scraped_data

def GetImages(image_data_array, out_dir):
    for image_data in image_data_array:

        # download the image
        file_request = requests.get(image_data.url, stream=True)
        file_request.raw.decode_content = True

        # TODO: save using hte ID and create a CSV that maps the name to the file
        final_file = "{path}/{id}.{ext}".format(path=out_dir, id = image_data.name, ext = image_data.ext)
        print("saving: " + final_file)
        with open(final_file, 'wb') as file_out:
                shutil.copyfileobj(file_request.raw, file_out)

def main(args):
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    scraped_data = ScrapeData(args.pages_back, args.pages_back)
    GetImages(scraped_data, args.outdir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='deep-dream')
    parser.add_argument('--pages_back', '-p', type=int, default=1)
    parser.add_argument('--outdir', '-o', default='./output')
    args = parser.parse_args()

    result = main(args)
    sys.exit(result)