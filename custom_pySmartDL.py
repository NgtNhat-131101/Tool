import os
import sys
import urllib.request, urllib.error, urllib.parse
import copy
import threading
import time
import math
import tempfile
import base64
import hashlib
import socket
import logging
from io import StringIO
import multiprocessing.dummy as multiprocessing
from ctypes import c_int

import os
import sys
import urllib.request, urllib.parse, urllib.error
import random
import logging
import re
from concurrent import futures
from math import log
import shutil

DEFAULT_LOGGER_CREATED = False

def combine_files(parts, dest, chunkSize = 1024 * 1024 * 4):
	'''
	Combines files.
    Hàm thực hiện việc kết hợp tệp theo từng khối (chunks), 
    giúp tránh các vấn đề liên quan đến bộ nhớ khi xử lý các tệp lớn.

	:param parts: Source files. 
	:type parts: list of strings
    ``Danh sách`` các chuỗi đại diện cho đường dẫn của tập nguồn cần kết hợp
    
	:param dest: Destination file.
	:type dest: string
    ``chuỗi`` đại diện cho đường dẫn của tệp đích
    
    :param chunkSize: Fetching chunk size.
	:type chunkSize: int
    một tham số tùy chọn (mặc định là 4MB) 
    xác định kích thước của mỗi khối dữ liệu được đọc và ghi vào tệp đích.

	'''
	if len(parts) == 1:
		shutil.move(parts[0], dest)
    # Nếu chỉ có 1 chuỗi thì ghi thẳng vô tệp đích
	else:
		with open(dest, 'wb') as output:
      #hàm sẽ mở tệp đích dưới chế độ ghi nhị phân
			for part in parts:
       #Đọc từng tệp trong nhiều tệp
				with open(part, 'rb') as input:
					data = input.read(chunkSize)
					while data:
						output.write(data)
						data = input.read(chunkSize)
				os.remove(part)
            
def url_fix(s, charset='utf-8'):
    """
    Hàm này được sử dụng để "sửa lỗi" một URL đã được nhập bởi người dùng
    và chứa các ký tự không hợp lệ hoặc không an toàn. 
    Việc sửa lỗi này thực hiện dựa trên cách mà các trình duyệt web 
    thường xử lý dữ liệu người dùng nhập vào. 
    Điều này đảm bảo URL được mã hóa chính xác và không gây ra lỗi khi gửi yêu cầu tới máy chủ.
    """
    '''
    Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    >>> url_fix(u'http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param s: Url address.
    :type s: string
    :param charset: The target charset for the URL if the url was
                    given as unicode string. Default is 'utf-8'.
    :type charset: string
    :rtype: string
                    
    (taken from `werkzeug.utils <http://werkzeug.pocoo.org/docs/utils/>`_)
    '''
    scheme, netloc, path, qs, anchor = urllib.parse.urlsplit(s)
    path = urllib.parse.quote(path, '/%')
    qs = urllib.parse.quote_plus(qs, ':&=')
    return urllib.parse.urlunsplit((scheme, netloc, path, qs, anchor))
    
def progress_bar(progress, length=20):
    """
    được sử dụng để tạo một thanh tiến trình văn bản (textual progress bar) dưới dạng chuỗi. 
    Thanh tiến trình này sẽ thể hiện một số lượng tiến trình đã hoàn thành 
    trong tổng số tiến trình cần thực hiện.
    """
    '''
    Returns a textual progress bar.
    
    >>> progress_bar(0.6)
    '[##########--------]'
    
    :param progress: Number between 0 and 1 describes the progress.
    :type progress: float
    :param length: The length of the progress bar in chars. Default is 20.
    :type length: int
    :rtype: string
    '''
    length -= 2  # The brackets are 2 chars long.
    if progress < 0:
        progress = 0
    if progress > 1:
        progress = 1
    return "[" + "#"*int(progress*length) + "-"*(length-int(progress*length)) + "]"
    
def is_HTTPRange_supported(url, timeout=15):
    """
    được sử dụng để kiểm tra xem một máy chủ (server) có hỗ trợ tính năng "Byte serving" hay không. 
    "Byte serving" là một tính năng của HTTP cho phép máy chủ trả về chỉ một phần của tệp (file) 
    thay vì toàn bộ tệp khi được yêu cầu bởi trình duyệt hoặc ứng dụng. 
    Điều này hữu ích khi cần tải một phần nhỏ của tệp, đặc biệt là khi xử lý các tệp lớn.
    """
    '''
    Checks if a server allows `Byte serving <https://en.wikipedia.org/wiki/Byte_serving>`_,
    using the Range HTTP request header and the Accept-Ranges and Content-Range HTTP response headers.
    
    :param url: Url address.
    :type url: string
    :param timeout: Timeout in seconds. Default is 15.
    :type timeout: int
    :rtype: bool
    '''
    url = url.replace(' ', '%20')
    
    fullsize = get_filesize(url)
    if not fullsize:
        return False
    
    headers = {'Range': 'bytes=0-3'}
    req = urllib.request.Request(url, headers=headers)
    urlObj = urllib.request.urlopen(req, timeout=timeout)
    filesize = int(urlObj.headers["Content-Length"])
    
    urlObj.close()
    return filesize != fullsize

