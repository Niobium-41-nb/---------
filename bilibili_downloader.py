import requests
import json
import os


def sanitize_filename(title):
    # 替换可能引起路径问题的字符
    return title.replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"',
                                                                                                                    '_').replace(
        '<', '_').replace('>', '_').replace('|', '_')


def download_bilibili_video(bv_id):
    # 获取视频基本信息
    info_url = "https://api.bilibili.com/x/web-interface/view"
    params = {'bvid': bv_id}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/'
    }

    try:
        response = requests.get(info_url, params=params, headers=headers)
        response.raise_for_status()
        data = json.loads(response.text)

        if data['code'] != 0:
            print(f"错误：{data.get('message', '未知错误')}")
            return

        cid = data['data']['cid']
        title = sanitize_filename(data['data']['title'])
        print(f"视频标题：{title}")

        # 获取视频下载地址
        play_url = "https://api.bilibili.com/x/player/playurl"
        params_play = {
            'bvid': bv_id,
            'cid': cid,
            'qn': 16,  # 360P
            'fnval': 1  # FLV格式
        }

        response_play = requests.get(play_url, params=params_play, headers=headers)
        play_data = json.loads(response_play.text)

        if play_data['code'] != 0:
            print(f"获取下载链接失败：{play_data.get('message', '未知错误')}")
            return

        durls = play_data['data']['durl']
        if not durls:
            print("未找到有效视频链接")
            return

        # 创建下载目录
        download_dir = '哔哩哔哩视频下载器\downloads'
        os.makedirs(download_dir, exist_ok=True)
        filename = os.path.join(download_dir, f"{title}.mp4")

        # 下载视频
        with open(filename, 'wb') as f:
            for index, segment in enumerate(durls, 1):
                print(f"正在下载第 {index}/{len(durls)} 个片段...")
                video_url = segment['url']
                with requests.get(video_url, headers=headers, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        print(f"下载完成！视频已保存至：{filename}")

    except Exception as e:
        print(f"发生错误：{str(e)}")


if __name__ == "__main__":
    bv_id = input("请输入B站视频BV号（例如 BV1Qe91YRELp）：").strip()
    if not bv_id.startswith('BV'):
        print("输入错误，请确认输入的是有效的BV号")
    else:
        download_bilibili_video(bv_id)