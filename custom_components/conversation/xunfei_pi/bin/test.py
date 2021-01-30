# -*- coding: utf-8 -*-  
import os, re

rs = os.popen("./iat_sample")
text = rs.read()
arr = text.split('=============================================================')
print(arr[1].strip('\n'))