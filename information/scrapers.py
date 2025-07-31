import re

import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError


def get_vessel_info(imo_no):
    def get_page(url, counter=10, dynamic_verification=True):
        """
        Returns response
        @param url:
        @param counter:
        @param dynamic_verification:
        @return:
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        verify = True
        for count in range(1, counter + 1):
            try:
                response = requests.get(url, timeout=10, headers=headers, verify=verify)
                return response
            except ConnectionError as cae:
                print("A weird connection error!", count, url, cae)
                continue
            except Exception as e:
                print('Error occurred while getting page content!', count, url, e)
                if dynamic_verification and type(e) == SSLError:
                    verify = False
                continue
        raise TimeoutError

    data = {}
    if not len(str(imo_no)) == 7:
        raise TypeError("IMO must consist of 7 digits.")
    vesselfinder_url = "https://www.vesselfinder.com/vessels/SHIPNAME-IMO-{}-MMSI-0".format(imo_no)
    page = get_page(vesselfinder_url)
    soup = BeautifulSoup(page.content, "lxml")

    if not soup.find("div", "error-content"):
        flag_style = soup.find("div", "title-flag-icon")["style"]
        # use django's own urlize function here
        data["Flag URL"] = re.findall(r"(?P<url>https?://[^\s()]+)", flag_style)[0]
        for product in soup.find_all("tr"):
            n3 = product.find("td", "n3")
            v3 = product.find("td", "v3")
            if n3 and v3:
                if v3.find("i", "nd"):
                    data[n3.text] = None
                else:
                    data[n3.text] = v3.text
        return data
    else:
        raise ValueError("Vessel not found.")
