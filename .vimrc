augroup python_file_settings " {
  noremap <leader>r :wa<CR> <bar> :Silent $(tmux send-keys -t left C-e C-u C-c 'python %' C-m)<CR>
augroup END }"
