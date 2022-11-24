#!/usr/bin/bash

tmux new -s beta -x "$(tput cols)" -y "$(tput lines)" -d
tmux send-keys -t beta "ssh ovidiu@ubuntu-home" C-m
tmux send-keys -t beta "watch docker ps" C-m
tmux split -v -t beta -p 68
tmux split -h -t beta

tmux select-pane -t 1
tmux split -v -t beta

tmux select-pane -t 3
tmux split -v -t beta

tmux select-pane -t 1
tmux send-keys -t beta "ssh ovidiu@ubuntu-home" C-m

tmux select-pane -t 3
tmux send-keys -t beta "cd projects/comori-od/web/comori-od-all" C-m
# tmux send-keys -t prod "./tail-prod.sh" C-m

tmux select-pane -t 2
tmux send-keys -t beta "ssh ovidiu@ubuntu-home" C-m

tmux select-pane -t 4
tmux send-keys -t beta "ssh ovidiu@ubuntu-home" C-m
tmux send-keys -t beta "docker stats" C-m

tmux select-pane -t 0
tmux split -h -t beta
tmux send-keys -t beta "ssh ovidiu@ubuntu-home" C-m
tmux send-keys -t beta "top -i" C-m

tmux attach -t beta