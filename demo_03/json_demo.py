#!/usr/bin/env python
import json

chinese_str = "中国"
print(chinese_str)

print(json.dumps(chinese_str))

print(json.dumps(chinese_str, ensure_ascii=False))
