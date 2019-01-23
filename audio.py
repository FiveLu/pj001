# -*- coding:utf-8 -*-
import pyaudio
from datetime import datetime
import webbrowser
from urllib import request
import json
import uuid
import wave
import pycurl
#  一些参数设置  具体看百度给的技术文档
CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 8000
CHANNELS = 1
RECORD_SECONDS = 5
#  Baidu开放云申请的在线语音识别sdk
api_key = "4l0v2yxFn4fuPDP8AObOtZ31"
secret_key = "fPiQaOAarSraUIQlEc9EQNG50OBTQTto"

access_token = ""
ret_text = ""

#  获取本机mac地址
def get_mac_address():
    return uuid.UUID(int=uuid.getnode()).hex[-12:]

#  获取API权限
def get_access_token():
    url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + api_key + "&client_secret=" + secret_key

    req = request.Request(url, method="POST")
    resp = request.urlopen(req)
    data = resp.read().decode('utf-8')
    json_data = json.loads(data)

    global access_token
    access_token = json_data['access_token']

    return access_token


#  获取 音频数据
def get_wav_data(wav_path):
    if wav_path is None or len(wav_path) == 0:
        return None

    fp = wave.open(wav_path, 'rb')
    nf = fp.getnframes()
    f_len = nf * 2
    audio_data = fp.readframes(nf)

    return audio_data, f_len

#  语音识别 返回数据参数
def dump_res(buf):
    resp_json = json.loads(buf.decode('utf-8'))
    ret = resp_json['result']

    global ret_text
    ret_text = ret[0]

    print(buf)


#  音频上传 并返回处理好的转为文本
def wav_to_text(wav_path):
    if wav_path is None or len(wav_path) == 0:
        return None

    if len(access_token) == 0:
        get_access_token()
        if len(access_token) == 0:
            return None

    data, f_len = get_wav_data(wav_path)

    url = 'http://vop.baidu.com/server_api?cuid=' + get_mac_address() + '&token=' + access_token
    http_header = [
        'Content-Type: audio/pcm; rate=8000',
        'Content-Length: %d' % f_len
    ]

    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(url))   # curl doesn't support unicode
    # c.setopt(c.RETURNTRANSFER, 1)
    c.setopt(c.HTTPHEADER, http_header)   # must be list, not dict
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 30)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.WRITEFUNCTION, dump_res)
    c.setopt(c.POSTFIELDS, data)
    c.setopt(c.POSTFIELDSIZE, f_len)
    c.perform() #pycurl.perform() has no return val

    return ret_text

#  记录语音
def record_wave(to_dir=None):
    if to_dir is None:
        to_dir = "./"

    pa = pyaudio.PyAudio()
    stream = pa.open(format = FORMAT,
                     channels = CHANNELS,
                     rate = RATE,
                     input = True,
                     frames_per_buffer = CHUNK)

    print("****** plz speaking  ******")

    save_buffer = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        audio_data = stream.read(CHUNK)
        save_buffer.append(audio_data)

    print("****** done recording ******")

    # stop
    stream.stop_stream()
    stream.close()
    pa.terminate()

    # wav path
    file_name = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")+".wav"
    if to_dir.endswith('/'):
        file_path = to_dir + file_name
    else:
        file_path = to_dir + "/" + file_name

    # save file
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    # join 前的类型
    wf.writeframes(b''.join(save_buffer))
    wf.close()

    return file_path


#  根据语音转换的文字实现相应操作
def browser_open_text(text):
    if text is None:
        return

    url = "http://www.baidu.com"
    if text.startswith("谷歌") or text.startswith("google"):
        url = "http://www.google.com"
    elif text.startswith("斗鱼") or text.startswith("douyu"):
        url = "https://www.douyu.com/"
    elif text.startswith("京东"):
        url = "https://www.jd.com"
    elif text.startswith("淘宝"):
        url = "https://www.taobao.com/"


    webbrowser.open_new_tab(url)

if __name__ == "__main__":
    to_dir = "./"
    file_path = record_wave(to_dir)

    text = wav_to_text(file_path)
    with open("lkj.txt","a+") as f:
        f.write(text)
        f.write("\n")
    browser_open_text(text)