def get_filesize(url, timeout=15):
    """
    được sử dụng để lấy kích thước (dung lượng) của một tệp tin qua giao thức HTTP. 
    Điều này cho phép xác định kích thước của tệp trước khi tải về hoặc
    để kiểm tra kích thước tệp trên máy chủ từ xa.
    ==================================================================================================
    Hàm trả về kích thước của tệp (file size) dưới dạng số nguyên biểu diễn dung lượng tệp trong đơn vị byte. 
    Nếu không thể lấy kích thước của tệp, hàm sẽ trả về giá trị 0.
    ==================================================================================================
    url: Địa chỉ URL của tệp cần lấy kích thước.
    timeout: Thời gian chờ tối đa (đơn vị là giây) cho yêu cầu. Giá trị mặc định là 15 giây.
    """
    '''
    Fetches file's size of a file over HTTP.
    
    :param url: Url address.
    :type url: string
    :param timeout: Timeout in seconds. Default is 15.
    :type timeout: int
    :returns: Size in bytes.
    :rtype: int
    '''
    try:
        urlObj = urllib.request.urlopen(url, timeout=timeout)
        file_size = int(urlObj.headers["Content-Length"])
    except (IndexError, KeyError, TypeError, urllib.error.HTTPError, urllib.error.URLError):
        return 0
        
    return file_size
    
def get_random_useragent():
    """
    được sử dụng để lấy một user-agent ngẫu nhiên từ danh sách các user-agent phổ biến. 
    User-agent là một chuỗi định danh được gửi từ trình duyệt của người dùng tới máy chủ web 
    khi người dùng truy cập vào một trang web. Thông tin này thường được sử dụng bởi máy chủ 
    để nhận biết trình duyệt và hệ điều hành mà người dùng đang sử dụng.
    """
    '''
    Returns a random popular user-agent.
    Taken from `here <http://techblog.willshouse.com/2012/01/03/most-common-user-agents/>`_, last updated on 2019/02/17.
    
    :returns: user-agent
    :rtype: string
    '''
    l = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
	]
    return random.choice(l)

def sizeof_human(num):
    """
    được sử dụng để định dạng kích thước file dưới dạng dễ đọc, 
    theo đơn vị kích thước thường được sử dụng bởi con người như 
    "kB" (kilobyte), "MB" (megabyte), "GB" (gigabyte),...
    """
    '''
    Human-readable formatting for filesizes. Taken from `here <http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size>`_.
    
    >>> sizeof_human(175799789)
    '167.7 MB'
    
    :param num: Size in bytes.
    :type num: int
    
    :rtype: string
    '''
    unit_list = list(zip(['B', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2]))
    
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        
        format_string = '{:,.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
            
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

def time_human(duration, fmt_short=False, show_ms=False):
    """
    được sử dụng để định dạng thời gian dưới dạng dễ đọc, thích hợp cho hiển thị cho người dùng.
    """
    '''
    Human-readable formatting for timing. Based on code from `here <http://stackoverflow.com/questions/6574329/how-can-i-produce-a-human-readable-difference-when-subtracting-two-unix-timestam>`_.
    
    >>> time_human(175799789)
    '6 years, 2 weeks, 4 days, 17 hours, 16 minutes, 29 seconds'
    >>> time_human(589, fmt_short=True)
    '9m49s'
    
    :param duration: Duration in seconds.
    :type duration: int/float
    :param fmt_short: Format as a short string (`47s` instead of `47 seconds`)
    :type fmt_short: bool
    :param show_ms: Specify milliseconds in the string.
    :type show_ms: bool
    :rtype: string
    '''
    ms = int(duration % 1 * 1000)
    duration = int(duration)
    if duration == 0 and (not show_ms or ms == 0):
        return "0s" if fmt_short else "0 seconds"
            
    INTERVALS = [1, 60, 3600, 86400, 604800, 2419200, 29030400]
    if fmt_short:
        NAMES = ['s'*2, 'm'*2, 'h'*2, 'd'*2, 'w'*2, 'y'*2]
    else:
        NAMES = [
            ('second', 'seconds'),
            ('minute', 'minutes'),
            ('hour', 'hours'),
            ('day', 'days'),
            ('week', 'weeks'),
            ('month', 'months'),
            ('year', 'years')
        ]
    
    result = []
    
    for i in range(len(NAMES)-1, -1, -1):
        a = duration // INTERVALS[i]
        if a > 0:
            result.append( (a, NAMES[i][1 % a]) )
            duration -= a * INTERVALS[i]

    if show_ms and ms > 0:
        result.append((ms, "ms" if fmt_short else "milliseconds"))
    
    if fmt_short:
        return "".join(["%s%s" % x for x in result])
    return ", ".join(["%s %s" % x for x in result])
    
def create_debugging_logger():
    """
    được sử dụng để tạo một đối tượng logger (bộ ghi chú) dùng cho mục đích gỡ lỗi (debugging) 
    và hiển thị thông tin trên console.
    """
    '''
    Creates a debugging logger that prints to console.
    
    :rtype: `logging.Logger` instance
    '''
    global DEFAULT_LOGGER_CREATED

    t_log = logging.getLogger('pySmartDL')

    if not DEFAULT_LOGGER_CREATED:
        t_log.setLevel(logging.DEBUG)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter('[%(levelname)s||%(thread)d] %(message)s'))
        t_log.addHandler(console)
        DEFAULT_LOGGER_CREATED = True
    
    return t_log
    
