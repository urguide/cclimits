#!/usr/bin/env bash

##  cclimits   查看全部AI訂閱資源的用量
curl -o ~/.local/bin/cclimits https://raw.githubusercontent.com/urguide/cclimits/main/lib/cclimits.py
chmod +x ~/.local/bin/cclimits
##  tmux warpper可以讓tmux刷新的時候畫面不卡
curl -o ~/.local/bin/cclimits-tmux https://raw.githubusercontent.com/urguide/cclimits/main/bin/cclimits-tmux
chmod +x ~/.local/bin/cclimits-tmux

