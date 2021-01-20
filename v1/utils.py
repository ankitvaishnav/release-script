import datetime as dt
import errno
import json
import hashlib
import os
import shutil
import pprint
import logging
import subprocess
import time
import traceback
from types import SimpleNamespace
from typing import List


def myprint(msg, head=None):
    if head == 1:
        logging.info('\n\n===================================================================')
        logging.info(Colors.HEADER + Colors.BOLD + (pprint.pformat(msg) if not isStr(msg) else msg) + Colors.ENDC)
        logging.info('-------------------------------------------------------------------')
    elif head == 2:
        logging.info('\n--------------------------')
        logging.info(Colors.OKBLUE + (pprint.pformat(msg) if not isStr(msg) else msg) + Colors.ENDC)
        logging.info('-------------')
    elif head == 3:
        logging.info(pprint.pformat(msg) if not isStr(msg) else msg)
    elif head == 11:
        logging.info(Colors.WARNING + (pprint.pformat(msg) if not isStr(msg) else msg) + Colors.ENDC)
    elif head == 12:
        logging.info(Colors.OKGREEN + (pprint.pformat(msg) if not isStr(msg) else msg) + Colors.ENDC)
    elif head == 13:
        logging.info(Colors.FAIL + (pprint.pformat(msg) if not isStr(msg) else msg) + Colors.ENDC)
    else:
        logging.info(pprint.pformat(msg) if not isStr(msg) else msg)


def getTimestamp(seconds_offset=None):
    '''
    Current TS.
    Format: 2019-02-14T12:40:59.768Z  (UTC)
    '''
    delta = dt.timedelta(days=0)
    if seconds_offset is not None:
        delta = dt.timedelta(seconds=seconds_offset)

    ts = dt.datetime.utcnow() + delta
    ms = ts.strftime('%f')[0:3]
    s = ts.strftime('%Y-%m-%dT%H:%M:%S') + '.%sZ' % ms
    return s


def sha256Hash(data):
    '''
    data assumed as type bytes
    '''
    m = hashlib.sha256()
    m.update(data)
    h = m.hexdigest().upper()
    return h


def response_to_dict(r):
    try:
        myprint('Response: <%d>' % r.status_code)
        r = r.content.decode()  # to str
        r = json.loads(r)
    except:
        r = traceback.format_exc()

    return r


def print_response(r, h=None):
    print('Status code =  %s' % r.status_code)
    if h is not None:
        print('Headers =  %s' % r.headers)
    print('Links =  %s' % r.links)
    print('Encoding = %s' % r.encoding)
    print('Response Data = %s' % r.content)
    print('Size = %s' % len(r.content))


def zip_packet(regid, base_path, out_dir):
    '''
    Args:
        regid: Registration id - this will be the name of the packet
        base_path:  Zip will cd into this dir and archive from here
        out_dir: Dir in which zip file will be written
    Returns:
        path of zipped packet
    '''
    out_path = os.path.join(out_dir, regid)
    shutil.make_archive(out_path, 'zip', base_path)
    return out_path + '.zip'


def init_logger(log_file):
    logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)
    root_logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)


def get_json_file(path):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return json.loads(file.read(), object_hook=lambda d: SimpleNamespace(**d))
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)


def get_json_file_cls(path, c):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return json.loads(file.read(), object_hook=lambda d: c(**d))
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)


def write_json_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def dict_to_json(data):
    return json.dumps(data)


def get_file_extension(file):
    filename, extension = os.path.splitext(file)
    return extension


def keyExists(key, d):
    if key in d.keys():
        return True
    else:
        return False


def isStr(s):
    return isinstance(s, str)


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def Pprint(s):
    return s if isinstance(s, str) else pprint.pformat(s)


def Wait(t):
    myprint("Waiting for "+Pprint(t)+" seconds")
    time.sleep(t)


def Command(command: List):
    myprint("Command: " + ' '.join(command))
    ds = subprocess.Popen(command, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    myprint(ds.stderr, 13)
    while True:
        output = ds.stdout.readline()
        if output == b'' and ds.poll() is not None:
            break
        if output:
            myprint("Console: " + output.strip().decode("utf-8"))


def CommandOutput(command: str):
    myprint("Command: "+command)
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout
    return res.decode("utf-8") if isinstance(res, bytes) else res


def getRepoNameFromUrl(repo: str):
    return os.path.splitext(os.path.basename(repo))[0]