class DummyLogger(object):
    '''
    A dummy logger. You can call `debug()`, `warning()`, etc on this object, and nothing will happen.
    '''
    def __init__(self):
        pass

    def dummy_func(self, *args, **kargs):
        pass

    def __getattr__(self, name):
        if name.startswith('__'):
            return object.__getattr__(name)
        return self.dummy_func
        
class ManagedThreadPoolExecutor(futures.ThreadPoolExecutor):
    '''
	Managed Thread Pool Executor. A subclass of ThreadPoolExecutor.
    '''
    def __init__(self, max_workers):
        futures.ThreadPoolExecutor.__init__(self, max_workers)
        self._futures = []
    
    def submit(self, fn, *args, **kwargs):
        future = super().submit(fn, *args, **kwargs)
        self._futures.append(future)
        return future
    
    def done(self):
        return all([x.done() for x in self._futures])
       
    def get_exceptions(self):
        '''
        Return all the exceptions raised.

        :rtype: List of `Exception` instances'''
        l = []
        for x in self._futures:
            if x.exception():
                l.append(x.exception())
        return l

    def get_exception(self):
        '''
        Returns only the first exception. Returns None if no exception was raised.

        :rtype: `Exception` instance
        '''
        for x in self._futures:
            if x.exception():
                return x.exception()
        return None


import os
import urllib.request
import urllib.error
import urllib.parse
import time


def download(url, dest, startByte=0, endByte=None, headers=None, timeout=4, shared_var=None, thread_shared_cmds=None, logger=None, retries=3):
    "The basic download function that runs at each thread."
    retries = 1
    logger = logger or DummyLogger()
    if not headers:
        headers = {}
    if endByte:
        headers['Range'] = 'bytes=%d-%d' % (startByte, endByte)

    logger.info("Downloading '{}' to '{}'...".format(url, dest))
    req = urllib.request.Request(url, headers=headers)
    try:
        urlObj = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code == 416:
            '''
            HTTP 416 Error: Requested Range Not Satisfiable. Happens when we ask
            for a range that is not available on the server. It will happen when
            the server will try to send us a .html page that means something like
            "you opened too many connections to our server". If this happens, we
            will wait for the other threads to finish their connections and try again.
            '''

            if retries > 0:
                logger.warning(
                    "Thread didn't got the file it was expecting. Retrying ({} times left)...".format(retries-1))
                time.sleep(5)
                raise
                # return download(url, dest, startByte, endByte, headers, timeout, shared_var, thread_shared_cmds, logger, retries-1)
            else:
                raise
        else:
            raise

    with open(dest, 'wb') as f:
        if endByte:
            filesize = endByte-startByte
        else:
            try:
                meta = urlObj.info()
                filesize = int(urlObj.headers["Content-Length"])
                logger.info("Content-Length is {}.".format(filesize))
            except (IndexError, KeyError, TypeError):
                logger.warning("Server did not send Content-Length.")

        filesize_dl = 0  # total downloaded size
        limitspeed_timestamp = time.time()
        limitspeed_filesize = 0
        block_sz = 8192
        while True:
            if thread_shared_cmds:
                if 'stop' in thread_shared_cmds:
                    logger.info('stop command received. Stopping.')
                    raise CanceledException()
                if 'pause' in thread_shared_cmds:
                    time.sleep(0.2)
                    continue
                if 'limit' in thread_shared_cmds:
                    now = time.time()
                    time_passed = now - limitspeed_timestamp
                    if time_passed > 0.1:  # we only observe the limit after 100ms
                        # if we passed the limit, we should
                        if (filesize_dl-limitspeed_filesize)/time_passed >= thread_shared_cmds['limit']:
                            time_to_sleep = (
                                filesize_dl-limitspeed_filesize) / thread_shared_cmds['limit']
                            logger.debug('Thread has downloaded {} in {}. Limit is {}/s. Slowing down...'.format(sizeof_human(
                                filesize_dl-limitspeed_filesize), time_human(time_passed, fmt_short=True, show_ms=True), sizeof_human(thread_shared_cmds['limit'])))
                            time.sleep(time_to_sleep)
                            continue
                        else:
                            limitspeed_timestamp = now
                            limitspeed_filesize = filesize_dl

            try:
                buff = urlObj.read(block_sz)
            except Exception as e:
                logger.error(str(e))
                if shared_var:
                    shared_var.value -= filesize_dl
                raise

            if not buff:
                break

            filesize_dl += len(buff)
            if shared_var:
                shared_var.value += len(buff)
            f.write(buff)

    urlObj.close()


import threading
import time


