# -*- coding:utf-8 -*-

import urllib
import urllib2
import re
import tool
import os
import Queue
import sys
import requests
import threading
import time
import datetime
import codecs

reload(sys)
sys.setdefaultencoding("utf-8")


class Spider:

    #页面初始化
    def __init__(self):
        self.siteURL = 'http://www.cijichina.com'
        self.baseURL = 'http://www.cijichina.com/search/agent.html?tag='
        self.tool = tool.Tool()

    #获取页面的内容
    def getPage(self,name):
        url = self.baseURL + urllib.quote(name.encode('UTF-8'))
        print u'Request url:' + url
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        return response.read().decode('UTF-8')

    #获取详细信息
    def getContents(self,name):
        page = self.getPage(name)
		
        flag = re.findall(u'查无此人',page,re.S)
        if(len(flag)>=1):
        	print u'None'
        	return False
        else:
        	# print name + ' exists!'
        
        	pattern = re.compile(u'<span><img src="(.*?)".*?<p>身份证号：(.*?)</p>.*?<p>微信号：(.*?)</p>',re.S)
        	items = re.findall(pattern,page)
        	print items			
        	contents = []
        	for item in items:
        		contents.append([item[0],item[1],item[2]])
        	return contents


    #保存个人简介
    def saveBrief(self,content,name,id):
		# 有些身份证id内容是*，而*不能创建文件，所以替换了一下
        id = id.replace('*','k')
        fileName = name + "/" + str(id) + ".txt"
        print u"正在保存信息：",fileName
        f = open(fileName,"w+")
        f.write(str(content))


    #传入图片地址，文件名，保存单张图片
    def saveImg(self,imageURL,name,id):
        try:
 		# 有些身份证id内容是*，而*不能创建文件，所以替换了一下
            id = id.replace('*','k')           
            u = urllib.urlopen(self.siteURL + imageURL)
            data = u.read()
            filename = name + r"/" + str(id) + ".jpg"
            print u"正在保存图片：",filename
            f = open(filename, 'wb')
            f.write(data)

            f.close()
        except:
            print u"保存失败"

    #创建新目录
    def mkdir(self,path):
        path = path.strip()
        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists=os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            print u"新建了",path,u'的文件夹'
            # 创建目录操作函数
            os.makedirs(path)
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            print u"名为",path,'的文件夹已经创建成功'
            return False

    #将信息保存起来
    def start(self,name):
        
        contents = self.getContents(name)
        if contents != False:
        	self.mkdir(name)
        	for items in contents:
        		self.saveImg(items[0],name,items[1])
        		self.saveBrief(items,name,items[1])


class Worker(threading.Thread):    # 处理工作请求
    def __init__(self, workQueue, resultQueue, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue


    def run(self):
        while 1:
            try:
                callable, args, kwds = self.workQueue.get(False)    # get task
                res = callable(*args, **kwds)
                self.resultQueue.put(res)    # put result
            except Queue.Empty:
                break

class WorkManager:    # 线程池管理,创建
    def __init__(self, num_of_workers=10):
        self.workQueue = Queue.Queue()    # 请求队列
        self.resultQueue = Queue.Queue()    # 输出结果的队列
        self.workers = []
        self._recruitThreads(num_of_workers)

    def _recruitThreads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.workQueue, self.resultQueue)    # 创建工作线程
            self.workers.append(worker)    # 加入到线程队列


    def start(self):
        for w in self.workers:
            w.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()    # 从池中取出一个线程处理请求
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append(worker)    # 重新加入线程池中
        print 'All jobs were complete.'


    def add_job(self, callable, *args, **kwds):
        self.workQueue.put((callable, args, kwds))    # 向工作队列中加入请求

    def get_result(self, *args, **kwds):
        return self.resultQueue.get(*args, **kwds)


def download_file(name):
    spider.start(name)

def main():

    try:
        num_of_threads = int(sys.argv[1])
    except:
        num_of_threads = 100
    _st = time.time()
    wm = WorkManager(num_of_threads)
    print num_of_threads
	
	
    file = codecs.open('name_cn.txt','r','utf-8')
	
    
    while 1:
        line = file.readline()
        if not line:
            break
        line=line.strip('\n')
        line=line.strip('\r')
        wm.add_job(download_file, line)


    wm.start()
    wm.wait_for_complete()
    print time.time() - _st
    file.close()


if __name__ == '__main__':
	spider = Spider()
	#spider.start(u'丁凤')
	main()



