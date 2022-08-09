"""工具包"""

import hashlib
import re


def verify_name_rule(value):
    """验证名称规则：2-36位字符，支持-_两种特殊字符,且不能是开头或结尾"""
    if value is None:
        return False
    elif not (2 <= len(value.encode('gbk', 'ignore')) <= 36):
        return False
    elif value.startswith('_') or value.startswith('-') or value.endswith('-') or value.endswith(
            '_') or len(''.join(re.findall('[\u4e00-\u9fa5a-zA-Z0-9_-]+', value))) != len(value):
        return False
    return True


def transfer_str(str):
    """
    转义字符
    :param str: 定义转义字符
    :return: 转义之后的字符
    """
    new_str = ""
    special = ['/', '^', '$', '*', '+', '?', '.', '(', ')', '#', '[', ']', '&', '+', ';']
    for c in str:
        if c in special:
            new_str += '\\'
        new_str += c
    return new_str


class Dict2Attr(object):
    """字典转换属性"""

    def __init__(self, initial_data):
        """初始属性"""
        for key in initial_data:
            setattr(self, key, initial_data[key])


def get_file_md5(file_name):
    """获取文件的md5"""
    with open(file_name, 'rb') as fp:
        data = fp.read()
    file_md5 = hashlib.md5(data).hexdigest()
    return file_md5
