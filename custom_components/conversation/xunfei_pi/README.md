# 编译方式

```bash
# 编译
source 32bit_make.sh
# 切换到bin目录
cd ../../bin

# 开始录音，需要安装依赖 `sudo apt-get install alsa-oss`
arecord -d 3 -r 16000 -c 1 -t wav -f S16_LE voice.wav

# 开始语音识别
./iat_sample

```