# coding:utf-8

"""
author: songzhongsen@weibangong.com
"""

import os


def rm_ia_all_pyc(_path):
    for root,_,files in os.walk(_path):
        for _file in files:
            if _file.endswith('pyc'):
                os.remove(os.path.join(root, _file))


if __name__ == "__main__":
    import sys
    dir_name = sys.argv[1]
    rm_ia_all_pyc(dir_name)
