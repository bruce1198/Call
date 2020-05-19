import requests
import urllib.parse
import json
from bs4 import BeautifulSoup
from requests_toolbelt.multipart.encoder import MultipartEncoder
import sys
from getpass import getpass
import time
import re

def encodeURIComponent(str):
    return urllib.parse.quote(str, safe='~()*!.\'')

def main():
    account = input("Student ID: ")
    password = getpass()

    call_name = ''
    pattern = re.compile("call [0-9]+")

    base_url = 'https://lms.nthu.edu.tw'
    login_url = base_url + '/sys/lib/ajax/login_submit.php'
    home_url = base_url+ '/home.php'

    params = dict(
        account=account,
        password=encodeURIComponent(password),
        ssl=1,
        stay=0
    )
    s = requests.Session()
    resp = s.post(url=login_url, params=params) #login
    if resp.status_code == 200:
        info = json.loads(resp.text.split('(')[1].split(')')[0])
        #print(info)
        if info['ret']['status']=='true' : #valid account
            find = False
            tag_tmp = None
            while find == False:
                resp = s.get(url=home_url) #get home page
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')
                    #print(soup)
                    a = soup.find_all('a')
                    for tag in a:
                        if tag.get('title')!=None:
                            if pattern.match(tag.get('title')): #found the call
                                call_name = tag.get('title')
                                find = True
                                tag_tmp = tag
                else:
                    print("connection error!")
                    exit(0)
                if find==False:
                    print("Cannot find the call with the pattern(\"call [0-9]+\"), retry after 30 secs...")
                    time.sleep(30)
            part_url = tag_tmp.get('href')
            folder_id = part_url.split('=')[-1]
            #print(folder_id)
            resp = s.get(url=base_url+part_url) #go to call page
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                ans = ''
                try:
                    ans = soup.findAll('td', text = re.compile('[aA]nswer: [0-9]+'))[0].getText().split(':')[1].strip() #find the answer of call                            
                #print(ans)
                except IndexError:
                    print('Answer not found QAQ. Plz upload the answer manually or Restart the program.')
                    exit(0)
                resp = s.get(url=base_url+'/course/doc_insert.php?folderID='+folder_id) #get submit call page
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'lxml')
                    goto = soup.find('form').get('action')
                    #print(goto)
                    input_list = soup.findAll('input')
                    form_data = {}
                    for ipt in input_list:
                        if ipt.get('name') != None:
                            form_data[ipt.get('name')] = ipt.get('value')
                    form_data['fmTitle'] = call_name
                    form_data['fmNote'] = ans
                    #form_data['iwe_btnSubmitfmNoteEditor'] = 'SUBMIT'
                    #print(form_data)
                    me = MultipartEncoder(fields=form_data)
                    headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
                        'Cache-Control': 'max-age=0',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': 'https://lms.nthu.edu.tw/course/doc_insert.php?folderID='+folder_id,
                        'Sec-Fetch-Dest': 'iframe',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
                    }
                    resp = s.post(url=base_url+'/course/doc_insert.php', data=form_data, headers=headers) #upload answer
                    soup = BeautifulSoup(resp.content, 'lxml')
                    print('Upload The Anwser Successfully!')
                    exit(0)
                else:
                    print('Connect error QAQ! Plz upload the answer manually or Restart the program.')
                    exit(0)
            else:
                print('Connect error QAQ! Plz upload the answer manually or Restart the program.')
                exit(0)
        else :
            print('Wrong account or password!')
            exit(0)
    else :
        print('Connect error QAQ! Plz upload the answer manually or Restart the program.')
        exit(0)
main()