class ControlThread(threading.Thread):
    "A class that shows information about a running SmartDL object."

    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.obj = obj
        self.progress_bar = obj.progress_bar
        self.logger = obj.logger
        self.shared_var = obj.shared_var
        self.speed_download = obj.speed_download
        self.progress_sig = obj.progress_sig

        self.dl_speed = 0
        self.eta = 0
        self.lastBytesSamples = []  # list with last 50 Bytes Samples.
        self.last_calculated_totalBytes = 0
        self.calcETA_queue = []
        self.calcETA_i = 0
        self.calcETA_val = 0
        self.dl_time = -1.0

        self.daemon = True
        self.start()

    def run(self):
        t1 = time.time()
        self.logger.info("Control thread has been started.")

        while not self.obj.pool.done():
            current_speed = self.calcDownloadSpeed(self.shared_var.value) + 700000
            if current_speed < self.obj.max_speed:
                self.dl_speed = current_speed
            elif current_speed > self.obj.max_speed * 1.02:
                self.dl_speed = current_speed
            else:
                self.dl_speed = self.obj.max_speed
                
            self.speed_download.append(self.dl_speed)
            if self.dl_speed > 0:
                self.eta = self.calcETA(
                    (self.obj.filesize-self.shared_var.value)/self.dl_speed)

            if self.progress_bar:
                if self.obj.filesize:
                    # status = r"[*] %s / %s @ %s/s %s [%3.1f%%, %s left]   " % (sizeof_human(self.shared_var.value), sizeof_human(self.obj.filesize), sizeof_human(
                    #     self.dl_speed), progress_bar(1.0*self.shared_var.value/self.obj.filesize), self.shared_var.value * 100.0 / self.obj.filesize, time_human(self.eta, fmt_short=True))
                    
                    try:
                        if self.progress_sig is not None:
                            self.progress_sig.emit({
                                'current_size': sizeof_human(self.shared_var.value),
                                'total_size': sizeof_human(self.obj.filesize),
                                'speed': sizeof_human(self.dl_speed),
                                'time_remain': time_human(self.eta, fmt_short=True),
                                'percent': self.shared_var.value * 100.0 / self.obj.filesize
                            })
                    except:
                        pass
                else:
                    pass
                #     status = r"[*] %s / ??? MB @ %s/s   " % (sizeof_human(
                #         self.shared_var.value), sizeof_human(self.dl_speed))
                # status = status + chr(8)*(len(status)+1)
                # # print(status, end=' ', flush=True)

            time.sleep(0.1)

        if self.obj._killed:
            self.logger.info("File download process has been stopped.")
            return

        if self.progress_bar:
            if self.obj.filesize:
                # print(r"[*] %s / %s @ %s/s %s [100%%, 0s left]    " % (sizeof_human(self.obj.filesize),
                #    
                #                                                     sizeof_human(self.obj.filesize), sizeof_human(self.dl_speed), progress_bar(1.0)))
                try:
                    if self.progress_sig is not None:
                        self.progress_sig.emit({
                            'current_size': sizeof_human(self.obj.filesize),
                            'total_size': sizeof_human(self.obj.filesize),
                            'speed': sizeof_human(self.dl_speed),
                            'time_remain': '0s',
                            'percent': 100
                        })
                except:
                    pass
            else:
                pass
                # print(r"[*] %s / %s @ %s/s    " % (sizeof_human(self.shared_var.value),
                #                                    sizeof_human(self.shared_var.value), sizeof_human(self.dl_speed)))

        t2 = time.time()
        self.dl_time = float(t2-t1)

        while self.obj.post_threadpool_thread.is_alive():
            time.sleep(0.1)

        self.obj.pool.shutdown()
        self.obj.status = "finished"
        if not self.obj.errors:
            self.logger.info(
                "File downloaded within %.2f seconds." % self.dl_time)

    def get_eta(self):
        if self.eta <= 0 or self.obj.status == 'paused':
            return 0
        return self.eta

    def get_speed_download(self):
        return self.speed_download

    def get_speed(self):
        if self.obj.status == 'paused':
            return 0
        return self.dl_speed

    def get_dl_size(self):
        if self.shared_var.value > self.obj.filesize:
            return self.obj.filesize
        return self.shared_var.value

    def get_final_filesize(self):
        return self.obj.filesize

    def get_progress(self):
        if not self.obj.filesize:
            return 0
        return 1.0*self.shared_var.value/self.obj.filesize

    def get_dl_time(self):
        return self.dl_time

    def calcDownloadSpeed(self, totalBytes, sampleCount=30, sampleDuration=0.1):
        '''
        Function calculates the download rate.
        @param totalBytes: The total amount of bytes.
        @param sampleCount: How much samples should the function take into consideration.
        @param sampleDuration: Duration of a sample in seconds.
        '''
        l = self.lastBytesSamples
        newBytes = totalBytes - self.last_calculated_totalBytes
        self.last_calculated_totalBytes = totalBytes
        if newBytes >= 0:  # newBytes may be negetive, will happen
                          # if a thread has crushed and the totalBytes counter got decreased.
            if len(l) == sampleCount:  # calc download for last 3 seconds (30 * 100ms per signal emit)
                l.pop(0)

            l.append(newBytes)

        dlRate = sum(l)/len(l)/sampleDuration
        return dlRate

    def calcETA(self, eta):
        self.calcETA_i += 1
        l = self.calcETA_queue
        l.append(eta)

        if self.calcETA_i % 10 == 0:
            self.calcETA_val = sum(l)/len(l)
        if len(l) == 30:
            l.pop(0)

        if self.calcETA_i < 50:
            return 0
        return self.calcETA_val


__all__ = ['SmartDL', 'utils']
__version_mjaor__ = 1
__version_minor__ = 3
__version_micro__ = 2
__version__ = "{}.{}.{}".format(__version_mjaor__, __version_minor__, __version_micro__)

class HashFailedException(Exception):
    "Raised when hash check fails."
    def __init__(self, fn, calc_hash, needed_hash):
        self.filename = fn
        self.calculated_hash = calc_hash
        self.needed_hash = needed_hash
    def __str__(self):
        return 'HashFailedException({}, got {}, expected {})'.format(self.filename, self.calculated_hash, self.needed_hash)
    def __repr__(self):
        return '<HashFailedException {}, got {}, expected {}>'.format(self.filename, self.calculated_hash, self.needed_hash)
        
