import random

colorObj = {
    '红': 'red',
    '橙': 'orange',
    '黄': 'yellow',
    '绿': 'green',
    '青': 'teal',
    '蓝': 'blue',
    '紫': 'purple',
    '粉': 'pink',
    '白': 'white',
    '紫红': 'fuchsia',
    '橄榄': 'olive'
}

proxy = random.choice(list(colorObj))
print(proxy)