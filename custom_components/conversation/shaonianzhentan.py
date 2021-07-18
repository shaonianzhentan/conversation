import hashlib

# MD5加密
def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()