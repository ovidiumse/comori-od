#!/usr/bin/bash

tmux new -s prod -x "$(tput cols)" -y "$(tput lines)" -d
tmux send-keys -t prod "ssh ubuntu@comori-od.ro" C-m
tmux send-keys -t prod "watch docker ps" C-m
tmux split -v -t prod -p 68
tmux split -h -t prod

tmux select-pane -t 1
tmux split -v -t prod

tmux select-pane -t 3
tmux split -v -t prod

tmux select-pane -t 1
tmux send-keys -t prod "ssh ubuntu@comori-od.ro" C-m

tmux select-pane -t 3
tmux send-keys -t prod "cd projects/comori-od/web/comori-od-all" C-m
tmux send-keys -t prod "./tail-prod.sh" C-m

tmux select-pane -t 2
tmux send-keys -t prod "ssh ubuntu@comori-od.ro" C-m

tmux select-pane -t 4
tmux send-keys -t prod "ssh ubuntu@comori-od.ro" C-m
tmux send-keys -t prod "top -i" C-m

tmux select-pane -t 0
tmux split -h -t prod
tmux send-keys -t prod "ssh ubuntu@comori-od.ro" C-m
tmux send-keys -t prod "docker stats" C-m

tmux attach -t prod