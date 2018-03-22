#encoding=utf-8

from __future__ import print_function
try:
    import queue
except ImportError:
    import Queue as queue

from multiprocessing import Queue
import threading
import time
import multiprocessing
import logging

import argparse
import os
from itertools import count

from log_utils import setup_logger
from request_utils import get_result
from utils import read_url_from_file,find_last

# Use queue to control the process
def generator_url_queue(urls_generator, max_q_size=2, wait_time=0.05):
    q = Queue(max_q_size)
    _stop = threading.Event() 

    def url_generator_task():
        while not _stop.is_set():
            try:
                generator_output = urls_generator.next()
                if generator_output == None:
                    break
                q.put(generator_output)
            except Exception:
                _stop.set()
                raise

    generator_thread = threading.Thread(target=url_generator_task)
    generator_thread.daemon = True
    generator_thread.start()

    return q, _stop

class URL_Generator:
    def __init__(self, urls):
        self.urls = urls
        self.pointer = 0
    def next(self):
        if self.pointer<len(self.urls):
            url = self.urls[self.pointer]
            self.pointer += 1
            return url
        return None
    def __len__(self):
        return len(self.urls)


def crawler(args):
    urls = read_url_from_file(args.filepath, args.bad_urls_save_dir)
    logger.info('In total, {} legible urls'.format(len(urls)))
    urls_generator = URL_Generator(urls)

    num_process = len(urls) if args.num_process>len(urls) else args.num_process

    q, _ = generator_url_queue(urls_generator)



    def crawl(process_idx, q):
        save_filepath = args.save_path
        process_idx = str(process_idx)
        if save_filepath is None:
            index = find_last(args.filepath, '/')
            if index!=-1:
                if not os.path.exists(args.filepath[:index] + '/results'):
                    os.mkdir(args.filepath[:index] + '/results')
                    logging.info('Create results folder')
                save_file = args.filepath[:index] + '/results/{}.txt'.format(process_idx)
            else:
                if not os.path.exists('results'):
                    logging.info('Create results folder')
                    os.mkdir('results')
                save_file = 'results/{}.txt'.format(process_idx)
        else:
            logging.info('Using folder {} for results'.format(save_filepath))
            save_file = save_filepath + '/{}.txt'.format(process_idx)
        with open(save_file, 'w') as f:
            unknown_exception_counts = 0
            f.write('{\n')
            res_count = 0
            for i in count():
                try:
                    url = q.get(block=True, timeout=0.5)
                    res = get_result(url, greedy=args.greedy)
                    if res!=None:
                        key = process_idx + '_' + str(res_count)
                        f.write(key + ':' + str(res) + ',\n')
                        res_count += 1
                except queue.Empty:
                    f.write('}')
                    break
                except:
                    unknown_exception_counts += 1
                    if unknown_exception_counts>3:
                        f.write('}')
                        break
                    logger.info('Unknown exception catches')
        return

    logger.info('Ready for crawling...')
    ps = []
    for i in range(num_process):
        p = multiprocessing.Process(target=crawl, args=(i, q))
        p.start()
        ps.append(p)
    for p in ps:
        try:
            p.join()
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt, stop all tasks.')
            for p in ps:
                p.terminate()
            break

    logger.info('Finish crawling...')

parser = argparse.ArgumentParser()
parser.add_argument('filepath', help='File path to file contains urls, separated by line.') 
parser.add_argument('-b', '--bad-urls-save-dir', help='File path to save unrecoginizable urls.', default=None) 
parser.add_argument('-g', '--greedy', help='Whether to use greedy stratagies.', type=bool, default=False)	
parser.add_argument('-t', '--timeout', help='Timeout time.', default=3, type=int) 
parser.add_argument('-r', '--rety-time', help='Retry time when connection failed.', default=3, type=int) 
parser.add_argument('-n','--num-process', help='Number of crawling process.', default=1, type=int) 
parser.add_argument('-sf', '--save-path', help='Where to save results', default=None)	


if __name__ == '__main__':
    args = parser.parse_args()
    #logger = logging.getLogger()
    #logger.setLevel(logging.INFO)
    logger = setup_logger()
    crawler(args)

