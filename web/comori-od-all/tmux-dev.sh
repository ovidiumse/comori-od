#!/usr/bin/bash

tmux new -s dev -x "$(tput cols)" -y "$(tput lines)" -d
tmux send-keys -t dev "watch docker ps" C-m
tmux split -v -t dev -p 75
tmux split -h -t dev

tmux select-pane -t 1
tmux split -v -t dev

tmux select-pane -t 3
tmux split -v -t dev

tmux select-pane -t 1
tmux send-keys -t dev "cd projects/comori-od/web/comori-od-all" C-m

tmux select-pane -t 3
tmux send-keys -t dev "cd projects/comori-od/web/comori-od-all" C-m
tmux send-keys -t dev "./tail-dev.sh" C-m

tmux select-pane -t 2
tmux send-keys -t dev "docker stats" C-m

tmux select-pane -t 4
tmux send-keys -t dev "top -i" C-m

tmux select-pane -t 2
tmux split -v -t dev
tmux send-keys -t dev "cd projects/comori-od/tools" C-m

tmux attach -t dev