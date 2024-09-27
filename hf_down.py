import os
import requests
from lxml import etree
import time
import re
import urllib.request
from tqdm import tqdm


# 开始
def start_run(url, head, root_dir_name):
    # 状态码
    respone = requests.get(url, headers=head)
    print(respone)
    # 状态码是否正常
    if respone.status_code >= 200 or respone.status_code < 300:
        html = etree.HTML(respone.text)
        model_dir_list = html.xpath('/html/body/div[1]/main/div[2]/section/div[3]/ul/li')

        for model_dir in model_dir_list:
            test = len(model_dir.xpath('div[1]/@class')[0])
            # 文件
            if test > 24:
                model_down_url = model_dir.xpath('a[1]/@href')[0]
                model_url = 'https://huggingface.co' + model_down_url
                model_name = model_down_url.split('/')[-1].split('?')[0]
                down_url(model_url, model_name, dir_name=root_dir_name)
            # 文件夹
            else:
                dir_name = model_dir.xpath('a[1]/span/text()')[0]
                dir_name = root_dir_name + '/' + dir_name
                # 判断文件夹是否存在
                if not os.path.exists(dir_name):
                    # 如果不存在，创建文件夹
                    os.makedirs(dir_name)
                    print(f"子目录文件夹 {dir_name} 创建成功")
                else:
                    print(f"子目录文件夹 {dir_name} 已经存在")

                model_url = model_dir.xpath('a[1]/@href')[0]
                next_url = 'https://huggingface.co' + model_url
                next_rep(next_url, dir_name)


# 翻到下一页
def next_rep(next_url, dir_name):
    next_respone = requests.get(url=next_url, headers=head)

    html = etree.HTML(next_respone.text)

    model_down_url_list = html.xpath('/html/body/div[1]/main/div[2]/section/div[3]/ul/li')
    for value in model_down_url_list:
        model_down_url = value.xpath(f'a[1]/@href')[0]

        model_url = 'https://huggingface.co' + model_down_url
        model_name = model_down_url.split('/')[-1].split('?')[0]
        down_url(model_url, model_name, dir_name)


# 下载
def down_url(model_url, model_name, dir_name=''):
    response = urllib.request.urlopen(model_url)
    chunk_size = 1024 * 1024
    total_size = int(response.getheader('Content-Length').strip())

    if dir_name != '':
        model_name = dir_name + '/' + model_name

    if os.path.exists(model_name):
        print("已跳过！！！，文件存在")
    else:

        # 不同的下载样式
        # 1,基本样式
        # tqdm(total=100, desc="下载进度", unit='B', unit_scale=True)
        # 下载进度: 60%|███████████████           | 60MB/100MB [00:30<00:20, 2MB/s]
        #
        # 2,改变进度块的样式
        # tqdm(total=100, ascii=True)
        # 40%|####                            | 40/100 [00:20<00:30]

        # 3，自定义 bar_format
        # tqdm(total=100, bar_format="{l_bar} {bar} | {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
        # 下载中... |███████████████████         | 70/100 [00:35<00:15, 2MB/s]

        # 4，自定义 bar_format
        # tqdm(total=100, bar_format="{percent:3.0f}%")
        #  75%

        # 5，详细信息
        # tqdm(total=100, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n}/{total} [{rate_fmt}{postfix}]")
        # 正在下载:  90%|████████████████████████ | 90/100 [2MB/s]
        existing_file_size = 0
        if os.path.exists(model_name):
            existing_file_size = os.path.getsize(model_name)

        # 发送请求，如果需要从已下载部分继续下载
        req = urllib.request.Request(url)
        if existing_file_size:
            req.add_header('Range', f'bytes={existing_file_size}-')

        with urllib.request.urlopen(req) as response:
            # 确定总文件大小
            total_size = existing_file_size + int(response.headers.get('content-length', 0))
        with open(model_name, 'ab') as f, tqdm(
                desc=model_name,
                total=total_size,
                initial=existing_file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            chunk_size = 1024 * 1024  # 1MB 每块
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                bar.update(len(chunk))


if __name__ == '__main__':
    # 爬取的链接
    url_list = [
        'https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/tree/main',
        # 'https://huggingface.co/stabilityai/sd-vae-ft-mse/tree/main',
        # 'https://huggingface.co/runwayml/stable-diffusion-v1-5/tree/main',
    ]
    # 请求头
    head = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'
    }
    for url in url_list:
        root_dir_name = url.split('/')[-3]
        if not os.path.exists(root_dir_name):
            # 如果不存在，创建文件夹
            os.makedirs(root_dir_name)
            print(f"根目录文件夹 {root_dir_name} 创建成功")
        else:
            print(f"根目录文件夹 {root_dir_name} 已经存在\n")
        # bolg(url, head)
        start_run(url, head, root_dir_name)



