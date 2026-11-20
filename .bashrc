echo 999999
alias dpython='docker compose exec -it app sh -c '\''cd "$1" && shift && exec python "$@"'\'' sh "$(realpath --relative-to=/workspaces/notifica/src "$PWD")"'