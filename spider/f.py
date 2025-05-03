import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
]
def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Referer': 'https://www.tianqi.com/',
        'cookie': 'cityPy=nanning; cityPy_expire=1739374268; UserId=17395259843950314; Hm_lvt_ab6a683aa97a52202eab5b3a9042a8d2=1738769468,1739525985,1739769297; Hm_lvt_7c50c7060f1f743bccf8c150a646e90a=1739685782,1739767519,1739785270,1739790781; HMACCOUNT=221CACC0E917732B; Hm_lvt_30606b57e40fddacb2c26d2b789efbcb=1739686084,1739769401,1739785273,1739791849; Hm_lpvt_30606b57e40fddacb2c26d2b789efbcb=1739791849; Hm_lpvt_7c50c7060f1f743bccf8c150a646e90a=1739791849'
    }
print(get_headers()['cookie'])