# -*- coding: utf-8 -*-
import urllib.request  # 요청을 보내서 html을 받아오는 lib
import os  # 파일 생성 및 유지에 필요한 lib
import requests  # get을 보내기 위해서 사용하는 lib
import re  # 파일의 이름을 정규표현식을 사용하기 위해서 사용하는 lib
import time  # 현재의 시간을 구하기 위해서 사용하는 lib
import datetime  # 현재의 시간을 구하기 위해서 사용하는 lib
import hashlib  # 파일제목을 hash를 통해서 재설정함
import socket  # timeout 관련 예외처리 lib
import sys  # sys.argv에 사용하기 위한 lib
import http  # http.client.RemoteDisconnected오류를 처리하기 위한 lib
import ssl  # ssl오류를 처리하기 위한 lib
from bs4 import BeautifulSoup  # 받아온 html을 분석하기 위한 lib
import json ## json으로 bing_request를 묶기 위해서 사용하는 lib
import argparse#입력변수를 parse하기위해서 사용하는 lib
from _socket import gaierror#gaierror에러를 처리하기위해서 사용하는 lib
import io##utf-8로 파일을 저장시키기 위해서 io.open을 사용해주고 encoding='utf-8-sig'로 저장합니다.
import random
from collections import OrderedDict#배열의 값들을 중복 제거하기 위한 lib
socket.setdefaulttimeout(15)#소켓의 timeout을 설정시켜놓음으로써 urlretrieve의 다운로드 도중에 끊기는 현상을 방지합니다.
# 조건 :로그 폴더의 이름은 항상 logs이여야 한다.
class crawler_:
    def __init__(self):
        self.success_url_memory = []  # url을 파일에서 읽어와 메모리에 사용하도록 하는 list입니다. 모든 날짜를 받습니다.
        self.success_log_memory = []  # log를 메모리상에 올려서 append시켜서 사용하도록 하는 list입니다. 오늘 하루의 날짜를 받습니다. 
        self.success_path_memory = []  # memory상에 성공한 path를 올리는 list입니다. 모든 날짜를 받습니다.
        self.total_log_memory = []  # log은 비교할 필요가 없기에 파일에서 읽어오지 않는다.
                                    # 두 개의 변수를 이용해서 메모리상에 url을 올려놓고
                                    # 1페이지가 넘어갈 때마다 일괄적으로 메모장에 작성을 하는 방식을 사용할 것 입니다.
                                    # 해당 텍스트들은 리스트를 사용하여 관리합니다.
        self.delete_log_memory=[]
        self.temp_total_log_memory=[]
        self.search_word_history_memory=[]#어떤 검색어를 입력했고 언제 실행이 됐으며 어떤 사이트를 사용했는 등에 관해서 저장하는 메모리.
        crawler_choice,DOWNLOAD_FOLDER_PATH,TARGET_FILE_NAME,TARGET_FILE_TYPE,freshness,AUTO_CHECK,DOWNLOAD_FILE_NUMBER,CLEAR_BOOL =self.parse_args()#크롤러 선택 변수, 폴더 경로 설정 변수, 파일 이름 변수, date에 관련된 변수
        self.freshness=freshness    #Bing에서 사용하는 변수로 day,week,month,all이 옵니다.
        self.crawler_choice=crawler_choice[0]        # daum | bing이 오는 변수. 크롤러를 선택하는 변수입니다.
        self.TARGET_FILE_NAME = TARGET_FILE_NAME[0]  # 내가 검색하고자 하는 파일의 이름이 무엇인지 저장하는 변수입니다.
        self.TARGET_FILE_TYPE = TARGET_FILE_TYPE[0]  # 내가 검색하고자 하는 파일의 유형이 무엇인지 저장하는 변수입니다.
        self.LOG_FILE_TYPE = TARGET_FILE_TYPE[0]     # 로그에 작성되는 파일 타입입니다.
        self.extend_filetype_list=['XLSX','PPTX','DOCX']
        if(TARGET_FILE_TYPE[0].upper() in self.extend_filetype_list):
            self.LOG_FILE_TYPE=TARGET_FILE_TYPE[0]
            self.TARGET_FILE_TYPE=TARGET_FILE_TYPE[0][0:3]
            
        self.DOWNLOAD_FOLDER_PATH = self.download_folder_rename(DOWNLOAD_FOLDER_PATH[0])  # hwp파일을 담아놓는 폴더의 위치를 갖고 있는 변수입니다.
        self.LOG_FOLDER_PATH = self.DOWNLOAD_FOLDER_PATH + "logs/"  # log를 담아놓을 수 있는 폴더의 위치를 갖고 있는 변수입니다.
        self.SUCCESS_LOG_FILE_NAME = '_success_log.txt'  # 성공한 로그를 담아두는 파일의 이름을 지정하는 변수입니다.
        self.TOTAL_LOG_FILE_NAME = '_total_log.txt'  # 실패한 로그를 담아두는 파일의 이름을 지정하는 변수입니다.
        self.SEARCH_WORD_HISTORY_FILE_NAME='_search_word_history.txt'   #검색한 시간과 검색어, 검색 페이지, 검색 변수를 저장하는 로그이다.
        self.get_address = []  # def split_web에서 html연결을 통해서 얻어낸 url을 저장하는 배열이다.
        self.set_current_time() #현재의 시간을 가져오는 변수입니다.
        self.today_Ymd = self.today.strftime('%Y-%m-%d')  # 오늘의 시간정보를 ymd식으로 표현합니다.
        self.today_YmdHMS = self.today.strftime('[%Y-%m-%d_%H:%M:%S]')  # 오늘의 시간정보를 Ymd HMS로 표현입니다.
        self.SUCCESS_LOG_FILE_PATH = self.LOG_FOLDER_PATH + self.today_Ymd + self.SUCCESS_LOG_FILE_NAME  # ex)c:\경로\2016-07-25_success_log_text.txt
        self.TOTAL_LOG_FILE_PATH = self.LOG_FOLDER_PATH + self.today_Ymd + self.TOTAL_LOG_FILE_NAME  # 모든 로그 파일을 만들 경로를 설정합니다.   ex)#c:\경로\2016-07-25_total_log_text.txt
        self.SEARCH_WORD_HISTORY_FILE_PATH = self.LOG_FOLDER_PATH + self.today_Ymd + self.SEARCH_WORD_HISTORY_FILE_NAME # 검색어의 히스토리를 저장하는 로그입니다. 
        self.HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1', 'Accept-language':'fr'}  # request.get에 보내기 위한 header저장 변수입니다. 
        self.offset='0'#bing에서 사용하는 skip변수
        self.log_file_reset()  # 해당 함수는 다운로드 폴더를 만들고 로그파일,폴더,다운로드 폴더를 만듭니다. 
        self.success_log_temp_file_path, self.success_log_will_delete_file_path = self.atomic_create_file_reset(self.SUCCESS_LOG_FILE_PATH)  # 해당 함수는 success_log_file이 atomic_create_file 도중에 종료시에 exist_file이 사라지고 will_delete만 있는 것을 정정합니다.
        self.total_log_temp_file_path, self.total_log_will_delete_file_path = self.atomic_create_file_reset(self.TOTAL_LOG_FILE_PATH)  # 해당 함수는 total_log_file이 atomic_create_file 도중에 종료시에 exist_file이 사라지고 will_delete만 있는 것을 정정합니다.
        self.search_word_history_temp_file_path, self.search_word_history_delete_file_path = self.atomic_create_file_reset(self.SEARCH_WORD_HISTORY_FILE_PATH)
        self.success_url_file_to_memory()  # 메모리에 올려서 사용을 하기위해서 사용해줍니다. #해당 함수는 self.success_url_memory의 내용을 채워줍니다. 한 번만 실행됩니다.
        self.log_file_to_memory()  # 해당 함수는 self.success_log_memory의 내용을 채워줍니다. 한 번만 실행됩니다.                                   
        self.success_path_file_to_memory()  # self.success_path_file_to_memory는 성공한 로그의 파일 경로들을 list형태로
                                            # self.success_path_memory를 채워줍니다. 한 번만 실행됩니다.                                    
        if(CLEAR_BOOL==True):
            self.check_disk(self.success_path_memory)  # success_path_memory에는 모든 날짜의 파일 경로를 갖고 있습니다. 만약 이 momory에 없이 폴더 안에 파일이 있다면 삭제를 합니다.    
        self.AUTO_CHECK=AUTO_CHECK          #쿼리문을 자동적으로 입력해서 무한적으로 검색하기 위함을 사용하는 변수를 체크하는 변수
        self.last_page_bool=False           #마지막페이지를 체크하는 bool변수입니다.
        self.bool_Bing_finish=False         #마지막페이지를 체크하는 bool변수입니다.
        self.DOWNLOAD_FILE_NUMBER=int(DOWNLOAD_FILE_NUMBER)#다운로드 받을 파일의 수를 저장하는 변수입니다.
        self.DOWNLOAD_FILE_COUNT=0          #다운로드 받을 파일의 수를 체크하는 변수입니다.
        print("crawler")
  
    def parse_args(self):
        parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),description="크롤러 옵셜 설정 변수",usage='''%(prog)s -s [bing|daum] -p FILE_PATH -q QUERY_STRING -t FILE_TYPE -d [all|month|week|day] (-a) (-n NUMBER) \n\nexample:%(prog)s -s bing -p c:/download/ -q 신문 -t hwp -d week\nexample:%(prog)s -s bing -p /home/abc/download/ -q 신문 -t hwp -d day -a -n 500\nexample:%(prog)s -s daum -p /home/abc/download/ -q 신문 -t hwp
        \nexample:%(prog)s -s google -p e:/example/ -q "" -a -t hwp -d day -n 500 -d week''')
        parser.add_argument('-s','--site',nargs=1,action="store",choices=['bing','daum','google'],required=True,metavar='SITE',help ='검색할 사이트 명. -s [daum | bing | google]')
        parser.add_argument('-p','--path',nargs=1, action='store',required=True,metavar='PATH', help = '저장시킬 폴더명. -p c:/download/')
        parser.add_argument('-q','--query',nargs=1, action='store',required=True,metavar='SEARCH_WORD', help = '검색할 검색어 명. -q "검색어명"')
        parser.add_argument('-t','--type',nargs=1, action='store',required=True,metavar='FILE_TYPE', help = '검색할 검색어의 파일 유형. -t hwp doc ppt xls ..')
        parser.add_argument('-d','--date', action='store',metavar='DATE',choices=['all','month','week','day'],help = '''bing, google에서만 사용가능. 검색어의 파일date를 설정한다. 필수값은 아닙니다.\n-d all, month, week, day''')
        parser.add_argument('-a','--auto', action='store_true',help='''자동검색을 사용하기 위해서 -a,--atuo를 붙이면 query문에 자동적으로 단어를 입력해줍니다. 필수값은 아닙니다.''')
        parser.add_argument('-n','--number',default=1000,action='store',metavar='NUMBER',help='''몇 개의 파일을 받을 지에 대해서 카운트해줍니다. 기본 값은 1000입니다. 필수값은 아닙니다.''')
        parser.add_argument('-c','--cleardisk',action='store_true',help='''디스크를 검사하기 위해서 -c,--clear를 붙이면 시작할 때 디스크를 검사합니다. 디스크 검사 대상은 로그에 없는 파일을 삭제하거나 파일 용량이 3KB이하인 파일을 삭제합니다.''')
        parser.print_help()
        args = parser.parse_args()
        try:
            if(args.site[0]=='daum'):
                if args.date[0]:
                    print(args.site[0]+"에서 입력하신 -d 옵션인 "+args.date+"는 사용되지 않습니다.")
                    time.sleep(2)
        except:
            pass
        if(args.site[0]=='bing' or args.site[0]=='google'):
            if(args.date==None):
                print("-d [all, month, week, day] --date [all, month, week, day]를 입력하여 주십시오.")
                exit(1)
        print(args.site,args.path,args.query,args.type,args.date)
        return args.site, args.path, args.query, args.type, args.date, args.auto, args.number, args.cleardisk
    
    def atomic_create_file_reset(self, exist_file_path):  # atomic_create_file함수를 하던 도중에 종료시, 불온전한 경로들이 전개됩니다. #해당 함수는 경로를 바로잡아주기 위해서 사용합니다.    
        temp_file_path = re.sub(self.today_Ymd, 'temp_' + self.today_Ymd, exist_file_path)  # c:/경로/2016-07-25_success_log_text.txt -> c:/경로/temp_2016-07-25....txt
        will_delete_file_path = re.sub(self.today_Ymd, 'will_delete_file_' + self.today_Ymd, exist_file_path)  # c:/경로/2016-07-25_success_log_text.txt -> c:/경로/will_delete_file_2016-07-25....txt                                  
        if(os.path.isfile(temp_file_path)):  # 경우의 수 두 가지이다. temp파일이 생성되고 기존exist가 will로 안바뀐 상태와 temp파일이 생성되고 exist가 will_delelte가 될 때 이다. 
            os.remove(temp_file_path)  # 우선 1번 temp파일이 있고 exist가 생성시에는 항상 temp파일은 지워줘야 하기 때문에 os.remove()를 이 함수에 들어오면 실행시킨다.
        if(os.path.isfile(will_delete_file_path)):  # 2번은 exist가 will_delete가 될 때, exist가 존재하지 않을 때이다. 이 때 고려해야 할 것은 폴더를 새로만들어서 어떤 텍스트파일도 없을 경우이다.                    
            if(os.path.isfile(exist_file_path) == False):  # 그렇기 때문에 exist_file_path이 없는 경우에 관한 if문이 밖으로 나오게 된다면 폴더에 빈 상태일 때 의도하지 않은 상황이 나타날 것이다. 
                os.rename(will_delete_file_path, exist_file_path)  # 그래서 will_delete로 검사를 한 후에 있다는 것이 확인되면 한번 더 기존 log파일이 없는 것을 확인한 후에 rename을 해야한다.
            else:  # temp_file이 존재하고 exist_file이 존재하고 will_delete_file이 존재할 경우
                os.remove(will_delete_file_path)
                
        return temp_file_path, will_delete_file_path
    
    def atomic_create_file(self, exist_file_path, temp_file_path, will_delete_file_path, memory):
        # 파일을 write하는 도중에 오류를 방지하기 위해서, temp파일을 만들어서 작성을 하고 temp파일이 작성이 된다면
        # 기존 파일의 이름을 바꾼 후에 temp파일을 기존 파일의 이름으로 바꾸는 과정을 하는 함수입니다.
        with io.open(temp_file_path, "w",encoding='utf-8-sig') as log_file:
            #utf-8로 파일을 저장시키기 위해서 io.open을 사용해주고 encoding='utf-8-sig'로 저장합니다.
            # 성공한 로그 파일을 불러와 글을 작성합니다.
            for log_line in memory:
            # crawler객체에서 success_log_memory 리스트를 가져와서 한 줄 한 줄 읽습니다.
                log_file.write(log_line)
                # 성공한 로그의 파일 경로에 있는 log 파일에 각 한 줄 한 줄을 작성합니다.
        os.rename(exist_file_path, will_delete_file_path)  # 지금 존재하는 파일을 삭제할 파일로 변경합니다.
        os.rename(temp_file_path, exist_file_path)  # temp파일을 존재할 파일로 이름을 변경합니다. #os.rename은 os.rename(기존 경, 바꿀 경로)입니다.
        os.remove(will_delete_file_path)  # temp파일이 기존 파일로 되었다면 지우기로 할 파일을 지워줍니다.
    
    def set_current_time(self):  # 현재의 시간을 구하는 함수입니다.
        # 현재 시간을 구하는 함수입니다. #print_switch값이 True가 되면 현재 시간을 출력해줍니다.
        self.today = datetime.datetime.now()  # 현재 시간에 대한 객체를 생성합니다.
        self.today_Ymd = self.today.strftime('%Y-%m-%d')  # 오늘의 시간정보를 ymd로 표현
        self.today_YmdHMS = self.today.strftime('[%Y-%m-%d_%H:%M:%S]')  # 오늘의 시간정보를 Ymd HMS로 표현
        
    def recode_current_time(self, search_word='',url='', file_path=''):  # 현재 시간을 출력하고 log_text에 기록하는 함수입니다.
        # 반환 값으로 success_log_text와 fail_log_text를 반환합니다.
        self.set_current_time()  # 현재 시간 정보를 가져옵니다.
        print("다운로드 time:", self.today_YmdHMS)  # 현재 시간을 출력합니다.
        success_log_text = self.today_YmdHMS + "\tDone\t" + search_word +"\t" +url + "\t" + file_path + "\n"
        # 성공했을 때 작성해야할 로그의 내용
        # [현재 시간] \t url \t file_path
        fail_log_text = self.today_YmdHMS + "\tFail\t" + search_word + "\t" + url + "\tERROR\t"
        # 실패했을 때 작성해야할 로그의 내용
        # [현재 시간] \t url \t file_path \t err내용
        return success_log_text, fail_log_text

    def success_url_file_to_memory(self):  # 성공한 로그파일의 url을 읽어오는 함수입니다.
        # 해당 함수는 __init__할 때만 사용되며 추후에 url값을 비교하기 위해서 사용합니다.
        # memory에서는 모든 날짜의 url을 갖고 있습니다.
        # 로그를 기록할 때에는 url값을 비교하여 이미 존재하는 url은 다운로드 받지 않게 합니다. 따라서 로그를 작성하는 것에는 영향을 미치지 않습니다.
        allday_success_log_file_list = self.allday_log_file_to_a_day_log_file()  # allday_log_file_to_a_day_log_file은  폴더안의 모든 success_log의 경로값을 반환해줍니다.
        for a_day_success_log_file in allday_success_log_file_list:  # 모든 날의 success_log값에서 하루의 success_log의 파일의 제목값을 하나씩 돌립니다.
            with open(a_day_success_log_file, "rb") as a_day_success_log_file_read:  # a_day_success_log_file=하루의 log파일 제목값을 읽기모드로하여, a_day_success_log_file_read라는 파일 객체를 생성을 해줍니다.
                for text_line in a_day_success_log_file_read: # 하루의 로그 파일을 읽어서 한 줄 한 줄 for문을 돌리고 밑의 내용은 url을 읽어오는 과정입니다.  
                    try:
                        temp_text = re.findall("http.+\t",str(text_line.decode('utf-8')))
                        result_text = re.sub('\t', '', temp_text[0])
                        # 우리는 \t를 사용할 필요가 없기 때문에 마지막 단어 \t를 삭제하여줍니다. 또한 log가 불순물이 있을 수 있습니다.
                        # 그럴 시에 그 열은 list에서 []로 처리되어 공백이기에 c[0]을 호출합니다. 이 때 []는 아무 내용이 없기 때문에
                        # 오류를 출력합니다. 그렇기 때문에 except처리를 해줍니다.
                        self.success_url_memory.append(result_text)
                        # 메모리에 올리기 위해서 각 url을 리스트로 처리해줍니다. 이것을 갖고 다운 받을 url과 비교 파일 경로를 설정할 url과 비교를 합니다.
                    except IndexError:  # 없을 경우
                        pass
              
    def success_path_file_to_memory(self):  # 성공한 로그파일의 path를 읽어오는 함수입니다.
        # 해당 함수는 __init__할 때만 사용되며 시작시에 path값으로 파일들을 삭제할 때만 사용됩니다.
        allday_success_log_file_list = self.allday_log_file_to_a_day_log_file()  # allday_log_file_to_a_day_log_file은  폴더안의 모든 log의 경로값을 반환해줍니다.
        for a_day_success_log_file in allday_success_log_file_list:  # 모든 날의 success_log값에서 하루의 success_log의 파일의 제목값을 하나씩 돌립니다.
            with open(a_day_success_log_file, "r",encoding='utf-8') as a_day_success_log_file_read:  # a_day_success_log_file=하루의 log파일 제목값을 읽기모드로하여, a_day_success_log_file_read라는 파일 객체를 생성을 해줍니다.
            # 성공한 로그파일의 파일 경로를 읽어옵니다.
                for text_line in a_day_success_log_file_read:
                    try:
                        temp_text=re.split("[\t\n]",text_line)#\t나 \n을 지점으로 split을 함.
                        #split을 했을 때 4번째에 파일경로가 오기에 인덱스 3번 호출
                        self.success_path_memory.append(temp_text[4])  # success_path_memory에 넣어줍니다.
                    except IndexError:  # 없을 경우
                            pass
                        
    def allday_log_file_to_a_day_log_file(self):  # 로그 폴더내의 모든 파일을 가져와서 success_log_file을 뽑아내는 함수입니다.
        allday_success_log_file_list = []
        allday_log_file = os.listdir(self.LOG_FOLDER_PATH)
        # 성공한 경로의 파일을 메모리로 올리는 함수입니다. 해당 함수는 __init__할 때만 사용되며 추후에 파일 경로를 비교하고 만약
        # log파일의 내용과 다르다는 것을 파일이 존재하지 않는다는 것으로 인식해서 삭제시킵니다.
        # 해당 path는 여러 날짜의 log를 다 검사해야합니다.
        for a_day_log_file in allday_log_file:  # 모든 날의 로그파일을 for문을 돌려서 하루의 로그파일을 뽑아냅니다.
            if('success' in a_day_log_file):  # 모든 날의 로그파일 중에서 success가 들어갔다면
                allday_success_log_file_list.append(self.LOG_FOLDER_PATH + a_day_log_file)  # allday_success_log_file_list에 그 날을 넣어줍니다.     
        return allday_success_log_file_list    
    
    def make_search_word_history_log(self,page_number,memory,freshness):
        self.set_current_time()
        log_text=str(self.today_YmdHMS)+"\t"+self.crawler_choice+"\t"+self.TARGET_FILE_NAME+"\t"+self.LOG_FILE_TYPE+"\t"+str(page_number)+"\t"+freshness+"\n"
        memory.append(log_text)
        return memory
    
    def log_file_to_memory(self):  # 로그 파일을 메모리에 올리는 함수입니다.
        self.write_to_memory(self.SUCCESS_LOG_FILE_PATH, self.success_log_memory)  # success_log_file의 경로와 메모리를 입력시키면 경로에 대한 파일 객체를 생성해 메모리에 올립니다.
        self.write_to_memory(self.TOTAL_LOG_FILE_PATH, self.total_log_memory)  # total_log_file의 경로와 메모리를 입력시키면 경로에 대한 파일 객체를 생성해 메모리에 올립니다.
        self.write_to_memory(self.SEARCH_WORD_HISTORY_FILE_PATH,self.search_word_history_memory)
        
    def write_to_memory(self, log_file_path, log_memory):  # 로그 파일을 메모리에 올리는 기능을 하는 함수입니다.
        with open(log_file_path, "r",encoding='utf-8') as log_file_read:  # 모든 로그파일을 읽어옵니다. 읽어온 것을 file_read객체를 생성해줍니다.       
            for text_line in log_file_read:
                log_memory.append(text_line)  # 각 객체를 한 줄 씩 읽어와서 total_log_memory에 입력시킵니다.
                
    def check_url(self, url):  # 고유한 성질을 갖는 url을 체크합니다. #변수로 받은 url을 memory의 url과 비교해서 True/False로 존재여부를 반환합니다.
        return_value = url in self.success_url_memory  # 메모리에 올라온 url중 성공한 것을 temp_url이라 지정합니다.
        return return_value  # True/False 반환
    
    def check_disk(self, log_file_path):  # 다운로드 폴더의 list를 만들어서  메모리에 올라온 파일 경로와 비교해서 메모리에 없는 파일이 있다면 삭제합니다.
        # 디스크 안에 파일이 log에 있는 파일 경로들 중 하나가 아니라면 디스크 안에 파일을 삭제한다. 처음 시작했을 때 file_path들이 메모리 상에 올라오고
        # 파이썬 라이브러리를 통해서 폴더 안의 내용들을 각 값들로 하여서 그 값들을 메모리의 값과 비교하는 구조이다.
        files_in_folder = os.listdir(self.DOWNLOAD_FOLDER_PATH)#폴더안에 파일들을 리스트로 저장시킨다.
        # os.listdir은 list형식으로 해서 폴더 안의 내용들을 return한다. 반환값은 파일명만 반환한다. 따라서 파일 경로를 지정해줘야한다.
        print("잠시만 기다려주십시오. 디스크를 검사하고 있습니다.\n")
        for index_number_A in range(len(files_in_folder)):# 폴더 안에 있는 파일들을 0번인덱스부터 불러냅니다.
            myfile_check = False  # 내가 갖고 있는 파일들을 True/False로 구분합니다.
            #files_in_folder[index_number_A] #파일만 있는 경로
            #self.DOWNLOAD_FOLDER_PATH + files_in_folder[index_number_A]#파일의 절대경로
            try:#해당 라인부터는 용량이 3KB이하인 파일을 삭제하는 코드입니다.
                if(os.path.getsize(self.DOWNLOAD_FOLDER_PATH+files_in_folder[index_number_A])<=3072):#폴더안의 파일들을 index순으로 뽑아내서 3072byte이하라면 삭제합니다.
                    print(self.DOWNLOAD_FOLDER_PATH+files_in_folder[index_number_A]+" :%dByte 파일 삭제.\n"%os.path.getsize(self.DOWNLOAD_FOLDER_PATH+files_in_folder[index_number_A]))#print
                    os.remove(self.DOWNLOAD_FOLDER_PATH+files_in_folder[index_number_A])#해당 파일들을 삭제합니다.
                    self.find_del_log(files_in_folder[index_number_A])#파일을 지우고 또한 로그도 지워야하기 때문에 해당 파일경로를 delete_log_memory에 저장시켜놓습니다.
            except (PermissionError,FileNotFoundError,IndexError) as e:#만약 파일을 찾지 못 할 경우에 오류를 출력합니다.
                print(e)   
            for index_number_B in range(len(log_file_path)):  # 메모리에 올라온 파일 list들을 0번 인덱스부터 불러냅니다.                                                                                    
                myfile_check = files_in_folder[index_number_A] in self.split_log_file_path_slash(log_file_path[index_number_B])   # 메모리에 올라온 파일 경로들과 폴더안에 있는 파일을 비교합니다. 만약 둘이 같다면 True로 반환합니다.
                if myfile_check:  # 둘이 같다면 break.
                    break    
            if(os.path.isdir(self.DOWNLOAD_FOLDER_PATH+files_in_folder[index_number_A])):  # 검사하는 것들 중에 폴더라면 삭제하지 않습니다.
                myfile_check = True 
            if(myfile_check == False):  # myfile_check가 False인 것들을 삭제합니다.
                try:
                    print(self.DOWNLOAD_FOLDER_PATH+files_in_folder[index_number_A], ":삭제.\n")    
                    os.remove(self.DOWNLOAD_FOLDER_PATH+files_in_folder[index_number_A])
                except:
                    pass  # os.remove는 해당 특정경로의 폴더안에 폴더를 제외하고 파일들만 삭제합니다.
                 
        temp_log_file_path_list,base_log_file_path_list,will_delete_log_file_path_list=self.write_total_log_to_log_file()#위의 로그들을 로그파일로 작성합니다.
        self.change_temp_file_to_current_file(temp_log_file_path_list,base_log_file_path_list,will_delete_log_file_path_list)
        exit(1)
    def split_log_file_path_slash(self,log_file_path):
        split_log_file_path=log_file_path.split('/')
        only_log_file_name=split_log_file_path[-1]
        return only_log_file_name
        
    def find_del_log(self, path_log):#로그를 입력받으면 __init__에 있는 메모리에 append시킵니다.
        self.delete_log_memory.append(path_log)
    
    def write_total_log_to_log_file(self):#삭제할 로그를 제외하고 모든 로그를 로그파일로 작성합니다. #리턴 값으로 atomic 저장할 로그 경로들을 받습니다.
        current_log_path_list=[]#현재 로그 파일 경로를 리스트로 저장시킵니다.
        temp_log_path_list=[]   #temp 로그 파일 경로를 리스트로 저장시킵니다.
        will_del_log_path_list=[]#앞으로 삭제할 로그 파일 경로를 리스트로 저장시킵니다.
        log_list_in_folder=os.listdir(self.LOG_FOLDER_PATH)#로그 폴더 경로를 입력시, 해당 파일 경로의 파일 리스트를 리스트로 저장합니다.
        for log_number in range(len(log_list_in_folder)):#로그 파일의 갯수만큼 파일을 비교합니다.
            if not(os.path.isdir(self.LOG_FOLDER_PATH+log_list_in_folder[log_number])):   #폴더가 아니라면 실행하는 if문 
                base_log_file_path=self.LOG_FOLDER_PATH+log_list_in_folder[log_number]#기존 로그 파일의 경로
                temp_log_file_path=self.LOG_FOLDER_PATH+'temp'+log_list_in_folder[log_number]#바꿔서 temp로 저장할 로그 파일 경로
                will_del_log_file_path=self.LOG_FOLDER_PATH+'will'+log_list_in_folder[log_number]#기존 로그 파일을 삭제시키기 위해 임시로 저장하는 파일 경로
                self.append_log_path_list(base_log_file_path, current_log_path_list)#기존 로그 파일 경로를 로그 파일 경로를 저장시켜놓는 리스트에 저장시킵니다.
                self.append_log_path_list(temp_log_file_path,temp_log_path_list)    #temp 로그 파일 경로를 로그 파일 경로를 저장시켜놓는 리스트에 저장시킵니다.
                self.append_log_path_list(will_del_log_file_path, will_del_log_path_list)#will_del 로그 파일 경로를 로그 파일 경로를 저장시켜놓는 리스트에 저장시킵니다.
                with io.open(base_log_file_path,"r+",encoding='utf-8-sig') as log_file:#기존 로그를 읽기 위해서 객체를 생성합니다.
                    for log_file_line in log_file.readlines():#한 줄 씩 나눈 list를 for문을 통해서 한 줄의 string을 불러냅니다.
                            self.temp_total_log_memory.append(log_file_line)#위에서 나눈 string들을 메모리에 저장시킵니다. 
                with io.open(base_log_file_path,"r+",encoding='utf-8-sig') as log_file,io.open(temp_log_file_path,"w",encoding='utf-8-sig') as temp_log_file:
                    #기존 로그를 읽어서 파일 경로만 따기 위해서 'r+'을 통해서 파일 객체를 생성해주고, 지울 log가 저장된 메모리와 기존 로그의 파일 경로를 비교해서 삭제한 로그들을 temp로 저장시키기 위해서 파일 객체를 생성해줍니다.
                    for log_file_line in log_file.readlines():#기존 log파일을 한 줄씩 읽습니다.
                        split_log_file_line=log_file_line.split("\t")#한 줄을 \t을 기준으로 split을 해줍니다. 
                        for index_ in range(len(self.delete_log_memory)):#지워야 할 로그의 갯 수 만큼 index를 잡아줍니다.
                            try:
                                if(self.delete_log_memory[index_] in split_log_file_line[4]):#0번 인덱스부터 n-1번 인덱스까지 비교를 하는데 한 개 한 개씩 \t를 기준으로 나눈 line에 path와 같다면
                                    self.temp_total_log_memory.remove(log_file_line)#해당 로그의 라인을 삭제시켜줍니다.
                            except:
                                pass
                    self.temp_total_log_memory=self.remove_overlap(self.temp_total_log_memory)#여러번 for문을 통해서 여러번 작성이 되기 대문에 중복을 제거해줍니다.
                    for aday_total_log in self.temp_total_log_memory:#삭제하고 난 후에 메모리에 저장 시킨 한 줄 한 줄을 리스트로 저장한 것을 다시 한 줄 한 줄 작성을 해줍니다.
                        temp_log_file.write(aday_total_log)
                del self.temp_total_log_memory[:]#다음에 들어오게 될 경로를 사용하기 위해서 해당 메모리를 삭제해줍니다.
        return temp_log_path_list,current_log_path_list,will_del_log_path_list#리턴 값으로는 로그 파일들이 들어있는 경로의 list를 반환합니다.

    def append_log_path_list(self,log_path,log_path_list):
        log_path_list.append(log_path)
        return log_path_list
    
    def change_temp_file_to_current_file(self,temp_log_list,current_log_list,will_delete_log_list):
        for index_ in range(len(current_log_list)):
            os.rename(current_log_list[index_], will_delete_log_list[index_])  # 지금 존재하는 파일을 삭제할 파일로 변경합니다.
            os.rename(temp_log_list[index_], current_log_list[index_])  # temp파일을 존재할 파일로 이름을 변경합니다. #os.rename은 os.rename(기존 경, 바꿀 경로)입니다.
            os.remove(will_delete_log_list[index_])  # temp파일이 기존 파일로 되었다면 지우기로 할 파일을 지워줍니다.
            
    def download_folder_rename(self, argv_text):  # cmd로 받는 파일 경로를 오류없이 처리하기 위한 함수입니다.
        if(argv_text[-1]!='/'):
            print("파일 경로는 c:/example/나 /home/downloads/와 같이 /를 이용하여 합니다.")
            sys.exit()
        return argv_text
    
    def log_file_reset(self):  # 로그 파일을 작성하기 위해 폴더 및 txt파일을 만드는 함수입니다. 시작시에만 한 번 사용 되어서 초기 경로 설정을 해줍니다.     
        # 1. A=self.DOWNLOAD_FOLDER_PATH B=self.SUCCESS_LOG_FILE_PATH
        # 2. A=self.LOG_FOLDER_PATH B=self.TOTAL_LOG_FILE_PATH 
        self.some_folder_create(self.DOWNLOAD_FOLDER_PATH)                                               
        self.some_folder_create(self.LOG_FOLDER_PATH)
        self.log_file_create(self.SUCCESS_LOG_FILE_PATH)
        self.log_file_create(self.TOTAL_LOG_FILE_PATH)
        self.log_file_create(self.SEARCH_WORD_HISTORY_FILE_PATH)
         
    def some_folder_create(self, some_folder_path):  # 경로를 입력하면 그 경로에 대한 폴더를 확인하고 없다면 만듭니다.
        if os.path.isdir(some_folder_path):  # 같은 경로에 다운로드를 할 폴더가 있는지 확인합니다.
            print(some_folder_path, "에 폴더 존재")
        else:
            try:
                os.mkdir(some_folder_path)  # 해당 경로에 hwp다운로드를 담아놓는 폴더를 생성합니다.
                print('폴더 생성\n')
            except:  # 해당 경로를 가지 못 해, 폴더를 만들지 못 할 경우 일어나는 오류입니다.  
                print("폴더 생성 오류")  
   
    def log_file_create(self, some_log_file_path):  # 경로를 입력하면 해당 경로에 변수로 받은 이름을 가진 파일이 없다면 만들거나 존재한다면 확인합니다.
        with io.open(some_log_file_path, "a",encoding='utf-8-sig') as log_file_info:  # 해당 경로 밑에날짜 이름을 가진 파일을 만들어 줍니다.
            #utf-8로 파일을 저장시키기 위해서 io.open을 사용해주고 encoding='utf-8-sig'로 저장합니다.
            print("로그파일 설정\n") 
              
    def file_name_create(self, url):  # 파일의 이름을 만들어주는 함수입니다. hash를 통해서 url을 변수로 해서 받은 것을 파일 경로를 지정해줍니다.
        hash_text = hashlib.md5(url.encode("UTF-8"))  # url을 인코딩한 후에 md5 암호화 해시의 객체를 생성합니다.
        hash_title = hash_text.hexdigest()  # 생성한 객체를 16진수로 반환합니다.
        savePath = os.path.join(self.DOWNLOAD_FOLDER_PATH + hash_title + "." + self.LOG_FILE_TYPE)
        # 파일 경로+url명+file type으로 파일의 저장위치를 설정하기 위해서 os.path.join함수로 파일 이름을 만듭니다.
        time_stamp = self.file_name_check(savePath)
        # hash한 값의 이름을 가진 파일이 있는 지 확인합니다.
        # file_name_check는 return 값으로 현재 시간의 마지막 자리 네자리를 반환합니다.
        # 하지만 그 조건은 폴더에 같은 hash값을 가질 때만 이고 그 외에 return값은 ""입니다.
        if (time_stamp != ''):  # hash 값이 같은 것이 있어 time_stamp가 찍히면 새로 경로를 설정해줍니다.
            savePath = os.path.join(self.DOWNLOAD_FOLDER_PATH + hash_title + time_stamp + "." + self.LOG_FILE_TYPE)
        return savePath
        # 해당 경로에 다운받으려고 하는 파일을 받았는 지 여부에 관해서 비교합니다.
        # 해당 함수에서는 memory에 올라온 url 값을 비교하여 if / else를 통해서
        # 같은 url이 존재한다면 다운로드하지 않고 url이 존재하지 않는다면 다운로드를 합니다.
             
    def replace_safe_string(self, error_text):  # 파일 다운에 실패시 url값을 텍스트파일에 저장
        error_text = re.sub('[ㄱ-ㅣ 가-힣<>,]+', '', str(error_text))
        # 파일명에 들어가지 말아야할 특수문자들을 치환, re.sub([들어가지 말아야 할 문자],'바꿀 문자',검사 문자) 입니다.
        # [ㄱ-ㅣ 가-힣<>,]+는 ㄱ에서 ㅣ까지 가에서 힣까지 모두 콤마와 <>,까지 모두 들어갈 수 없습니다.
        return error_text
        # error_text를 return합니다.
        
    def file_name_check(self, savePath):  # 폴더 내에 똑같은 파일이 존재한다면 타임 스탬프를 붙여서 이름을 반환합니다.
        if os.path.isfile(savePath):
            time_stamp = str(time.time())[-6:-1]
            # 만약에 hash한 값의 savePath가 같다면 current타임의 시간을 뒤에다 붙여서 파일이름을 작성한다.
            return time_stamp
        return ""
    
    def file_download(self, file_path, url):  # 파일을 다운받기위한 함수입니다.
     
        if self.check_url(url):  # 같은 경로의 파일이 있는지 확인. check_url은 True와 False를 반환합니다.
            print("\n똑같은 파일 발견")
        else:                    # 만약 경로에 파일이 없다면 다운로드.
            self.DOWNLOAD_FILE_COUNT=self.DOWNLOAD_FILE_COUNT+1#다운로드 받은 갯수를 올립니다.
            success_log_text, fail_log_text = self.recode_current_time(self.TARGET_FILE_NAME,url, file_path)  # 현재 시간을 print를 사용하고, success_log_text,fail_log_text를 반환받습니다.     
            url_info = ""  # url의 정보를 출력해주기 위해서 사용합니다.
            print("다운로드 url:", str(url.encode(encoding='utf_8')))
            try:
                try:
                    url_info = urllib.request.urlopen(url, timeout=10)  # html의 정보를 얻기위한 연결해, url의 객체를 생성한다.    
                except ValueError as err:
                    url = urllib.request.quote(url, ":/")
                    # urllib.request.quote는 url을 encode하기 위해서 사용합니다.
                    # urllib.request.quote(url명, "encode하지 않을 단어")로 구성되어집니다.
                    url_info = urllib.request.urlopen(url, timeout=10)     
                
                # urllib.reqeust.urlopen(URL,[,data][,time out])으로 데이터를 보낼 수도 있으며 timeout설정을 할 수 있다.
                fname, header = urllib.request.urlretrieve(url, file_path,reporthook=self.download_report)  # 다운로드를 받고 파일의 path와 header를 반환합니다. 
                download_size = url_info.headers.get('content-length')  # 연결한 url의 객체에서 header.get(키), 키의 내용을 출력한다. #해당 라인도 value error 발생
                print("\n다운로드 size:", download_size)  # 다운받을 파일 길이 확인                                                      
                print("다운로드 path:", fname,"\n")  # 파일이름    
                self.success_log_memory.append(success_log_text)  # 오늘의 날짜를 가진 log_file에 입력하기 위한 메모리 입력
                self.success_url_memory.append(url)  # 모든 url을 갖도록 메모리를 모든 url의 메모리에 입력
                self.total_log_memory.append(success_log_text)  # 오늘의 날짜를 가진 total_log_file에 입력하기 위한 메모리 입력
        
            except (Exception,ConnectionResetError,socket.timeout, urllib.error.HTTPError, urllib.error.URLError, ssl.CertificateError, ConnectionAbortedError,ValueError) as err:
                #httplib.IncompleteRead는 http.client.IncompleteRead를 고치기 위해서 사용합니다.
                #해당 오류는 IncompleteRead(0 Bytes read)라고 뜨며 urllib.request.urlretrieve(url, file_path)에서 오류가 발생합니다.
                #urllib.request.urlopen(url, timeout=10)에서 오류가 발생합니다.
                #ConnectionResetError는 [WinError 10054] 현재 연결은 원격 호스트에 의해서 강제로 끊겼습니다. 라는 오류를 냅니다.
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
                    self.total_log_memory.append(fail_log_text + self.replace_safe_string(err) + "\n")
                    print('다운로드 error:', str(err).encode(encoding='utf_8'),"\n")
    
    def download_report(self, blocknum, blocksize, totalsize):#progress bar를 표현하는 함수입니다.
        readsofar = blocknum * blocksize #블락 사이즈와 블락 갯수를 곱하여 갖고 있는 파일 만큼을 표시합니다.
        surplus = totalsize - readsofar  #잔여량을 뽑습니다. readsofar는 항상 blocksize만큼 일정하게 더하기 때문에 totalsize보다 커집니다. 그렇기 때문에 잔여량을 저장해놓고 음수가 될 경우에 기존 totalsize에 음수량을 더해 정확한 수치를 계산합니다.
        if totalsize > 0:
            if surplus < 0:
                readsofar = readsofar + surplus
            percent = readsofar * 1e2 / totalsize
            s = "\r다운로드 prog: %5.1f%% %*d / %d" % (
                percent, len(str(totalsize)), readsofar, totalsize)
            sys.stdout.write(s)
            if readsofar >= totalsize: 
                sys.stdout.write("")
        else: 
            sys.stdout.write("\r다운로드 prog: read %d" % (readsofar))
        
    def check_last_page(self,prev_page_check_memory,current_page_check_memory):
        #copy_prev_page_to_current_page에서 얻어온 current_memory를 갖고 last_page_get_url에서 얻은 prev_page_check_memory를 비교한다.
        #이것을 비교한다는 것은 전의 url을 저장시켜놓은 current_memory와 방금의 url을 저장시켜놓은 prev_memory를 비교하는 것이다.
        if(prev_page_check_memory==current_page_check_memory):
            self.last_page_bool=True
        if(crawler.DOWNLOAD_FILE_COUNT>=crawler.DOWNLOAD_FILE_NUMBER):#
            print("크롤러 종료.")
            exit(1)
            
    def copy_prev_page_to_current_page(self,current_page_check_memory):#prev_page_memory를 current_page_memory로 저장시키는 함수, prev_page_memory또한 지운다.
        prev_page_check_memory=current_page_check_memory            #prev_page_memory를 current_page_memory에 저장시킨다.
        current_page_check_memory=[]                                   #prev_page_memory를 지운다.
        return prev_page_check_memory, current_page_check_memory    #두 개의 메모리를 리턴한다.

    def last_page_get_url(self,url,current_page_check_memory):# 마지막 받은 페이지를 입력받기위한 메모리 입력
        current_page_check_memory.append(url)                 #해당 함수는 for문 속에서 url을 하나씩 받아와서 메모리에 저장만 한다.
        
    def check_URL_params(self,query,COUNT,offset,freshness):
        #Bing함수에서 사용하는 url의 parameter들을 체크하는 것입니다.
        #가장 큰 목적은 freshness=파일의 시간순 정렬을 위해서 사용합니다.
        if(freshness.upper()=='ALL'):
            return {'q': query,'count':COUNT,'offset':offset}
        else:
            return {'q': query,'count':COUNT,'offset':offset,'freshness':freshness}
        
    def not_use_URL_to_use_URL(self,not_use_url):#해당 함수는 Bing에서만 사용되어지는 함수입니다.
        #해당 함수의 목적은 Bing에서 추출되어지는 url의 값이 실시간 값이 담겨져 있기 때문에 그 값을 제외시킨 URL을 만들기 위함입니다.
        not_use_url=re.sub("IG.+&CID=\w+","",not_use_url)#실시간 값은 IG이하 &CID이하의 문자들입니다.
        use_url=re.sub("&p=.+","",not_use_url)
        return use_url
    
    def get_URL_List_Daum(self,search_page_number):  # 다운 받아야할 사이트를 뽑아내기 위한 함수이다.
        URL_List = []  # 배열을 초기화 시킨다.
        if(self.LOG_FILE_TYPE.upper() in self.extend_filetype_list):
            target_url = "http://search.daum.net/search?nil_suggest=btn&w=web&lpp=10&q=" + self.TARGET_FILE_NAME+" "+self.LOG_FILE_TYPE + "&file_type=" + self.TARGET_FILE_TYPE + "&p=" + str(search_page_number) + "&DA=STC"
        else:
            target_url = "http://search.daum.net/search?nil_suggest=btn&w=web&lpp=10&q=" + self.TARGET_FILE_NAME + "&file_type=" + self.TARGET_FILE_TYPE + "&p=" + str(search_page_number) + "&DA=STC"
        print(target_url)
        try:
            html_data = requests.get(target_url)
        except socket.gaierror as e:
            print(e)#host의 name이 ' '일 경우에 발생합니다.
        # 내가 찾고자하는 target_url을 get한다.
        # data.text:HTML 문서 내용
        # data.headers:HTML 헤더
        soup_text = html_data.text
        # 내가 요청한 사이트의 HTML 내용을 soup_text로 넣는다.
        soup = BeautifulSoup(soup_text, "html.parser", from_encoding='utf-8')
        # urllilb.request.urlopen을 통해서 url을 오픈후 해당 html을 읽어와
        # data에 저장한 것을 Soup에 저장시킨다. 그리고 저장 내용 중에
        # =html_data의 HTML문서내용 중에서 a태그를 가진 클래스명이 f_url인 것을 뽑아낸다.
        temp_result_text = soup.find_all('div', {'id':'webdocColl'})
        #프리미엄 링크를 제외한 url을 따오기 위해서 10개의 검색결과만 나오는 부분을 1차적으로 가려냄
        result_text= temp_result_text[0].find_all('a',class_='f_url',href=True)
        # 위의 검색 결과중에 f_url에 관련된 링크만 1차적으로 걸러냄.
        # 1차적으로 걸러낸 것들은 많은 태그가 있는데 href태그만 다시 찾음.
        
        for address in result_text:
            # href태그만 찾아낸 것들 모두를 for문을 통해 각 객체의 원소들을 address에 저장해서 돌린다.
            URL_List.append(address['href'])
        # del self.get_address[0:3]#필요없는 url이 저장된 것을 삭제합니다. [0:3]은 광고 url
        if (len(result_text)!=10):#마지막 페이지의 조건은 url의 lpp의 수와 일치해야 합니다. 마지막 장 체크를 위해서 lpp의 수와 다를 때 마지막 페이지 bool을 True로 변환시킵니다.
            self.last_page_bool=True
        self.make_search_word_history_log(search_page_number,self.search_word_history_memory,"")
        return URL_List  # url 리스트를 리턴함.
    
    def get_URL_List_Bing(self,search_page_number):   
        URL_List = []  # 배열을 초기화 시킨다.
        target_url = "https://api.cognitive.microsoft.com/bing/v5.0/search"
        if(self.LOG_FILE_TYPE in self.extend_filetype_list):
            query=self.TARGET_FILE_NAME+" "+self.LOG_FILE_TYPE+" FileType:"+self.TARGET_FILE_TYPE
        else:
            query=self.TARGET_FILE_NAME+" FileType:"+self.TARGET_FILE_TYPE
        freshness=self.freshness  # 내가 검색하고자 하는 데이터의 시간순 정렬을 위해서 사용. BING에서만 사용가능한 변수. #Day,Week,Month,All
        COUNT=50#TOP=50, 화면당 출력 갯수, 최대 50까지 출력 가능.
        offset=self.offset
        payload = self.check_URL_params(query, COUNT, offset, freshness)
        #반환값 sample:{'q': query,'count':COUNT,'offset':offset, 'freshness':freshness}
        headers = {'Ocp-Apim-Subscription-Key': '2026d73832ba4415ac2f838eecc30175'}
        #키 확인 : https://www.microsoft.com/cognitive-services/en-US/subscriptions
        r = requests.get(target_url,params=payload,headers=headers)#request를 보냄, url에 변수들과 헤더에 key값을 적어서 보냄
        result_text = json.loads(r.text)#결과 값은 json으로 넘어온다.
        try:
            for url_number in range(COUNT):
                download_url=self.not_use_URL_to_use_URL(result_text['webPages']['value'][url_number]['url'])
                URL_List.append(download_url)
                #json으로 넘어온 값들 중에서 webPage의 value에 넘어온 number 중에서 url이 다운로드 받을 url을 갖고 있는곳이다.
                print(url_number)
            self.offset=str(int(self.offset)+50)
        except:
            if(self.bool_Bing_finish==True):
                sys.exit()
            self.bool_Bing_finish=True
            pass##만약에 except가 난다는 것은 더이상 웹사이트에서 출력할 것이 없다는 것을 의미하기 때문에 해당 웹크롤러만 긁고 종료해야 한다.
        self.make_search_word_history_log(search_page_number,self.search_word_history_memory,freshness)   #검색어 결과를 저장하는 로그입니다.
        return URL_List # url 리스트를 리턴함.
    
    def get_URL_List_GOOGLE(self,search_page_number):
        URL_List=[]
        day_=self.make_using_date()
        if(search_page_number==1):#start의 값은 0이면 start 변수를 없애줘야 한다. 그렇기 때문에 if문으로 처리한다.
            target_url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyCo1p1FP0qA2YRY0uJNV5RC4oF5NXfc0ec&cx=002673536718529979084:tliqfa-m8im&q='+self.TARGET_FILE_NAME+' filetype:'+self.LOG_FILE_TYPE+'&dateRestrict='+day_#'&start='+str((int(search_page_number)-1)*10)
        else:
            target_url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyCo1p1FP0qA2YRY0uJNV5RC4oF5NXfc0ec&cx=002673536718529979084:tliqfa-m8im&q='+self.TARGET_FILE_NAME+' filetype:'+self.LOG_FILE_TYPE+'&dateRestrict='+day_+'&start='+str((int(search_page_number)-1)*10)
        print(target_url)
        #filetype은 query문을 통해서 제어를 해야합니다.
        #dateRestrict는 d,w,m,y의 변수를 갖고 앞에 숫자n을 붙인다. 예를 들면 dn이면 몇 일 전까지의 결과만 출력, wn이라면 주 전까지만의 결과만 출력을 하도록 한다.
        #cx는 검색엔진의 ID를 뜻합니다. https://cse.google.com/cse에서 결과값을 얻어올 수 있습니다.
        #검색엔진 수정-> 만들어진 엔진 -> 설정 -> 세부정보 -> 검색 엔진 ID
        #key는 사용자인증정보입니다. https://console.developers.google.com/apis/credentials에서 API키값입니다.
        #결과값은 json으로 오기때문에 json으로 처리를 해주어야합니다.
        #the API provides 100 search queries per day for free. Additional requests cost $5 per 1000 queries, up to 10k queries per day.
        #하루에 100쿼리, num=화면당 출력할 수 있는 갯수는 10개까지 입니다.
        #따라서 하루에 처리할 수 있는 최대의 처리량은 1000개가 될 수 있습니다.
        #params 정보:https://developers.google.com/custom-search/json-api/v1/reference/cse/list
        html_data = requests.get(target_url)
        soup_text = html_data.text
        if(html_data.status_code==403):#403에러는 인증에러 or 하루 쿼리양을 다 썼을 때 일어난다.
            json_soup=json.loads(soup_text)#결과 값은 json으로 넘어온다.
            print(json_soup['error']['message'])
            exit(1)
        # 내가 요청한 사이트의 HTML 내용을 soup_text로 넣는다.
        soup = BeautifulSoup(soup_text, "html.parser")
        soup=str(soup)
        find_result=re.findall('"link":.+"',soup)#원래는 josn으로 파싱을 해야하지만 넘어오는 html에 오류가 종종 있어서 정규식표현을 통해서 link를 파싱합니다.
        for index_ in range(len(find_result)):#위의 결과에서 얻은 배열값을 불러냅니다.
            split_find_results=find_result[index_].split(': ')#"link" : "http://example.com/"으로 오기 떄문에 ": "로 구간을 나눠줍니다.
            split_find_result=split_find_results[1].replace('"','')
            URL_List.append(split_find_result)#split_find_result에는 리스트로 1번인덱스에 링크가 옵니다.
        #002673536718529979084:tliqfa-m8im  ::::cx1
        #AIzaSyCo1p1FP0qA2YRY0uJNV5RC4oF5NXfc0ec  :::key1
        #010368119512456933412:-ffgk5pq_ym ::::cx2
        #AIzaSyDDzNkCDfq8HTVZJyzyXzB0QPZcKgReCj0 :::key2
        #100쿼리라면 제한을 받을 일이 없음.
        self.make_search_word_history_log(search_page_number,self.search_word_history_memory,self.freshness)   #검색어 결과를 저장하는 로그입니다.
        if (len(URL_List)!=10):#마지막 페이지의 조건은 url의 lpp의 수와 일치해야 합니다. 마지막 장 체크를 위해서 lpp의 수와 다를 때 마지막 페이지 bool을 True로 변환시킵니다.
            self.last_page_bool=True
        return URL_List
    
    def make_using_date(self):
        if(self.freshness.upper()=='DAY'):
            return 'd1'
        elif(self.freshness.upper()=='WEEK'):
            return 'w1'
        elif(self.freshness.upper()=='MONTH'):
            return 'm1'
        elif(self.freshness.upper()=='ALL'):
            return 'y100'    
    def extract_random_text(self):
        url='http://m.naver.com/'#naver url을 에서 
        naver_html=self.make_url_html(url)#naver url의 html을 생성합니다.
        data_news_html=naver_html.findAll('a',{'data-area':'NEWS'})#a 태그 이하의 data-area가 NEWS인 구역에서
        random_text_list=[]                                        #random_text_list를 생성합니다.
        for a in range(len(data_news_html)):                       #a 태그 이하의 data-area가 잡히는 갯수에 따라서
            random_text_list.append(data_news_html[a].get_text())  #random_text_list에 data-area의 news구역의 텍스트를 append시킵니다.
        random.shuffle(random_text_list)                           #random_text_list를 뒤섞은 후에
        unsafe_word_list=self.slice_list_text(random_text_list)           #random_text_list에서 단어만 갖고 있는 list를 뽑아냅니다.
        safe_word_list=self.change_unsafe_word_to_safe_word(unsafe_word_list)
        if(safe_word_list[0]!=''):
            return safe_word_list[0]                                       #word_list에 15번째에 있는 원소 아무거나를 리턴합니다. 해당 변수는 검색어로 사용됩니다.
        else:
            return(safe_word_list[15])
        
    def slice_list_text(self,list_):
        #extract_random_text에서 list들에는 문장들만 들어있습니다.
        #그렇기 때문에 그 문장들을 스페이스바 단위로 하여 split을 하고 나온 단어들을 word_list라는 곳에 집어넣고
        #중복된 값이 없는지 검사해서 리턴해줍니다.
        word_list=[]
        for text_list_in_list in list_:
            for text_in_text_list_ln_list in text_list_in_list.split(' '):
                text_in_text_list_ln_list=re.sub("[\s,\'\"\n]|","",text_in_text_list_ln_list)
                word_list.append(text_in_text_list_ln_list)
        word_list=self.remove_overlap(word_list)
        return word_list
    
    def remove_overlap(self,memory):#중복제거, set으로 바꾸고 list로 전환
        list_memory=list(OrderedDict.fromkeys(memory))
        return list_memory
    
    def change_unsafe_word_to_safe_word(self,unsafe_word_list):
        #사용하지 말아야할 단어들을 안전한 단어로 바꿔준다.
        safe_word_list=[]
        for unsafe_word in unsafe_word_list:
            safe_word_list.append(re.sub("[^0-9,.ㄱ-ㅣ가-힣a-zA-Z]","",unsafe_word))
        for index_ in range(len(safe_word_list)):
            try:
                if(safe_word_list[index_]==''):
                    del safe_word_list[index_]
            except:
                pass
        return safe_word_list
    
    def make_url_html(self, search_url):#url이 입력되면 해당 url의 html을 생성하고 리턴합니다.
        try:
            html_data = requests.get(search_url, self.HEADER)
            if(html_data.status_code==403):
                print("403 Error!!!\n")
                print("다시 실행해주세요.")
                exit(1)
        except socket.gaierror as e:
            print(e)
        soup_text = html_data.text
        html_soup = BeautifulSoup(soup_text, "html.parser")
        return html_soup
    
    def find_search_history_log(self,log_folder_path):
        #log폴더 내에 search_log를 가져오는 함수입니다.
        log_folder_path_list=os.listdir(log_folder_path)#로그 폴더에 있는 파일들을 리스트로 받는다.
        temp_use_index_list=[]
        use_index_list=[]
        use_log_list=[]
        for index_ in range(len(log_folder_path_list)):#로그 폴더에 있는 파일들의 갯수만큼 index로 잡아준다.
            if('search' in log_folder_path_list[index_]):#파일 명에 search가 들어간다면 list로 넣는다.
                temp_use_index_list.append(index_)
        for index_ in temp_use_index_list:
            log_born_day=self.make_date_info(str(log_folder_path_list[index_][0:10]))#로그가 생성된 날을 date자료형으로 가져온다.
            today_Ymd=self.make_date_info(self.today_Ymd)                       #오늘의 날짜를 date자료형으로 가져온다.
            before_week_day=today_Ymd-datetime.timedelta(7)                     #1주일 전의 날짜를 date자료형으로 가져온다.
            if(log_born_day>=before_week_day):                                  #로그가 만들어진 날이 1주일 안이라면 리스트에 넣는다.
                use_index_list.append(index_)
        for index_ in use_index_list:
            use_log_list.append(log_folder_path_list[index_])
        return use_log_list
        
    def check_already_search_word(self,log_folder_path_list,search_word,search_site,search_type,already_search_word_bool):
        #이미 사용한 검색어인지 검사하는 함수입니다. 
        for index_ in range(len(log_folder_path_list)):
            with open(crawler.LOG_FOLDER_PATH+log_folder_path_list[index_],"r",encoding='utf-8') as log_file:
                log_file_readlines= log_file.readlines()
                for log_text_line in log_file_readlines:
                    split_log_text=log_text_line.split('\t')
                    if(search_site in split_log_text[1] and search_word in split_log_text[2] and search_type in split_log_text[3]):
                        already_search_word_bool=True
        return already_search_word_bool
              
    def make_date_info(self,string_day):
        try:
            split_date=string_day.split('-')
            target_day=datetime.date(int(split_date[0]),int(split_date[1]),int(split_date[2]))
            return target_day
        except:
            return 

    
