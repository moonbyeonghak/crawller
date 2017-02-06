# -*- coding: utf-8 -*-
import urllib.request  # 요청을 보내서 html을 받아오는 lib
import os  # 파일 생성 및 유지에 필요한 lib
import requests  # get을 보내기 위해서 사용하는 lib
import re  # 파일의 이름을 정규표현식을 사용하기 위해서 사용하는 lib
import time  # 현재의 시간을 구하기 위해서 사용하는 lib
import datetime  # 현재의 시간을 구하기 위해서 사용하는 lib
import socket  # timeout 관련 예외처리 lib
import sys  # sys.argv에 사용하기 위한 lib
import http  # http.client.RemoteDisconnected오류를 처리하기 위한 lib
import ssl  # ssl오류를 처리하기 위한 lib
from bs4 import BeautifulSoup  # 받아온 html을 분석하기 위한 lib
import json #json을 사용하기 위해서 사용하는 lib
from collections import OrderedDict#배열의 값들을 중복 제거하기 위한 lib
import random #웹페이지에서 얻어온 글자들을 random으로 추출하기 위해 사용하는 lib
import argparse#입력 변수를 파싱하기 위한 lib
import io   #utf-8로 저장 위해서 사용하는 lib
from _socket import gaierror#gaierror를 처리하기 위해 사용하는 lib
#sys.setrecursionlimit(10000)
class crawler_:
    def __init__(self):
        self.headers = {'User-Agent':'Mozilla/5.0 (Linux; Android 4.1.2; GT-I9100 Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.72 Mobile Safari/537.36'}
        folder_path,auto_boolen,query_,date_,blog_count_finish_number,categoryno=self.parse_args()
        self.BASE_DOWNLOAD_FOLDER_PATH = self.download_folder_rename(folder_path)
        self.LOG_FOLDER_PATH = self.BASE_DOWNLOAD_FOLDER_PATH + "logs/"
        self.one_blog_url_list = [] #한 블로그의 모든 post의 url을 담고있다.
        self.success_download_log = []#atomic에 사용
        self.total_download_log = []#atomic에 사용
        self.success_image_path_memory = []#처음에 실행시 log파일과 다운로드의 폴더와 파일이 같은지 확인하는것에 사용
        self.dict_key_image_value_path={}
        self.search_word_history_memory=[]
        self.image_and_text_list_reading_all=''
        self.auto_boolen=auto_boolen
        self.query_=query_
        self.date_=date_
        self.blog_count=0
        self.categoryno=categoryno
        self.blog_finish_num=int(blog_count_finish_number)
    def get_url_parameter(self):   
        display_ = '15'  # 화면에 뜨게할 검색 갯수
        start_='1'
        st_ = 'date'  # sim=정확도 / date=날짜순
        return display_, st_, start_
    
    def get_search_url(self, query_, display_, start_,st_='date'):
        search_url = 'https://m.search.naver.com/search.naver?where=m_blog&query=' + query_ + '&display=' + display_ + '&start=' + start_ + '&st=' + st_
        print(search_url)
        return search_url
    
    def get_blog_url(self, blog_url, blog_id, post_log_no):
        blog_url = re.sub(blog_url, "http://m.blog.naver.com/" + blog_id + "/" + post_log_no, blog_url)
        return blog_url
    
    def get_blog_id(self, blog_url):
        blog_id = re.sub('http://m.blog.naver.com/|/.+[^/]', '', blog_url)
        return blog_id
    
    def make_url_html(self, search_url):#url이 입력되면 해당 url의 html을 생성하고 리턴합니다.
        try:
            html_data = requests.get(search_url,allow_redirects=False)
            if(html_data.status_code==403):
                print("403 Error!!!\n")
                print("다시 실행해주세요.")
                sys.exit()
            soup_text = html_data.text
            html_soup = BeautifulSoup(soup_text, "html.parser")
            return html_soup
        except socket.gaierror as e:
            print(e)
            
    def parse_search_url_to_blog_url(self, html_soup):#html이 들어오면 url들이 total_wrap에 있는데 그 total_wrap을 분석해서 url_List를 출력해서 반환합니다.
        div_key_index_value_url_time={}
        total_wrap_HTMLs = html_soup.findAll(class_='total_wrap')
        index_=0
        for total_wrap_HTML in total_wrap_HTMLs:
            if re.match("http://m.blog.naver.com", total_wrap_HTML['href']):  # m.blog.naver.com 블로그 url을 받아온다.
                div_key_index_value_url_time[index_]=[total_wrap_HTML['href'],total_wrap_HTML.findAll(class_='sub_time sub_txt')[0].get_text()]
                index_=index_+1
        will_search_target_url_list=self.check_url_update_post_date(div_key_index_value_url_time)
        #self.check_time(div_key_url_value_time)
        return will_search_target_url_list
    
    def check_url_update_post_date(self,div_something):
        today, today_Ymd, today_YmdHMS = self.get_current_time()
        split_today_Ymd=today_Ymd.split('-')
        today_Ymd=datetime.date(int(split_today_Ymd[0]),int(split_today_Ymd[1]),int(split_today_Ymd[2]))
        will_search_target_url_list=[]
        for index_,url_value_ in div_something.items():
            if(self.date_.upper()=='ALL'):
                will_search_target_url_list.append(url_value_[0])
                pass#append(blog_url)
            elif(self.date_.upper()=='MONTH'):
                before_month_day=today_Ymd-datetime.timedelta(30)
                if('시간' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
                elif('일' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
                elif('분 전' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
                else:
                    split_date=url_value_[1].split('.')
                    update_post_date=datetime.date(int(split_date[0]),int(split_date[1]),int(split_date[2]))
                    if(update_post_date>=before_month_day):
                        will_search_target_url_list.append(url_value_[0])
                pass#blog_time('current_time-30'),주 전,일 전,시간 전
            elif(self.date_.upper()=='WEEK'):
                if('시간' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
                elif('일' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
                elif('분 전' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
            elif(self.date_.upper()=='DAY'):
                if('시간' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
                elif('분 전' in url_value_[1]):
                    will_search_target_url_list.append(url_value_[0])
        return will_search_target_url_list
            
    def pasre_title_in_blog(self, soup):
        title_html = re.findall('<title>.+</title>', str(soup))
        try:
            title_text = re.sub("<title>|</title>", "", title_html[0])
        except:
            title_text= ''
        return title_text
   
    def parse_text_and_image_in_blog(self,soup,post_text=''):#블로그로부터 text와 image를 긁어옵니다.
        unable_post_image_list=[]
        able_post_image_list=[]
        post_html_memory=[]
        div_post_ct_soup=soup.findAll('div',class_='post_ct')#가장 큰 부분인 div태그의 post_ct를 가져옵니다. 해당 부분은 블로그 포스터에서 글을 쓰는 부분입니다.
        try:
            div_post_find_all_result=div_post_ct_soup[0].findAll('div',class_="se_sectionArea")#div에서 class가 se_sectionArea인 부분입니다.
            post_html_memory.append(div_post_ct_soup[0].findAll('div',class_="se_sectionArea"))
        except:
            return "","",""
        div_post_find_all_result_2=div_post_ct_soup[0].findAll('p')
        div_post_find_all_result_3=div_post_ct_soup[0].findAll('span')
        div_post_find_all_result_4=div_post_ct_soup[0].findAll(align=True)
        div_post_find_all_result_5_td=div_post_ct_soup[0].findAll('td')
        max_result_line_number=max(len(div_post_find_all_result),len(div_post_find_all_result_2),len(div_post_find_all_result_3),len(div_post_find_all_result_4))
        for array_num in range(max_result_line_number):
            try:
                div_image_result=div_post_find_all_result[array_num].findAll('',{'data-linkdata':True})#div이하 post_ct이하에 0~m-1까지 글자 보관중 # 두 변수는 n과 m으로 for문을 돌릴경우 각각 찾은 것을 보여줘 개연성이 없다.
                div_image_json_result=json.loads(div_image_result[0]['data-linkdata'])
                self.append_parse_result_to_memory(unable_post_image_list,div_image_json_result['src'])
            except:
                pass
            try:
                div_post_find_src_result=div_post_find_all_result[0].findAll({'img':'src'})
                self.append_parse_result_to_memory(unable_post_image_list,div_post_find_src_result[array_num]['src'])
            except:
                pass
            try:
                div_post_find_all_result_2_image=div_post_find_all_result_2[array_num].findAll('span',thumburl=True)   
                self.append_parse_result_to_memory(unable_post_image_list, div_post_find_all_result_2_image[0]['thumburl'])
            except:
                pass
            try:
                self.append_parse_result_to_memory(unable_post_image_list, div_post_find_all_result_3[array_num]['thumburl'])   
            except:
                pass
            try:
                self.append_parse_result_to_memory(unable_post_image_list, div_post_find_all_result_4[array_num][0].findAll(thumburl=True))    
            except:
                pass
            try:
                div_post_find_all_result_5=div_post_find_all_result_5_td[0].findAll({'img':'src'})
                self.append_parse_result_to_memory(unable_post_image_list, div_post_find_all_result_5[array_num])
            except:
                pass
        for unable_post_image in unable_post_image_list:
            try:
                able_post_image = re.sub("\?type=\Z", "?type=w2", unable_post_image)
            except:
                able_post_image=" "
            able_post_image_list.append(able_post_image)
        able_post_image_list=self.remove_overlap(able_post_image_list)                  #파싱하는 분류 과정에서 여러개의 분류 과정 속에 중복된 결과값이 들어있을 수 있기에 중복을 제거합니다.
        return able_post_image_list,div_post_ct_soup,unable_post_image_list
        
    def append_parse_result_to_memory(self,memory_A,result=''):#result값을 append해야할 memory의 수가 많기에 해당 함수를 사용한다.
        memory_A.append(result)

    def get_another_posting(self, naver_blog_url, able_post_log_no_list):    #log_no를 추적해서 또 다른 post_no를 찾아냅니다.
        naver_blog_html_soup = self.make_url_html(naver_blog_url)
        script_html = naver_blog_html_soup.findAll("script")  # naver블로그의 html 중에서 script부분만 찾아서 그것을 script_html로 저장한다.
        unable_post_log_no_list = (re.findall('"logNo":\w+', str(script_html)))  # 그 script부분에는 logNo가 있는데 이것은 이 카테고리에 관련된 해당 게시글의 앞 뒤로 총 5개의 글의 no를 갖는다.
        for unable_post_log_no in unable_post_log_no_list:  # 위에서 5개로 추리는 과정에서 "logNo": 숫자 , 이런식으로 출력해서 사용할 수 없기에 unable_post_log_no라고 한다.
            able_post_log_no = re.sub('"logNo":', '', str(unable_post_log_no))  # 그래서 이것들 중에서 실제로 사용하는 것은 숫자만 사용하기에 숫자만 빼낸다.
            able_post_log_no_list.append(able_post_log_no)  # 이 숫자들을  갖고 list를 하나 만들어준 후에 반환한다.
        return able_post_log_no_list
    
    def check_url_in_list(self, what_url, what_list):  # 해당 리스트에 해당 url이 있는지 확인하는 함수이다.
        if(what_url not in what_list):  # 만약 어떤 리스트에 어떤 url이 없다면
            what_list.append(what_url)  # 어떤 리스트에 어떤 url을 넣어준다.
        else:
            pass
    
    def get_another_posting_algorithm(self, naver_blog_url,count,end_boolean,able_post_log_no_list):  # 또 다른 포스팅이 있는지 찾는 알고리즘이다.
        post_log_no_list = self.get_another_posting(naver_blog_url,able_post_log_no_list)  # 해당 함수는 sciprt를 통해서 포스트의 logNo를 받아온다.
        post_log_no_list=self.remove_overlap(post_log_no_list)
        if(self.categoryno):
            post_log_no_list=[naver_blog_url]
            exit(1)
        for post_log_no in post_log_no_list:  # 리스트 중에서 logNo를 각 하나하나로 출력했을 때
            blog_id = self.get_blog_id(naver_blog_url)  # blog_id를 얻는다.
            another_blog_url = self.get_blog_url(naver_blog_url, blog_id, post_log_no)  # logNo와 blog_id를 이용해서 또다른 blog의 url의 stirng을 얻는다.
            self.check_url_in_list(another_blog_url, self.one_blog_url_list)
            # check_url_in_list라는 함수에 조합하여 만든 url을 넣고, 클래스에 있는 list를 불러내고, 검사한 값을 반환받기 위해서 check_append_url_bool을 넣어준다.
            # 해당 함수는 조합하여 만든 url이 하나라도 존재한다면 True를 반환한다.
            # 없다면 False가 나오며 해당 블로그의 같은 카테고리의 글들이 적힌 url이 있는 list를 반환한다.
        if(self.one_blog_url_list[-1]==naver_blog_url):
            end_boolean=True
        return end_boolean,count
    
    def get_image_url_file_type(self, image_url):  # 이미지 url의 file_type을 가져오는 함수이다.
        file_type = re.sub("http.+/.+\.|\?type.+", "", image_url)  # http이하에서 마지막 '/'이 나오는 곳에서 확장자 앞에 점까지를 삭제한다. or ?type이하를 삭제하면 확장자만 나온다.
        return file_type
    
    def get_unsafe_file_name_to_safe_file_name(self, file_name):  # file이름에 들어가지 못하는 것을 file이름에 들어갈 수 있는 것으로 변환하여 출력한다.
        safe_file_name = re.sub("[&=\?\/\.:]", "_", file_name)
        return safe_file_name
    
    def download_image_in_blog(self, search_word,download_folder_path, post_image_url, post_url, post_title,count_,unable_post_Image_url):  # 블로그의 이미지를 다운받는 함수이다.
        fname = self.file_download(search_word,download_folder_path,post_image_url, post_url, post_title,count_,unable_post_Image_url)
        return fname
    
    def save_html_to_text(self,file_path,post_url,html,type_):
        save_path=download_folder_path + self.get_unsafe_file_name_to_safe_file_name(post_url)+ type_ + ".txt"#파일 경로만들기
        try:
            for ptag in html[0].find_all():#div태그를 검색한 것을 받아온 결과들을 모두 검색해서
                if(ptag.name=='span'):
                    ptag.name='img'
            html=str(html[0]).replace('thumburl','src')
            with open(save_path,"w",encoding='utf-8-sig') as file_info:
                file_info.write(html)
        except IndexError:#오류가 나는 이유:html에 내용이 아무것도 없기에 file_info.wirte시 아무것도 쓸 수 없다.
            with open(save_path,"w",encoding='utf-8-sig') as file_info:
                file_info.write(" ")    
                #따라서 except처리로는 pass를 한다.
            pass
        return save_path
    
    def file_download(self,search_word,download_folder_path, download_url, post_url, post_title,count_,unable_post_Image_url):  # 어떤 파일이든 받는 함수이다.
        file_path = self.file_path_create(download_folder_path,download_url, post_url,count_)
        try:
            try:
                download_url_info = urllib.request.urlopen(download_url, timeout=10)
                fname, header = urllib.request.urlretrieve(download_url, file_path, self.download_report)  # 다운로드  
                time.sleep(0.8)#다운로드 받는 속도가 너무 빠르게 되면 과접촉으로 오류가 뜨는걸 방지합니다. 2016_08_26 테스트해봐야함. 추측.
            except ValueError as err:
                download_url = urllib.request.quote(download_url, ":/")
                # urllib.request.quote는 url을 encode하기 위해서 사용합니다.
                # urllib.request.quote(url명, "encode하지 않을 단어")로 구성되어집니다.
                download_url_info = urllib.request.urlopen(download_url, timeout=10)     
                # urllib.reqeust.urlopen(URL,[,data][,time out])으로 데이터를 보낼 수도 있으며 timeout설정을 할 수 있다.
                fname, header = urllib.request.urlretrieve(download_url, file_path,self.download_report)  # 다운로드를 받고 파일의 path와 header를 반환합니다. 
            success_log_text = self.make_log_text(search_word,download_url, fname, post_url, post_title, "1")
            download_size = download_url_info.headers.get('content-length')  # 연결한 url의 객체에서 header.get(키), 키의 내용을 출력한다. #해당 라인도 value error 발생
            print("\n다운로드 size:", download_size)  # 다운받을 파일 길이 확인                                                      
            print("다운로드 path:", fname)  # 파일경로 
            self.success_download_log.append(success_log_text)#success로그에 등록할 로그를 리스트에 append합니다.
            self.total_download_log.append(success_log_text)#total로그에 등록할 로그를 리스트에 append합니다.
            self.dict_key_image_value_path[unable_post_Image_url]=file_path#추후에 다운로드 받은 url과 상대경로로 바꾸기 위해서 dict로 값을 저장시켜줍니다.
            
        except (socket.gaierror,OSError,socket.timeout, urllib.error.HTTPError, urllib.error.URLError, ssl.CertificateError, ConnectionAbortedError, ValueError) as err:
            # ConnectionAbortedError는 fname,header = urllib.request.urlretrieve(url,file_path)에서 오류 발생합니다.
            # ConnectionAbortedError는 Winerror 10053 현재 연결이 호스트 시스템의 소프트웨어에 의해 종료시에 오류 발생.
            # ssl.CertificateError는 hostname 'abc.go.kr' doesn't match '*.argc.go.kr'라는 오류를 입니다.
            # ssl.CertificateError는 a=urllib.request.urlopen(url,timeout=10)에서 발생합니다.
            # urllib.error.URLError는 <urlopen error timed out>과 같은 오류를 발생시킵니다.
            # urllib.error.URLError는 urllib.request.urlopen()에서 발생합니다.
            # socket.timeout는 urllib.request.urlopen()에서 설정한 timeout보다 시간이 초과되면 발생하는 오류입니다.
            # socket.timeout는 a=urllib.request.urlopen(url,timeout=10)에서 발생합니다.
            # urllib.error.HTTPError는 http error가 일어난다면 오류가 발생한다. ex) HTTP Error 404: Not Found
            # urllib.error.HTTPError는 a=urllib.request.urlopen(url,timeout=10)에서 발생합니다.
            # 해당 오류는 a=urllib.request.urlretrieve()에서도 발생합니다.
            # self.total_log_memory.append(fail_log_text + self.replace_safe_string(err) + "\n")
            print('다운로드 error:', err)   
            fail_log_text = self.make_log_text(download_url, str(err), post_url,post_title , "2" , str(err))
            #make_log_text(self, image_url, file_path, post_url, post_title , status_="1", err=''):
            self.total_download_log.append(fail_log_text)
         
    def download_report(self, blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        surplus = totalsize - readsofar
        if totalsize > 0:
            if surplus < 0:
                readsofar = readsofar + surplus
            percent = readsofar * 1e2 / totalsize
            s = "\r다운로드 prog: %5.1f%% %*d / %d" % (
                percent, len(str(totalsize)), readsofar, totalsize)
            sys.stdout.write(s)
            if readsofar >= totalsize: 
                sys.stdout.write("\n")
        else: 
            sys.stdout.write("\r다운로드 prog: read %d" % (readsofar))
                         
    def file_path_create(self,download_folder_path, image_url, post_url,count_):  # 파일의 이름을 만들어주는 함수입니다.
        file_type = self.get_image_url_file_type(image_url)  # 확장자를 반환받음.
        post_url = self.get_unsafe_file_name_to_safe_file_name(post_url)
        file_path = os.path.join(download_folder_path + post_url +"_index_"+count_ +"." + file_type)
        # 파일 경로+url명+file type으로 파일의 저장위치를 설정하기 위해서 os.path.join함수로 파일 이름을 만듭니다.
        
        time_stamp = self.file_name_check(file_path)
        # 같은 값의 이름을 가진 파일이 있는 지 확인합니다.
        # file_name_check는 return 값으로 현재 시간을 반환합니다.
        # 하지만 그 조건은 폴더에 같은 hash값을 가질 때만 이고 그 외에 return값은 ""입니다.
        if (time_stamp != ''):  # 같은 이름의 파일이 존재한다면 time_stamp가 찍히면 새로 경로를 설정해줍니다.
            file_path = os.path.join(download_folder_path + post_url + time_stamp +count_ +"." + file_type)
        return file_path
        # 해당 경로에 다운받으려고 하는 파일을 받았는 지 여부에 관해서 비교합니다.
        # 해당 함수에서는 memory에 올라온 url 값을 비교하여 if / else를 통해서
        # 같은 url이 존재한다면 다운로드하지 않고 url이 존재하지 않는다면 다운로드를 합니다.

    def file_name_check(self, savePath):  # 폴더 내에 똑같은 파일이 존재한다면 타임 스탬프를 붙여서 이름을 반환합니다.
        if os.path.isfile(savePath):
            time_stamp = str(time.time())[-10:-1]
            # 만약에 hash한 값의 savePath가 같다면 current타임의 시간을 뒤에다 붙여서 파일이름을 작성한다.
            return time_stamp
        return ""      
    
    def make_log_text(self, search_word='',image_url='', file_path='', post_url='', post_title='' , status_="1", err='',count_=''):
        #make_log_text(download_url, err, post_url,post_title , "2" , str(err))
        today, today_Ymd, today_YmdHMS = self.get_current_time()
        print("다운로드 time:", today_YmdHMS)  # 현재 시간을 출력합니다.
        success_log_text = today_YmdHMS + "\tDone\t" +search_word+"\t"+ image_url + "\t" + file_path + "\t" + post_url + "\t" + post_title + "\n"
        fail_log_text = today_YmdHMS + "\tFail\t" +search_word+"\t"+ image_url + "\tERROR\t" + err + "\t" + post_url + "\t" + post_title + "\n"
        history_log_text=today_YmdHMS+"\t"+search_word+"\t"+str(count_)+"\t"+self.date_+"\n"
        if(status_ == '1'):
            return success_log_text
        elif(status_ == '2'):
            return fail_log_text
        elif(status_=='3'):
            return history_log_text 
    def get_current_time(self):  # 현재의 시간을 구하는 함수입니다.
        # 현재 시간을 구하는 함수입니다. #print_switch값이 True가 되면 현재 시간을 출력해줍니다.
        today = datetime.datetime.now()  # 현재 시간에 대한 객체를 생성합니다.
        today_Ymd = today.strftime('%Y-%m-%d')  # 오늘의 시간정보를 ymd로 표현
        today_YmdHMS = today.strftime('[%Y-%m-%d_%H:%M:%S]')  # 오늘의 시간정보를 Ymd HMS로 표현
        return today, today_Ymd, today_YmdHMS
    
    def atomic_create_file_reset(self, exist_file_path, today_Ymd):  # atomic_create_file함수를 하던 도중에 종료시, 불온전한 경로들이 전개됩니다. #해당 함수는 경로를 바로잡아주기 위해서 사용합니다.    
        temp_file_path = re.sub(today_Ymd, 'temp_' + today_Ymd, exist_file_path)  # c:\경로\2016-07-25_success_log_text.txt -> c:\경로\temp_2016-07-25....txt
        will_delete_file_path = re.sub(today_Ymd, 'will_delete_file_' + today_Ymd, exist_file_path)  # c:\경로\2016-07-25_success_log_text.txt -> c:\경로\will_delete_file_2016-07-25....txt                                  
        if(os.path.isfile(temp_file_path)):  # 경우의 수 두 가지이다. temp파일이 생성되고 기존exist가 will로 안바뀐 상태와 temp파일이 생성되고 exist가 will_delelte가 될 때 이다. 
            os.remove(temp_file_path)  # 우선 1번 temp파일이 있고 exist가 생성시에는 항상 temp파일은 지워줘야 하기 때문에 os.remove()를 이 함수에 들어오면 실행시킨다.
        if(os.path.isfile(will_delete_file_path)):  # 2번은 exist가 will_delete가 될 때, exist가 존재하지 않을 때이다. 이 때 고려해야 할 것은 폴더를 새로만들어서 어떤 텍스트파일도 없을 경우이다.                    
            if(os.path.isfile(exist_file_path) == False):  # 그렇기 때문에 exist_file_path이 없는 경우에 관한 if문이 밖으로 나오게 된다면 폴더에 빈 상태일 때 의도하지 않은 상황이 나타날 것이다. 
                os.rename(will_delete_file_path, exist_file_path)  # 그래서 will_delete로 검사를 한 후에 있다는 것이 확인되면 한번 더 기존 log파일이 없는 것을 확인한 후에 rename을 해야한다.
            else:  # temp_file이 존재하고 exist_file이 존재하고 will_delete_file이 존재할 경우
                os.remove(will_delete_file_path)
                
        return exist_file_path, temp_file_path, will_delete_file_path
    
    def atomic_create_file(self, exist_file_path, temp_file_path, will_delete_file_path, memory):
        # 파일을 write하는 도중에 오류를 방지하기 위해서, temp파일을 만들어서 작성을 하고 temp파일이 작성이 된다면
        # 기존 파일의 이름을 바꾼 후에 temp파일을 기존 파일의 이름으로 바꾸는 과정을 하는 함수입니다.
        with io.open(temp_file_path, "w",encoding='utf-8-sig') as log_file:
            # 성공한 로그 파일을 불러와 글을 작성합니다.
            for log_line in memory:
            # crawler객체에서 success_log_memory 리스트를 가져와서 한 줄 한 줄 읽습니다.
                try:
                    log_file.write(log_line)
                    # 성공한 로그의 파일 경로에 있는 log 파일에 각 한 줄 한 줄을 작성합니다.
                except:#오류 원인 none타입이 왔을 경우
                    pass
        os.rename(exist_file_path, will_delete_file_path)  # 지금 존재하는 파일을 삭제할 파일로 변경합니다.
        os.rename(temp_file_path, exist_file_path)  # temp파일을 존재할 파일로 이름을 변경합니다. #os.rename은 os.rename(기존 경, 바꿀 경로)입니다.
        os.remove(will_delete_file_path)  # temp파일이 기존 파일로 되었다면 지우기로 할 파일을 지워줍니다.
        
    def make_log_file_path(self, log_file_name):#log파일의 경로를 만드는 함수입니다.
        today, today_Ymd, today_YmdHMS = self.get_current_time()#today_Ymd를 사용하기 위해서 현재 시간의 변수들을 받아옵니다.
        log_file_path = os.path.join(self.LOG_FOLDER_PATH + today_Ymd + log_file_name + ".txt")#txt파일의 경로를 만들어줍니다.
        with open(log_file_path, "a") as opener:#txt파일을 만들어줍니다.
            opener.write("")
        return log_file_path
    
    def some_folder_create(self, some_folder_path):# some_folder_path를 입력받으면 그 경로에 폴더가 있는 지 확인하고 없다면 해당 경로에 폴더를 만듭니다.
        if os.path.isdir(some_folder_path):        # 같은 경로에 다운로드를 할 폴더가 있는지 확인합니다.
            print(some_folder_path, "에 폴더 존재")
        else:
            try:
                os.mkdir(some_folder_path)         # 해당 경로에 다운로드를 담아놓는 폴더를 생성합니다.
                print('폴더 생성\n')
            except:                                # 해당 경로를 가지 못 해, 폴더를 만들지 못 할 경우 일어나는 오류입니다.  
                print("폴더 생성 오류")  
    
    def download_folder_rename(self, argv_text):  # cmd로 받는 파일 경로를 오류없이 처리하기 위한 함수입니다.
        if(argv_text[-1]!='/'):
            print("파일 경로는 c:/example/나 /home/downloads/와 같이 /를 이용하여 합니다.")
            sys.exit()
        return argv_text
            
    def check_download_file_in_disk(self, log_file_path):  # 다운로드 폴더의 list를 만들어서  메모리에 올라온 파일 경로와 비교해서 메모리에 없는 파일이 있다면 삭제합니다.
        # 디스크 안에 파일이 log에 있는 파일 경로들 중 하나가 아니라면 디스크 안에 파일을 삭제한다. 처음 시작했을 때 file_path들이 메모리 상에 올라오고
        # 파이썬 라이브러리를 통해서 폴더 안의 내용들을 각 값들로 하여서 그 값들을 메모리의 값과 비교하는 구조이다.
        files_in_folder = os.listdir(self.BASE_DOWNLOAD_FOLDER_PATH)
        # os.listdir은 list형식으로 해서 폴더 안의 내용들을 return한다. 반환값은 파일명만 반환한다. 따라서 파일 경로를 지정해줘야한다.
        for index_number_A in range(len(files_in_folder)):  # 폴더 안에 있는 파일들을 0번인덱스부터 불러냅니다.
            myfile_check = False  # 내가 갖고 있는 파일들을 True/False로 구분합니다.
            files_in_folder[index_number_A] = self.BASE_DOWNLOAD_FOLDER_PATH + files_in_folder[index_number_A]  # 경로를 설정
            for index_number_B in range(len(log_file_path)):  # 메모리에 올라온 파일 list들을 0번 인덱스부터 불러냅니다.                                                                                    
                myfile_check = log_file_path[index_number_B] in files_in_folder[index_number_A]  # 메모리에 올라온 파일 경로들과 폴더안에 있는 파일을 비교합니다. 만약 둘이 같다면 True로 반환합니다.
                if myfile_check:  # 둘이 같다면 break.
                    break
            if(os.path.isdir(files_in_folder[index_number_A])):  # 검사하는 것들 중에 폴더라면 삭제하지 않습니다.
                myfile_check = True 
            if(myfile_check == False):  # myfile_check가 False인 것들을 삭제합니다.
                try:
                    os.remove(files_in_folder[index_number_A])
                    print(files_in_folder[index_number_A], ":삭제.\n")
                except:
                    pass  # os.remove는 해당 특정경로의 폴더안에 폴더를 제외하고 파일들만 삭제합니다.
            else:
                print(files_in_folder[index_number_A], ":생존.\n")  # files_in_folder를 하나씩 검사해서 myfile_check==True라면 삭제합니다. 
                
    def success_path_in_log_to_memory(self,success_image_path_memory=[]):  #성공한 로그파일의 path를 읽어오는 함수입니다.
        #해당 함수는 __init__할 때만 사용되며 시작시에 path값으로 파일들을 삭제할 때만 사용됩니다.
        allday_success_log_file_list = self.allday_log_file_to_a_day_log_file()  # allday_log_file_to_a_day_log_file은  폴더안의 모든 log의 경로값을 반환해줍니다.
        for a_day_success_log_file in allday_success_log_file_list:  # 모든 날의 success_log값에서 하루의 success_log의 파일의 제목값을 하나씩 돌립니다.
            with open(a_day_success_log_file, "r",encoding='utf-8') as a_day_success_log_file_read:  # a_day_success_log_file=하루의 log파일 제목값을 읽기모드로하여, a_day_success_log_file_read라는 파일 객체를 생성을 해줍니다.
            # 성공한 로그파일의 파일 경로를 읽어옵니다.        
                for text_line in a_day_success_log_file_read:
                    try:
                        success_image_path_memory=self.parse_success_path_in_log_text_line(text_line)
                    except IndexError:  #인덱스가 없을 경우
                        pass
        return success_image_path_memory #return 성공한 이미지 경로가 저장된 메모리
    
    def load_log_file_to_memory(self,log_file_path,memory):#로그파일을 메모리에 올리는 함수입니다.
        with open(log_file_path,"r",encoding='utf-8') as log_file_info:#로그파일을 읽어서 메모리에 올립니다.
            for log_file_text_line in log_file_info:
                memory.append(log_file_text_line)
        return memory
    
    def append_image_and_text_to_memory(self, image_1,image_2,text_1,text_2,memory):
        memory.append(image_1)
        memory.append(image_2)
        memory.append(text_1)
        memory.append(text_2)
        return memory
    
    def parse_success_path_in_log_text_line(self,text_line):#로그 텍스트 라인 중에 성공한 파일 경로를 메모리로 만듭니다.
        temp_text=re.split("[\t\n]",text_line)#\t나 \n을 지점으로 split을 함.
        #split을 했을 때 4번째에 파일경로가 오기에 인덱스 3번 호출
        self.success_image_path_memory.append(temp_text[3])  # success_path_memory에 넣어줍니다.
        return self.success_image_path_memory
    
    def allday_log_file_to_a_day_log_file(self):  # 로그 폴더내의 모든 파일을 가져와서 success_log_file을 뽑아내는 함수입니다.
        allday_success_log_file_path_list = []
        allday_log_file = os.listdir(self.LOG_FOLDER_PATH)
        # 성공한 경로의 파일을 메모리로 올리는 함수입니다. 해당 함수는 __init__할 때만 사용되며 추후에 파일 경로를 비교하고 만약
        # log파일의 내용과 다르다는 것을 파일이 존재하지 않는다는 것으로 인식해서 삭제시킵니다.
        # 해당 path는 여러 날짜의 log를 다 검사해야합니다.
        for a_day_log_file in allday_log_file:  # 모든 날의 로그파일을 for문을 돌려서 하루의 로그파일을 뽑아냅니다.
            if('success' in a_day_log_file):  # 모든 날의 로그파일 중에서 success가 들어갔다면
                allday_success_log_file_path_list.append(self.LOG_FOLDER_PATH + a_day_log_file)  # allday_success_log_file_list에 그 날을 넣어줍니다.     
        return allday_success_log_file_path_list    
    
    def make_download_folder(self,naver_blog_url):#다운로드 폴더를 생성하는 함수입니다.
        blog_id=self.get_blog_id(naver_blog_url)#blog_id를 따와서 변수로 저장시킵니다.
        naver_blog_url=self.get_unsafe_file_name_to_safe_file_name(naver_blog_url)#naver_url에서 사용하지 못하는 특수문자를 제거합니다.
        download_folder_path=self.BASE_DOWNLOAD_FOLDER_PATH+"http___m_blog_naver_com_"+blog_id+"/"#다운로드 폴더 경로를 기준 다운로드폴더 + 네이버+id 사용을 통해서 경로를 만들어줍니다.
        try:
            os.mkdir(download_folder_path)#폴더를 생성합니다.
        except:
            pass#오류시에 패스를 해줍니다.
        return download_folder_path
    
    def load_used_post_to_memory(self,log_file_path,used_post_url_list=[]):#total_log_file_path를 입력함으로서 used_post_url_list에 블로그 post의 url을 가져옵니다.
        with open(log_file_path,encoding='utf-8') as log_file_info:
            for log_file_line_text in log_file_info:
                used_post_url=re.findall("http://m\.blog.+\t",log_file_line_text)#포스트 url을 가져옵니다.
                used_post_url=re.sub("\t","",used_post_url[0])                   #findall이 리스트형식이기 때문에 [0] 사용
                used_post_url_list.append(used_post_url)                         
        used_post_url_list=self.remove_overlap(used_post_url_list)               #중복을 제거합니다.
        return used_post_url_list                                                #중복이 제거된 리스트를 반환합니다.
    
    def remove_overlap(self,memory):#중복을 제거하는 함수입니다.
        list_memory=list(OrderedDict.fromkeys(memory))#OrderedDict.fromkeys를 사용하면 리스트의 중복을 제거하고 순서를 그대로 유지합니다.
        return list_memory
    
    def check_already_used_post_url(self,post_url_list,used_post_url_list=[]):#지금 접촉하려는 url을 이미 사용한 url과 비교해서 중복해서 들어가지 않게 해줍니다.
        try:
            for list_number in range(len(post_url_list)):
                if post_url_list[list_number] in used_post_url_list:
                    print("이미 크롤링한 웹:",post_url_list[list_number])
                    del post_url_list[list_number]
        except:
            pass
        
    def extract_random_text(self):#랜덤를 추출하는 함수입니다.
        url='http://m.naver.com/'#naver url의 url을 저장합니다.
        naver_html=self.make_url_html(url)#naver url의 html을 생성합니다.
        data_news_html=naver_html.findAll('a',{'data-area':'NEWS'})#a 태그 이하의 data-area가 NEWS인 구역에서
        random_text_list=[]                                        #random_text_list를 생성합니다.
        for a in range(len(data_news_html)):                       #a 태그 이하의 data-area가 잡히는 갯수에 따라서
            random_text_list.append(data_news_html[a].get_text())  #random_text_list에 data-area의 news구역의 텍스트를 append시킵니다.
        random.shuffle(random_text_list)                           #random_text_list를 뒤섞은 후에
        unsafe_word_list=self.slice_list_text(random_text_list)           #random_text_list에서 단어만 갖고 있는 list를 뽑아냅니다.
        safe_word_list=self.change_unsafe_word_to_safe_word(unsafe_word_list)#사용할 수 없는 단어를 삭제해줍니다.
        print(safe_word_list)
        return safe_word_list[15]                                       #word_list에 15번째에 있는 원소 아무거나를 리턴합니다. 해당 변수는 검색어로 사용됩니다.
    
    def change_unsafe_word_to_safe_word(self,unsafe_word_list):#사용하지 못하는 단어를 삭제해주는 함수입니다.
        safe_word_list=[]
        for unsafe_word in unsafe_word_list:
            safe_word_list.append(re.sub("[^0-9,.ㄱ-ㅣ가-힣a-zA-Z]","",unsafe_word))#0-9 / 한글 / 영어만 인식합니다.
        return safe_word_list
    
    def slice_list_text(self,list_): #문장을 공백마다 slice해서 단어로 바꿉니다.
        word_list=[]                 #리턴할 값을 list를 만듭니다.        
        for text_list_in_list in list_:#랜덤으로 받아온 문장 집합을 하나씩 꺼냅니다.
            for text_in_text_list_ln_list in text_list_in_list.split(' '): #문장 하나마다 공백을 기준으로 split합니다.
                text_in_text_list_ln_list=re.sub("[\s,\'\"\n]|","",text_in_text_list_ln_list)#필요 없는 기호를 삭제해줍니다.
                word_list.append(text_in_text_list_ln_list)#배열에 반환할 값들을 담습니다.
        word_list=self.remove_overlap(word_list)           #만약 중복되는 것이 있을 경우 삭제합니다.
        return word_list             #단어 list를 리턴합니다.
    
    def parse_args(self):           #입력변수들을 인식하는 함수입니다. 해당 함수는 파일경로만 필요합니다.
        parser = argparse.ArgumentParser(description="크롤러 옵셜 설정 변수",usage="parsing_blog2.py -p c:/example/ -q '검색어' -d week or python3 parsing_blog2.py -p /home/example/ -q '' -a -d all -n 1000 -a -cn" )
        parser.add_argument('-p','--path', action='store',required=True,metavar='PATH', help = '저장시킬 폴더명. -p c:/example/')
        parser.add_argument('-a','--auto', action='store_true',help='''자동검색을 사용하기 위해서 -a,--atuo를 붙이면 query문에 자동적으로 단어를 입력해줍니다. 필수값은 아닙니다.''')
        parser.add_argument('-q','--query',nargs=1, action='store',required=True,metavar='SEARCH_WORD', help = '검색할 검색어 명. -q "검색어명"')
        parser.add_argument('-d','--date', action='store',metavar='DATE',required=True,choices=['all','month','week','day'],help = '''검색어의 파일date를 설정한다. 필수값은 아닙니다.\n-d all, month, week, day''')
        parser.add_argument('-n','--number',default=100,action='store',metavar='NUMBER',help='''몇 개의 블로그를 받을 지에 대해서 카운트해줍니다. 기본 값은 100입니다. 필수값은 아닙니다.''')
        parser.add_argument('-cn','--categoryno',action='store_true',help='''블로그 파싱을 할 경우에 같은 카테고리를 뒤지지 않기 위해서 사용하는 변수입니다. 기본값은 카테 고리의 모든 포스트 글을 가져옵니다.''')
        parser.print_help()
        args = parser.parse_args()
        return args.path,args.auto,args.query,args.date,args.number,args.categoryno
    
    def replace_url_to_file_path(self,save_path,unable_post_Image_list):   #기존에 이미지url과 텍스트가 있는 텍스트파일을 파일경로와 텍스트가 있는 텍스트파일로 교체합니다.
        with open(save_path, "r",encoding='utf-8') as image_and_text_list_reading: #해당 텍스트 파일을 읽어들입니다.
            crawler.image_and_text_list_reading_all=str(image_and_text_list_reading.read())#해당 텍스트파일을 읽어서 변수로 저장합니다.
        for key_,value_ in crawler.dict_key_image_value_path.items():   #해당 딕셔너리엔 key에는 image, value에는 path가 들어가 있어서 이 값들을 꺼냅니다.
            try:
                crawler.image_and_text_list_reading_all=str(crawler.image_and_text_list_reading_all).replace(key_,value_)#key를 value로 교체합니다.
            except:
                pass
        save_path=self.rename_save_path(save_path)#파일 이름을 다시 지어서 작성할 준비를 합니다.
        with open(save_path+"_FILE_PATH.txt","w",encoding='utf-8-sig') as image_and_text_list_writing:
            image_and_text_list_writing.write(crawler.image_and_text_list_reading_all)#텍스트파일을 재작성해줍니다.
        try:
            os.rename(save_path+".txt",save_path+"_will_delete.txt")
            os.rename(save_path+"_FILE_PATH.txt",save_path+"_FILE_PATH.html")
            os.remove(save_path+"_will_delete.txt")
        except:
            pass
        if(os.path.getsize(save_path+"_FILE_PATH.html")<=30):
            os.remove(save_path+"_FILE_PATH.html")
    def rename_save_path(self,save_path):   #.txt를 지우기 위해서 사용하는 함수입니다.
        save_path=re.sub(".txt","",save_path)
        return save_path                    #지운 값을 리턴해줍니다.

    
#객체 생성---------------    
crawler = crawler_()#크롤러라는 객체를 생성합니다.
#다운 로드 폴더 생성--------
crawler.some_folder_create(crawler.BASE_DOWNLOAD_FOLDER_PATH) #다운로드를 하는 폴더를 생성합니다.
crawler.some_folder_create(crawler.LOG_FOLDER_PATH)           #로그를 저장시키는 폴더를 생성합니다.
#로그폴더 및 다운로드 폴더 생성--
today, today_Ymd, today_YmdHMS = crawler.get_current_time()   #현재 시간을 구하는 함수입니다.
success_log_file_path = crawler.make_log_file_path("success") #self.LOG_FOLDER_PATH + today_Ymd + log_file_name='success' + ".txt" success의 이름을 가진 log 파일을 생성합니다.
total_log_file_path = crawler.make_log_file_path("total")     #self.LOG_FOLDER_PATH + today_Ymd + log_file_name='total' + ".txt"   total의 이름을 가진 log 파일을ㅇ 생성합니다.
search_word_history_path=crawler.make_log_file_path("search_word_history")
#메모리 적재--------------
success_image_path_memory = crawler.success_path_in_log_to_memory()#다운로드 된 이미지의 파일 경로를 저장한 메모리에 적재합니다.
used_post_list=crawler.load_used_post_to_memory(total_log_file_path)#사용되어진 post url을 메모리에 적재합니다. 
crawler.load_log_file_to_memory(total_log_file_path,crawler.total_download_log)#total_log_file_path는 로그파일의 경로인데 해당 파일의 경로의 로그를 total_download_log 메모리에 채움
crawler.load_log_file_to_memory(success_log_file_path,crawler.success_download_log)#success_log_file_path는 로그파일의 경로인데 해당 파일의 경로의 로그를 success_download_log 메모리에 채움
crawler.load_log_file_to_memory(search_word_history_path,crawler.search_word_history_memory)
crawler.check_download_file_in_disk(success_image_path_memory)     #위의 함수에서 다운로드 받은 이미지 파일 경로를 해당 함수에 집어 넣음으로써 만약에 메모리에 없는 파일이 다운로드 폴더 안에 있다면 삭제시킵니다.
#검색할 쿼리문을 실시간 검색어로부터 받아옵니다.
display_, st_, start_ = crawler.get_url_parameter()                #검색을 하기 위해서 필요한 변수들을 뽑아냅니다.
prev_page_check_memory=[]   #이전에 돌았던 for문에서 다운 받은 url을 리스트로 저장합니다.
if(crawler.auto_boolen==True):
    query_=crawler.extract_random_text()                               #해당 함수에서 얻어낸 랜덤의 단어를 쿼리로 사용합니다.
else:
    query_=crawler.query_[0]
for infinite_ in range(9999):
    #위의 쿼리문을 통해서 얻어온 url을 통해서 블로그의 url을 얻습니다.
    search_url = crawler.get_search_url(query_, display_, start_)    #쿼리문에 해당하는 블로그 검색 화면을 url로 가져옵니다.
    search_content_html_soup = crawler.make_url_html(search_url)       #랜덤의 쿼리문에 해당하는 블로그 검색 url을 html로 만듭니다.
    naver_blog_url_List = crawler.parse_search_url_to_blog_url(search_content_html_soup)#블로그 검색시 나오는 여러 naver url을 출력해서 list로 반환받음
    #얻어온 블로그의 url을 통해서 해당 블로그의 다른 글들의 url을 얻어내는 1차 for문
    if(naver_blog_url_List==prev_page_check_memory):#현재 받아온 naver_blog_url_list가 이전에 갖고 있던 prev_page_check_memory와 같다면 더이상 검색할 수 없기에 종료합니다.
        print("종료")
        exit(1)
    history_log=crawler.make_log_text(query_, "", "", "", "", "3","" ,infinite_)#search_word_history로그를 만듭니다.
    crawler.search_word_history_memory.append(history_log)#search_word_history를 일괄적으로 write하기 때문에 메모리에 저장시켜서 계속 쌓습니다.
    search_word_history_exist_file_path, search_word_history_temp_file_path, search_word_history_will_delete_file_path = crawler.atomic_create_file_reset(search_word_history_path,today_Ymd)
    #search_word_log가 저장된 경로를 넣어주고, 해당 일을 입력시켜주게 되면 각 경로를 반환시켜주고 기존에 atomic_craete가 잘 되었는지 검사해줍니다.
    del prev_page_check_memory[:]#위에서 prev_page_check_memory를 검사했기 때문에 메모리를 삭제시켜줍니다.
    for naver_blog_url in naver_blog_url_List:#naver의 블로그 url주소들이 들은 것을 for문으로 url 한 개씩으로 가져옵니다.
        download_folder_path=crawler.make_download_folder(naver_blog_url)#블로그의 id를 갖고 있는 기존 다운로드 폴더 내에 id의 이름을 가진 다운로드 폴더를 생성합니다.
        crawler.one_blog_url_list.append(naver_blog_url)#해당 리스트는 한개의 블로그의 여러 포스트 url을 저장하는 리스트 입니다. 0번 인덱스를 채우기 위해서 접촉한 블로그의 post url 주소를 넣어줍니다.
        prev_page_check_memory.append(naver_blog_url)#종료조건 중, 마지막 페이지를 체크하기 위한 조건으로 이전 페이지와 다음 검색할 페이지가 같으면 종료하기 위해서 append로 url을 모아줍니다.
        end_boolean=False
        #get_another_posting_algorithm은 end_boolean의 bool값과 one_blog_url_list을 순차적으로 넣어줍니다.
        #one_blog_url_list는 검색시에 우연히 노출되는 포스트 url인데 이곳을 기점으로하여 log_no를 조사해서 또 다른 post들의 url을 얻어냅니다.
        #만약에 log_no로 얻은 url주소가 내가 갖고 있는 url_list에 없다면 append 있다면 append 시키지 않습니다.
        #그리고 one_blog_url_list[index]가 one_blog_url_list[-1]이라면 종료를 해줍니다. 이 뜻은 더이상 추가할 post_url이 없다는 것을 의미합니다.
        count=0#검색에 노출된 블로그에 들어가 100개의 포스트로 제한하기 위해서 사용하는 변수입니다.
        able_post_log_no_list=[]#해당 포스트에 연관된 log_no가 적힌 것을 저장하는 list입니다.
        try:#나올 수 있는 오류 : RecursionError-maximum recursion depth exceed가 나올 시에는 pass
            #redirect 오류가 날 시에 죽음.
            while(True):
                end_boolean,count=crawler.get_another_posting_algorithm(crawler.one_blog_url_list[count],count,end_boolean,able_post_log_no_list)#블로그에 들어가 같은 카테고리 내의 모든 글들의 url을 가져오는 재귀함수로 한개의 블로그 포스트 url 리스트를 반환받습니다.
                print(crawler.one_blog_url_list[count])
                count=count+1
                if(end_boolean or count==80):
                    break
        except:
            pass
        one_blog_post_url_list=crawler.check_already_used_post_url(crawler.one_blog_url_list,used_post_list)#한 블로그의 post url이 담긴 리스트를 이미 사용한 post url을 체크하는 함수에 집어넣어 반환값으로 사용하지 않은 블로그 post의 url을 리스트로 반환받는다.
        crawler.atomic_create_file(search_word_history_exist_file_path,search_word_history_temp_file_path,search_word_history_will_delete_file_path,crawler.search_word_history_memory)
        for post_blog_url in crawler.one_blog_url_list:#get_another_posting_algorithm 블로그 리스트들 중에서 1개의 블로그를 검색합니다.
            print("포스트 url:", post_blog_url)    
            html_soup = crawler.make_url_html(post_blog_url)     # one_blog_url_list들 중 하나의 post url을 html로 만듭니다.
            post_title = crawler.pasre_title_in_blog(html_soup)  # html로 만들었다면 해당 html을 해당 함수에 넣어서 title을 가져옵니다. 반환 값은 string
            Image_list,div_post_ct_soup,unable_post_Image_list=crawler.parse_text_and_image_in_blog(html_soup)#블로그로부터 text와 image를 긁어옵니다. 또한 다운로드받은 이미지 리스트와 div의 html, 그리고 수정하지 않은 이미지 경로 리스트를 반환합니다.
            save_path=crawler.save_html_to_text(download_folder_path,post_blog_url,div_post_ct_soup,"_HTML")#html을 text로 바꾸는 함수입니다. 다운로드폴더의 경로와 blog의 posturl을 입력하고 위에서 받은 html파싱한 것을 입력하게 되면 
            image_file_index_number=0#사진을 저장할 때 인덱스로 사용하기 위해서 사용하는 index_number
            for index_ in range(len(Image_list)): #해당 for문은 블로그의 post에서 url하나에서 나오는 사진들의 url들을 리스트로 담아놓은 값을 풀어서 이미지를 저장하고 경로들을 리스트에 저장시켜놓습니다.
                image_file_index_number=str(image_file_index_number)#이미지를 저장할 때 사용하는 인덱스 넘버를 저장하는 변수입니다.
                print("다운로드 url:", Image_list[index_])
                crawler.download_image_in_blog(query_,download_folder_path, Image_list[index_], post_blog_url, post_title,image_file_index_number,unable_post_Image_list[index_])  # 다운로드에 성공한 로그에 대한 메모리와 실패한 로그에 대한 메모리를 얻을 수 있음.
                success_exist_file_path, success_temp_file_path, success_will_delete_file_path = crawler.atomic_create_file_reset(success_log_file_path, today_Ymd)
                total_exist_file_path, total_temp_file_path, total_will_delete_file_path = crawler.atomic_create_file_reset(total_log_file_path, today_Ymd)
                crawler.atomic_create_file(success_exist_file_path, success_temp_file_path, success_will_delete_file_path, crawler.success_download_log)
                #다운로드에 성공한 로그는 success의 이름을 가진 파일들을 경로로 하여 atomic을 실행
                crawler.atomic_create_file(total_exist_file_path, total_temp_file_path, total_will_delete_file_path, crawler.total_download_log)
                #다운로드에 성공하거나 실패한 로그는 total의 이름을 가진 경로로 하여 atomic을 실행
                image_file_index_number=int(image_file_index_number)+1
            crawler.replace_url_to_file_path(save_path,unable_post_Image_list) #기존에는 div태그가 txt파일로 저장되어서 image_url이 적혀있는데 이것을 html파일로 만들고 image url을 다운로받은 상대경로로 바꿔놓습니다.
        del crawler.one_blog_url_list[:]#한 블로그에서 얻은 모든 포스트 list입니다.
        crawler.blog_count=crawler.blog_count+1#블로그 한개를 보게 되면 count를 해줍니다.
        if(crawler.blog_count==int(crawler.blog_finish_num)):
            print("크롤러 종료")
            sys.exit(1)
    start_=str(int(start_)+int(display_))#display는 뿌려지는 갯수인데 15개로 고정되어있고 수정해도 값이 변하지 않는다.