#!/usr/bin/env python

content = "中国"
print(type(content), content)

bin_content = content.encode("utf-8")
print(type(bin_content), bin_content)

decode_bin_content = bin_content.decode("utf-8")
print(type(decode_bin_content), bin_content.decode("utf-8"))