crawler = crawler_()  # crawler객체를 생성해줍니다.    
current_page_check_memory=[]#현재 돌고 있는 for문에서 다운 받은 url을 리스트로 저장합니다.
prev_page_check_memory=[]   #이전에 돌았던 for문에서 다운 받은 url을 리스트로 저장합니다.
for infinit in range(9999):
    if(crawler.AUTO_CHECK==True):
        already_search_word_bool=False
        safe_word=crawler.extract_random_text()
        crawler.TARGET_FILE_NAME=safe_word
        log_folder_path_list=crawler.find_search_history_log(crawler.LOG_FOLDER_PATH)
        already_search_word_bool=crawler.check_already_search_word(log_folder_path_list, safe_word, crawler.crawler_choice, crawler.LOG_FILE_TYPE,already_search_word_bool)
    for search_page_number in range(1,1000):#페이지수가 넘어가게함.
        try:
            if(already_search_word_bool==True):
                break
        except NameError as e:pass
        #크롤러의 시간,크롤러의 사이트,검색어,페이지를 저장하는 변수이다.
        print("next page")
        if(crawler.crawler_choice.upper()=='DAUM'):
            target_urls = crawler.get_URL_List_Daum(search_page_number)#해당 함수를 거쳐서 다운로드 할 url 리스트를 받아옵니다.
        elif(crawler.crawler_choice.upper()=='BING'):
            target_urls = crawler.get_URL_List_Bing(search_page_number)#해당 함수를 거쳐서 다운로드 할 url 리스트를 받아옵니다.     
        elif(crawler.crawler_choice.upper()=='GOOGLE'):
            target_urls = crawler.get_URL_List_GOOGLE(search_page_number)#해당 함수를 거쳐서 다운로드 할 url 리스트를 받아옵니다.     
        prev_page_check_memory, current_page_check_memory = crawler.copy_prev_page_to_current_page(current_page_check_memory)
        
        #current_page_check_memory를 변수로 집어넣습니다. prev_page에 current_page를 넣고 current_page를 비워줍니다.
        #그리고 prev_page와 current_page를 반환받습니다. 
        for slice_url in target_urls:       # list로 얻은 url의 값을 하나씩 돌린다.
            savePath = crawler.file_name_create(slice_url)  # 파일의 이름을 만들어주는 함수입니다. hash를 통해서 url을 변수로 해서 받은 것을 파일 경로를 지정해줍니다. 
            crawler.file_download(savePath, slice_url)      # 파일을 다운받기위한 함수입니다.
            crawler.last_page_get_url(slice_url,current_page_check_memory)            #마지막 페이지를 구하기 위해서 페이지의 url을 한 장 단위로 가져오는 함수입니다.  
        crawler.atomic_create_file(crawler.SUCCESS_LOG_FILE_PATH, crawler.success_log_temp_file_path, crawler.success_log_will_delete_file_path, crawler.success_log_memory)
        crawler.atomic_create_file(crawler.TOTAL_LOG_FILE_PATH, crawler.total_log_temp_file_path, crawler.total_log_will_delete_file_path, crawler.total_log_memory)
        crawler.atomic_create_file(crawler.SEARCH_WORD_HISTORY_FILE_PATH,crawler.search_word_history_temp_file_path,crawler.search_word_history_delete_file_path,crawler.search_word_history_memory)
        # 얻은 url에 관련된 로그를 작성하는 것을 안정성있게 하기위해서 atomic create file을 하는 함수입니다.
        # 해당 함수는 로그파일의 이름과 로그파일의 경로를 입력하게 되면 로그의 temp파일과 삭제할 로그파일을 만듭니다.
        # temp파일에 url을 작성합니다.
        # 기존의 로그파일을 삭제할 로그파일로 변경하면 temp파일을 기존의 로그파일로 변경하고 기존의 로그파일은 삭제합니다.
        crawler.check_last_page(prev_page_check_memory,current_page_check_memory)         # 마지막 페이지 url을 가져오면 list를 비교합니다.
        if(crawler.last_page_bool==True): #마지막페이지의 조건은 1. url의 갯수가 lpp의 갯수와 다를 경우, 2. 지난 번에 받은 파일과 이번에 받은 파일이 같을 경우입니다.
            if(crawler.AUTO_CHECK==False):#auto를 입력안했을 경우에 정상 종료, auto를 입력시에는 다음 검색어 검사
                print("크롤러 종료.")
                exit(1)
            crawler.last_page_bool=False  #auto가 아닐경우엔 다시 False로 돌리고 break을 시켜서 해당 for문을 빠져나옵니다.
            break
        
    print("크롤링 종료")