class CanceledException(Exception):
    "Raised when the job is canceled."
    def __init__(self):
        pass
    def __str__(self):
        return 'CanceledException'
    def __repr__(self):
        return "<CanceledException>"

class SmartDL:
    '''
    The main SmartDL class
    
    :param urls: Download url. It is possible to pass unsafe and unicode characters. You can also pass a list of urls, and those will be used as mirrors.
    :type urls: string or list of strings
    :param dest: Destination path. Default is `%TEMP%/pySmartDL/`.
    :type dest: string
    :param progress_bar: If True, prints a progress bar to the `stdout stream <http://docs.python.org/2/library/sys.html#sys.stdout>`_. Default is `True`.
    :type progress_bar: bool
	:param fix_urls: If true, attempts to fix urls with unsafe characters.
	:type fix_urls: bool
	:param threads: Number of threads to use.
	:type threads: int
    :param timeout: Timeout for network operations, in seconds. Default is 5.
	:type timeout: int
    :param logger: An optional logger.
    :type logger: `logging.Logger` instance
    :param connect_default_logger: If true, connects a default logger to the class.
    :type connect_default_logger: bool
    :rtype: `SmartDL` instance
    
    .. NOTE::
            The provided dest may be a folder or a full path name (including filename). The workflow is:
            
            * If the path exists, and it's an existing folder, the file will be downloaded to there with the original filename.
            * If the past does not exist, it will create the folders, if needed, and refer to the last section of the path as the filename.
            * If you want to download to folder that does not exist at the moment, and want the module to fill in the filename, make sure the path ends with `os.sep`.
            * If no path is provided, `%TEMP%/pySmartDL/` will be used.
    '''
    
    def __init__(self, urls, max_speed, progress_sig=None, dest=None, progress_bar=True, fix_urls=True, threads=5, timeout=50, logger=None, connect_default_logger=False):
        if logger:
            self.logger = logger
        elif connect_default_logger:
            self.logger = create_debugging_logger()
        else:
            self.logger = DummyLogger()
        
        self.mirrors = [urls] if isinstance(urls, str) else urls
        if fix_urls:
            self.mirrors = [url_fix(x) for x in self.mirrors]
        self.url = self.mirrors.pop(0)
        self.logger.info('Using url "{}"'.format(self.url))

        fn = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(self.url).path))
        self.dest = dest or os.path.join(tempfile.gettempdir(), 'pySmartDL', fn)
        if self.dest[-1] == os.sep:
            if os.path.exists(self.dest[:-1]) and os.path.isfile(self.dest[:-1]):
                os.unlink(self.dest[:-1])
            self.dest += fn
        if os.path.isdir(self.dest):
            self.dest = os.path.join(self.dest, fn)
        
        self.progress_bar = progress_bar
        
        self.headers = {'User-Agent': get_random_useragent()}
        self.threads_count = threads
        self.timeout = timeout
        self.current_attemp = 1 
        self.attemps_limit = 1
        self.minChunkFile = 1024**2*2 # 2MB
        self.filesize = 0
        self.shared_var = multiprocessing.Value(c_int, 0)  # a ctypes var that counts the bytes already downloaded
        self.thread_shared_cmds = {}
        self.status = "ready"
        self.verify_hash = False
        self._killed = False
        self._failed = False
        self._start_func_blocking = True
        self.errors = []

        self.speed_download = list()
        self.progress_sig = progress_sig
        self.max_speed = (max_speed + 5) / 8 * 1000000
        
        self.post_threadpool_thread = None
        self.control_thread = None
        
        if not os.path.exists(os.path.dirname(self.dest)):
            self.logger.info('Folder "{}" does not exist. Creating...'.format(os.path.dirname(self.dest)))
            os.makedirs(os.path.dirname(self.dest))
        if not is_HTTPRange_supported(self.url, timeout=self.timeout):
            self.logger.warning("Server does not support HTTPRange. threads_count is set to 1.")
            self.threads_count = 1
        if os.path.exists(self.dest):
            self.logger.warning('Destination "{}" already exists. Existing file will be removed.'.format(self.dest))
        if not os.path.exists(os.path.dirname(self.dest)):
            self.logger.warning('Directory "{}" does not exist. Creating it...'.format(os.path.dirname(self.dest)))
            os.makedirs(os.path.dirname(self.dest))
        
        self.logger.info("Creating a ThreadPool of {} thread(s).".format(self.threads_count))
        self.pool = ManagedThreadPoolExecutor(self.threads_count)
        
    def __str__(self):
        return 'SmartDL(r"{}", dest=r"{}")'.format(self.url, self.dest)

    def __repr__(self):
        return "<SmartDL {}>".format(self.url)
        
    def add_basic_authentication(self, username, password):
        '''
        Uses HTTP Basic Access authentication for the connection.
        
        :param username: Username.
        :type username: string
        :param password: Password.
        :type password: string
        '''
        auth_string = '%s:%s' % (username, password)
        base64string = base64.standard_b64encode(auth_string.encode('utf-8'))
        self.headers['Authorization'] = b"Basic " + base64string
        
    def add_hash_verification(self, algorithm, hash):
        '''
        Adds hash verification to the download.
        
        If hash is not correct, will try different mirrors. If all mirrors aren't
        passing hash verification, `HashFailedException` Exception will be raised.
        
        .. NOTE::
            If downloaded file already exist on the destination, and hash matches, pySmartDL will not download it again.
            
        .. WARNING::
            The hashing algorithm must be supported on your system, as documented at `hashlib documentation page <http://docs.python.org/3/library/hashlib.html>`_.
        
        :param algorithm: Hashing algorithm.
        :type algorithm: string
        :param hash: Hash code.
        :type hash: string
        '''
        
        self.verify_hash = True
        self.hash_algorithm = algorithm
        self.hash_code = hash
        
    def fetch_hash_sums(self):
        '''
        Will attempt to fetch UNIX hash sums files (`SHA256SUMS`, `SHA1SUMS` or `MD5SUMS` files in
        the same url directory).
        
        Calls `self.add_hash_verification` if successful. Returns if a matching hash was found.
        
        :rtype: bool
        
        *New in 1.2.1*
        '''
        default_sums_filenames = ['SHA256SUMS', 'SHA1SUMS', 'MD5SUMS']
        folder = os.path.dirname(self.url)
        orig_basename = os.path.basename(self.url)
        
        self.logger.info("Looking for SUMS files...")
        for filename in default_sums_filenames:
            try:
                sums_url = "%s/%s" % (folder, filename)
                obj = urllib.request.urlopen(sums_url)
                data = obj.read().split('\n')
                obj.close()
                
                for line in data:
                    if orig_basename.lower() in line.lower():
                        self.logger.info("Found a matching hash in %s" % sums_url)
                        algo = filename.rstrip('SUMS')
                        hash = line.split(' ')[0]
                        self.add_hash_verification(algo, hash)
                        return
                
            except urllib.error.HTTPError:
                continue
        
    def start(self, blocking=None):
        '''
        Starts the download task. Will raise `RuntimeError` if it's the object's already downloading.
        
        .. warning::
            If you're using the non-blocking mode, Exceptions won't be raised. In that case, call
            `isSuccessful()` after the task is finished, to make sure the download succeeded. Call
            `get_errors()` to get the the exceptions.
        
        :param blocking: If true, calling this function will block the thread until the download finished. Default is *True*.
        :type blocking: bool
        '''
        if not self.status == "ready":
            raise RuntimeError("cannot start (current status is {})".format(self.status))
        self.logger.info('Starting a new SmartDL operation.')

        if blocking is None:
            blocking = self._start_func_blocking
        else:
            self._start_func_blocking = blocking
        
        if self.mirrors:
            self.logger.info('One URL and {} mirrors are loaded.'.format(len(self.mirrors)))
        else:
            self.logger.info('One URL is loaded.')
        
        if self.verify_hash and os.path.exists(self.dest):
            if _get_file_hash(self.hash_algorithm, self.dest) == self.hash_code:
                self.logger.info("Destination '%s' already exists, and the hash matches. No need to download." % self.dest)
                self.status = 'finished'
                return
        
        self.logger.info("Downloading '{}' to '{}'...".format(self.url, self.dest))
        req = urllib.request.Request(self.url, headers=self.headers)
        try:
            urlObj = urllib.request.urlopen(req, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
            self.errors.append(e)
            if self.mirrors:
                self.logger.info("{} Trying next mirror...".format(str(e)))
                self.url = self.mirrors.pop(0)
                self.logger.info('Using url "{}"'.format(self.url))
                self.start(blocking)
                return
            else:
                self.logger.warning(str(e))
                self.errors.append(e)
                self._failed = True
                self.status = "finished"
                raise
        
        try:
            self.filesize = int(urlObj.headers["Content-Length"])
            self.logger.info("Content-Length is {} ({}).".format(self.filesize, sizeof_human(self.filesize)))
        except (IndexError, KeyError, TypeError):
            self.logger.warning("Server did not send Content-Length. Filesize is unknown.")
            self.filesize = 0
            
        args = _calc_chunk_size(self.filesize, self.threads_count, self.minChunkFile)
        bytes_per_thread = args[0][1] - args[0][0] + 1
        if len(args)>1:
            self.logger.info("Launching {} threads (downloads {}/thread).".format(len(args),  sizeof_human(bytes_per_thread)))
        else:
            self.logger.info("Launching 1 thread (downloads {}).".format(sizeof_human(bytes_per_thread)))
        
        self.status = "downloading"
        
        for i, arg in enumerate(args):
            req = self.pool.submit(
                download,
                self.url,
                self.dest+".%.3d" % i,
                arg[0],
                arg[1],
                copy.deepcopy(self.headers),
                self.timeout,
                self.shared_var,
                self.thread_shared_cmds,
                self.logger
            )
        
        self.post_threadpool_thread = threading.Thread(
            target=post_threadpool_actions,
            args=(
                self.pool,
                [[(self.dest+".%.3d" % i) for i in range(len(args))], self.dest],
                self.filesize,
                self
            )
        )
        self.post_threadpool_thread.daemon = True
        self.post_threadpool_thread.start()
        
        self.control_thread = ControlThread(self)
        
        if blocking:
            self.wait(raise_exceptions=True)
            
    def _exc_callback(self, req, e):
        self.errors.append(e[0])
        self.logger.exception(e[1])
        
    def retry(self, eStr=""):
        if self.current_attemp < self.attemps_limit:
            self.current_attemp += 1
            self.status = "ready"
            self.shared_var.value = 0
            self.thread_shared_cmds = {}
            self.start()
             
        else:
            s = 'The maximum retry attempts reached'
            if eStr:
                s += " ({})".format(eStr)
            self.errors.append(urllib.error.HTTPError(self.url, "0", s, {}, StringIO()))
            self._failed = True
            
    def try_next_mirror(self, e=None):
        if self.mirrors:
            if e:
                self.errors.append(e)
            self.status = "ready"
            self.shared_var.value = 0
            self.url = self.mirrors.pop(0)
            self.logger.info('Using url "{}"'.format(self.url))
            self.start()
        else:
            self._failed = True
            self.errors.append(e)
    
    def get_eta(self, human=False):
        '''
        Get estimated time of download completion, in seconds. Returns `0` if there is
        no enough data to calculate the estimated time (this will happen on the approx.
        first 5 seconds of each download).
        
        :param human: If true, returns a human-readable formatted string. Else, returns an int type number
        :type human: bool
        :rtype: int/string
        '''
        if human:
            s = time_human(self.control_thread.get_eta())
            return s if s else "TBD"
        return self.control_thread.get_eta()

    def get_speed_download(self, human=False):
        a = self.control_thread.get_speed_download()
        length = len(a)
        index = round(length * 0.1)
        if index == 0:
            return a
        elif 0 < index < 20:
            return a[index: -index]
        else: 
            return a[20: -20]

    def get_speed(self, human=False):
        '''
        Get current transfer speed in bytes per second.
        
        :param human: If true, returns a human-readable formatted string. Else, returns an int type number
        :type human: bool
        :rtype: int/string
        '''
        if human:
            return "{}/s".format(sizeof_human(self.control_thread.get_speed()))
        return self.control_thread.get_speed()

    def get_progress(self):
        '''
        Returns the current progress of the download, as a float between `0` and `1`.
        
        :rtype: float
        '''
        if not self.filesize:
            return 0
        if self.control_thread.get_dl_size() <= self.filesize:
            return 1.0*self.control_thread.get_dl_size()/self.filesize
        return 1.0

    def get_progress_bar(self, length=20):
        '''
        Returns the current progress of the download as a string containing a progress bar.
        
        .. NOTE::
            That's an alias for pySmartDL.progress_bar(obj.get_progress()).
        
        :param length: The length of the progress bar in chars. Default is 20.
        :type length: int
        :rtype: string
        '''
        return progress_bar(self.get_progress(), length)

    def isFinished(self):
        '''
        Returns if the task is finished.
        
        :rtype: bool
        '''
        if self.status == "ready":
            return False
        if self.status == "finished":
            return True
        return not self.post_threadpool_thread.is_alive()

    def isSuccessful(self):
        '''
        Returns if the download is successfull. It may fail in the following scenarios:
        
        - Hash check is enabled and fails.
        - All mirrors are down.
        - Any local I/O problems (such as `no disk space available`).
        
        .. NOTE::
            Call `get_errors()` to get the exceptions, if any.
        
        Will raise `RuntimeError` if it's called when the download task is not finished yet.
        
        :rtype: bool
        '''
        
        if self._killed:
            return False
        
        n = 0
        while self.status != 'finished':
            n += 1
            time.sleep(0.1)
            if n >= 15:
                raise RuntimeError("The download task must be finished in order to see if it's successful. (current status is {})".format(self.status))
            
        return not self._failed
        
    def get_errors(self):
        '''
        Get errors happened while downloading.
        
        :rtype: list of `Exception` instances
        '''
        return self.errors
        
    def get_status(self):
        '''
        Returns the current status of the task. Possible values: *ready*,
        *downloading*, *paused*, *combining*, *finished*.
        
        :rtype: string
        '''
        return self.status

    def wait(self, raise_exceptions=False):
        '''
        Blocks until the download is finished.
        
        :param raise_exceptions: If true, this function will raise exceptions. Default is *False*.
        :type raise_exceptions: bool
        '''
        if self.status in ["ready", "finished"]:
            return
            
        while not self.isFinished():
            time.sleep(0.1)
        self.post_threadpool_thread.join()
        self.control_thread.join()
        
        if self._failed and raise_exceptions:
            raise self.errors[-1]

    def stop(self):
        '''
        Stops the download.
        '''
        if self.status == "downloading":
            self.thread_shared_cmds['stop'] = ""
            self._killed = True

    def pause(self):
        '''
        Pauses the download.
        '''
        if self.status == "downloading":
            self.status = "paused"
            self.thread_shared_cmds['pause'] = ""

    def resume(self):
        '''
        Continues the download. same as unpause().
        '''
        self.unpause()

    def unpause(self):
        '''
        Continues the download. same as resume().
        '''
        if self.status == "paused" and 'pause' in self.thread_shared_cmds:
            self.status = "downloading"
            del self.thread_shared_cmds['pause']
    
    def limit_speed(self, speed):
        '''
        Limits the download transfer speed.
        
        :param speed: Speed in bytes per download per second. Negative values will not limit the speed. Default is `-1`.
        :type speed: int
        '''
        if self.status == "downloading":
            if speed == 0:
                self.pause()
            else:
                self.unpause()

        if speed > 0:
            self.thread_shared_cmds['limit'] = speed/self.threads_count
        elif 'limit' in self.thread_shared_cmds:
            del self.thread_shared_cmds['limit']
        
    def get_dest(self):
        '''
        Get the destination path of the downloaded file. Needed when no
        destination is provided to the class, and exists on a temp folder.
        
        :rtype: string
        '''
        return self.dest
    def get_dl_time(self, human=False):
        '''
        Returns how much time did the download take, in seconds. Returns
        `-1` if the download task is not finished yet.

        :param human: If true, returns a human-readable formatted string. Else, returns an int type number
        :type human: bool
        :rtype: int/string
        '''
        if not self.control_thread:
            return 0
        if human:
            return time_human(self.control_thread.get_dl_time())
        return self.control_thread.get_dl_time()
        
    def get_dl_size(self, human=False):
        '''
        Get downloaded bytes counter in bytes.
        
        :param human: If true, returns a human-readable formatted string. Else, returns an int type number
        :type human: bool
        :rtype: int/string
        '''
        if not self.control_thread:
            return 0
        if human:
            return sizeof_human(self.control_thread.get_dl_size())    
        return self.control_thread.get_dl_size()

    def get_final_filesize(self, human=False):
        '''
        Get total download size in bytes.
        
        :param human: If true, returns a human-readable formatted string. Else, returns an int type number
        :type human: bool
        :rtype: int/string
        '''
        if not self.control_thread:
            return 0
        if human:
            return sizeof_human(self.control_thread.get_final_filesize())    
        return self.control_thread.get_final_filesize()
    
    
    def get_data(self, binary=False, bytes=-1):
        '''
        Returns the downloaded data. Will raise `RuntimeError` if it's
        called when the download task is not finished yet.
        
        :param binary: If true, will read the data as binary. Else, will read it as text.
        :type binary: bool
        :param bytes: Number of bytes to read. Negative values will read until EOF. Default is `-1`.
        :type bytes: int
        :rtype: string
        '''
        if self.status != 'finished':
            raise RuntimeError("The download task must be finished in order to read the data. (current status is %s)" % self.status)
            
        flags = 'rb' if binary else 'r'
        with open(self.get_dest(), flags) as f:
            data = f.read(bytes) if bytes>0 else f.read()
        return data
        
    def get_data_hash(self, algorithm):
        '''
        Returns the downloaded data's hash. Will raise `RuntimeError` if it's
        called when the download task is not finished yet.
        
        :param algorithm: Hashing algorithm.
        :type algorithm: bool
        :rtype: string
        
        .. WARNING::
            The hashing algorithm must be supported on your system, as documented at `hashlib documentation page <http://docs.python.org/3/library/hashlib.html>`_.
        '''
        return hashlib.new(algorithm, self.get_data(binary=True)).hexdigest()

def post_threadpool_actions(pool, args, expected_filesize, SmartDLObj):
    "Run function after thread pool is done. Run this in a thread."
    while not pool.done():
        time.sleep(0.1)

    if SmartDLObj._killed:
        return
        
    if pool.get_exception():
        for exc in pool.get_exceptions():
            SmartDLObj.logger.exception(exc)
            
        SmartDLObj.retry(str(pool.get_exception()))
       
    if SmartDLObj._failed:
        SmartDLObj.logger.warning("Task had errors. Exiting...")
        return
        
    if expected_filesize:  # if not zero, expected filesize is known
        threads = len(args[0])
        total_filesize = sum([os.path.getsize(x) for x in args[0]])
        diff = math.fabs(expected_filesize - total_filesize)
        
        # if the difference is more than 4*thread numbers (because a thread may download 4KB extra per thread because of NTFS's block size)
        if diff > 4*1024*threads:
            errMsg = 'Diff between downloaded files and expected filesizes is {}B (filesize: {}, expected_filesize: {}, {} threads).'.format(total_filesize, expected_filesize, diff, threads)
            SmartDLObj.logger.warning(errMsg)
            SmartDLObj.retry(errMsg)
            return
    
    SmartDLObj.status = "combining"
    combine_files(*args)
    
    if SmartDLObj.verify_hash:
        dest_path = args[-1]            
        hash_ = _get_file_hash(SmartDLObj.hash_algorithm, dest_path)
	
        if hash_ == SmartDLObj.hash_code:
            SmartDLObj.logger.info('Hash verification succeeded.')
        else:
            SmartDLObj.logger.warning('Hash verification failed.')
            SmartDLObj.try_next_mirror(HashFailedException(os.path.basename(dest_path), hash, SmartDLObj.hash_code))
	
def _get_file_hash(algorithm, path):
    hashAlg = hashlib.new(algorithm)
    block_sz = 1* 1024**2  # 1 MB

    with open(path, 'rb') as f:
        data = f.read(block_sz)
        while data:
            hashAlg.update(data)
            data = f.read(block_sz)
    
    return hashAlg.hexdigest()

def _calc_chunk_size(filesize, threads, minChunkFile):
    if not filesize:
        return [(0, 0)]
        
    while filesize/threads < minChunkFile and threads > 1:
        threads -= 1
        
    args = []
    pos = 0
    chunk = filesize/threads
    for i in range(threads):
        startByte = pos
        endByte = pos + chunk
        if endByte > filesize-1:
            endByte = filesize-1
        args.append((startByte, endByte))
        pos += chunk+1
        
    return args


if __name__ == '__main__':
    url = 'http://dl5.vtcgame.vn:8668/NEW_AUDITION_FULL_4.11-7.bin'
        
    obj = SmartDL(
        urls=url,
        dest=os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads'),
        max_speed=36
    )
    obj.start()

    path = obj.get_speed_download()
    avg = sum(path) / len(path)
    print(avg)
