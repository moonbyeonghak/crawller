'''
Created on 2016. 10. 26.

@author: moon
'''
import requests#url 정보를 받아오기 위해서 사용.
from bs4 import BeautifulSoup#html을 파싱하기위해서 사용하는 lib
import re #url을 재조합하기 위해서 사용하는 lib
import os #폴더를 만들기위해서 사용하는 변수
from sys import argv #argv 제어.

class text_crawler:
    def __init__(self):#생성자
        print("hello? I'm text_crawler.")
    def making_url(self,query,start):#url을 만드는 매소드
        url="https://m.search.naver.com/search.naver?where=m_blog&query="+query+"&display=15&mtb_srt&nso=so%3Add&start="+start
        return url
    def html_find(self,url):#html을 가져오는 매소드
        #url구조 : https://m.search.naver.com/search.naver?where=m_blog&query=%EC%95%88%EB%85%95&display=15&mtb_srt&nso=so%3Ar
        #&query=검색어,&display=웹페이지에 출력할 결과물 갯수,&nso=so%3Add은  최신순으로 검색, &nso=so%3Ar은 정확성 순으로 검색.
        blog_find_results_object=requests.get(url)#블로그 검색결과 화면을 html객체로 가져옴.
        blog_find_results_html=blog_find_results_object.text#객체를 생성한 것을 기반으로 html을 만들어줌
        return blog_find_results_html
    def making_bs_text(self,html):
        bs_text=BeautifulSoup(html,'html.parser')
        html_tags=bs_text.findAll(class_='total_wrap',href=True)
        return html_tags
    def find_postct_bs_text(self,html):
        bs_text=BeautifulSoup(html,'html.parser')
        html_tags=bs_text.findAll(class_='post_ct  ')
        try:
            html_tags=html_tags[0]
            texts=html_tags.get_text()
            return texts
        except:
            html_tags=bs_text.findAll(class_='se_textarea')
            texts=""
            for tag in html_tags:
                text=tag.get_text()
                texts=texts+text+"\n"
            return texts
        return html_tags
    def making_blog_url_list(self,html_tags):
        url_list=[]
        for blog_index in range(len(html_tags)):
            if('blog.naver.com/' in html_tags[blog_index]['href']):
                url_list.append(html_tags[blog_index]['href'])
        return url_list
print("크롤러 :::: 파일명.py -query 검색어")
query=input("검색할 검색어를 입력하세요: ")
folder_path=input('example:c:/aaa/ 저장할 경로를 입력하세요: ') 
try:
    os.mkdir(folder_path)
    print("폴더를 생성하셨습니다.")
except:
    print("이미 폴더가 존재합니다.")
    pass
start=1
text_crawler=text_crawler()
temp_url_list=[]
for number in range(100):
    start=1+(number*15)
    print("현재query: ",query)
    print("현재start: ",start)
    blog_find_results_url=text_crawler.making_url(query,str(start))#url조합하는 매소드에 query와 start param을 집어넣음.
    print(blog_find_results_url)
    blog_find_results_html=text_crawler.html_find(blog_find_results_url)#네이버 블로그 검색 결과들의 html을 가져옴.
    html_tags=text_crawler.making_bs_text(blog_find_results_html)#얻어온 html을 slice함
    url_list=text_crawler.making_blog_url_list(html_tags)#slice한 html을 통해서 url을 찾아냄
    if(temp_url_list==url_list and temp_url_list[0]!=""): #temp_url_list와 현재의 list가 같다면 종료.
        exit(1)
    for blog_url in url_list:#url리스트들을 하나씩 뽑아냄.
        file_name=re.sub("[/:.]","",blog_url)
        print(os.path.isfile(str(folder_path)+str(file_name)+'.txt'))
        if (os.path.isfile(str(folder_path)+str(file_name)+'.txt')):#존재하지 않는다면
            print(file_name,"은 이미 검색하셨습니다.")
        else:    
            print(blog_url,"을 검색하고 있습니다.")
            blog_post_html=text_crawler.html_find(blog_url)
            get_texts=text_crawler.find_postct_bs_text(blog_post_html)
            with open(str(folder_path)+str(file_name)+'.txt','w',encoding='utf-8') as write_ob:
                write_ob.write(get_texts)
    temp_url_list=url_list
