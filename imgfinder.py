#!/usr/bin/python
#-*- coding: Utf-8 -*-

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener
from urllib import urlencode
from urllib2 import HTTPError
from reddit import Reddit
from json import loads
import time
import sys
reload(sys)
sys.setdefaultencoding( "Utf-8" )

USERNAME = "xxx"
PASSWORD = "xxx"

def find_digit(msg):
        msg = msg.split()
        for d in msg:
                if d.isdigit():
                        return int(d)


def url_data(url, json=False):
        opener = build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
                j_opener = opener.open(url)
                j_resp = j_opener.read()
                j_opener.close()
                if json == True:
                        return loads(j_resp)
                else:
                        return j_resp
        except HTTPError, e:
                print "Http Error", str(e.code)
                time.sleep(4)
                url_data(url, params, url_type)

def karmadecay(i_url):
        k_url = "http://karmadecay.com/" + i_url
        k_data = url_data(k_url)
        dups = []

        if "No very similar images were found" not in k_data:
                if "very similar images" in k_data:
                        k_soup = BeautifulSoup(k_data)
                        #iterate over entire result list
                        tr_result = k_soup("td", {"class":"info"})
                        for i in range(1, len(tr_result)):  
                                tr = tr_result[i]
                                votes = tr("div",{"class":"votes"})[0].text
                                try:
                                        similarity = tr("span", {"class":"fr"})[0].text

                                        #skipping amazon ads and less similar results

                                        if ("Over" not in votes) and ("similar" in similarity):
                                                submitted = tr("div",{"class":"submitted"})[0].text
                                                a_tag =  tr.find('a')
                                                a_text = a_tag.text
                                                a_href = a_tag['href']
                                                #print i, ". ", a_text, "---> ", votes, similarity
                                                dups.append({'link':a_href,'title':a_text, "submission_date":submitted, "votes":votes, "similarity":similarity})
                                        else:
                                                pass
                                except IndexError, e:
                                        pass

                        
                else:
                        pass
        else:
                print "No Similar images found"
                pass       
        return dups
def form_comment(repost):
        comment = "Previously on lost:\n\n"
        for rep in repost:
                #print rep['submission_date'], "\n--------------------------------------"
                submitted = rep['submission_date']\
                .replace('\n','')\
                .replace('            submitted                            ', '^submitted ^')\
                .replace(' ago                        by                             ', ' ^ago ^by ^/u/')\
                .replace('                [deleted]                                    to /r',' ^[deleted] ^to ^/r')\
                .replace('                                                    to /r',' ^to ^/r')\
                .replace('hour', '^hour')\
                .replace('day', '^day')\
                .replace('minute', '^minute')\
                .replace('second', '^second')\
                .replace('month', '^month')\
                .replace('year', '^year')
                comment += """##[%s](%s)\n\n%s ^| ^%s ^| ^%s \n\n""" %(rep['title'], rep['link'], submitted, rep['votes'].replace('points','^points').replace('\n','').replace('update pending', '^update ^pending'), rep['similarity'].replace('similar', ' ^similar'))
        return comment


def main(subreddit):
        print "Subreddit :", subreddit
        rsub = url_data("http://www.reddit.com/r/%s/new/.json?sort=new"%subreddit, json=True)
        children = rsub['data']['children']
        r = Reddit(USERNAME, PASSWORD)
        session = r.login()
        f = open('history.txt', 'r')
        history = f.read()
        f.close()
        for child in children:
                is_self = child['data']['is_self']
                thread_id = child['data']['name']
                print thread_id
                if thread_id in history:
                        print "Thread: %s already in history"%thread_id
                        pass

                else:
                        if not is_self:
                                img_url = child['data']['url']
                                thread_id = child['data']['name']
                                repost = karmadecay(img_url)
                                if repost:
                                        text = form_comment(repost)
                                        r_resp = r.post(session, thread_id, text) 
                                        if r_resp != None:
                                                error = r_resp['json']['errors']
                                                delay = find_digit(error[0][1])
                                                print "waiting: %s seconds" %delay*60
                                                time.sleep(delay*60) 
                                                r.post(session, thread_id, text) 
                                        f = open('history.txt', 'a')
                                        f.write("\n%s"%thread_id)
                                        print text
                                        f.close()
                                        time.sleep(1)
                                        print "Comment Posted:", thread_id 
                                else:
                                        pass
                        else:
                                pass
        print "Finished"
        return


if __name__ == "__main__":
        try:
                sys.argv[1]
                print "Queued subreddits %s:" %[i for i in sys.argv if i != sys.argv[0]]
                for i in range(1,len(sys.argv)):
                        main(sys.argv[i])
        except IndexError:
                print "\nPlease specify subreddit(s) name separated by a space. Example:\n python imgfinder.py funny pics wtf\n"                           