#!/usr/bin/env python


import subprocess
import threading
import re

""" Tools to ping many machines effectively. 
    Inspired by blog.boa.nu

    by Andrew Pedelty
"""


class Pinger(object): 
    """ 
    Use me to quickly find the ips associated with hostnames. 
    """
    status = {'good': [], 'bad': []} # Populate and return
    hostlist = [] # Global queue to avoid mutex issues
    lock = threading.Lock()
    ipfinder = re.compile(r"^.*?\((.*?)\)")

    def __init__(self, hosts, maxthreads=10, debug=False): 
        self.hostlist = hosts 
        self.max_threads = maxthreads
        self.debugging = debug

    def ping(self, host): 
        try: 
            pingresponse = subprocess.check_output(['ping', '-c', '1', '-W', '1', host], 
                                                   stderr=open('/dev/null', 'w'))
            address = self.ipfinder.search(pingresponse).group(1)
            return (host, address)
        except subprocess.CalledProcessError as e: 
            return (host, None)
        # -c1 means to send 1 ping, -W1 means to wait at most 1 second before timing out. 

    def next_hostname(self): 
        host = ""
        self.lock.acquire()
        if self.hostlist: 
            host = self.hostlist.pop()
        self.lock.release()
        return host

    def populate_status(self): 
        while 1: 
            host = self.next_hostname()
            if not host: 
                return None
            pingval = self.ping(host)
            if pingval[1] == None: 
                self.status['bad'].append(host)
            else: 
                self.status['good'].append(pingval)

    def go(self): 
        threadlist = []

        # Start max_threads threads to goin, each eaing at the same queue: 
        for i in range(self.max_threads): 
            thread = threading.Thread(target=self.populate_status)
            thread.start()
            threadlist.append(thread)

        wait = [t.join() for t in threadlist]
        if self.debugging: 
            print wait

        return self.status

if __name__ == "__main__": 
    print "Not to be called as a standalone script." 

