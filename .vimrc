" .vimrc configuration with COC, Python/C autocompletion and Catppuccin theme

" ===== Basic Settings =====
set nocompatible              " Use Vim settings rather than Vi settings
syntax enable                 " Enable syntax highlighting
set number                    " Show line numbers
set relativenumber            " Show relative line numbers
set hidden                    " Allow buffer switching without saving
set cursorline                " Highlight current line
set showmatch                 " Highlight matching brackets
set mouse=a                   " Enable mouse support
set clipboard=unnamedplus     " Use system clipboard
set encoding=utf-8            " Use utf-8 encoding
set fileencoding=utf-8        " Use utf-8 file encoding
set termencoding=utf-8        " Use utf-8 terminal encoding
set backspace=indent,eol,start " Make backspace work as expected
set laststatus=2              " Always show status line
set noshowmode                " Don't show mode (lightline will show it)
set updatetime=300            " Faster update time for better UX
set shortmess+=c              " Don't pass messages to completion menu
set signcolumn=yes            " Always show signcolumn
set cmdheight=2               " More space for displaying messages
set timeoutlen=500            " Time to wait for a mapped sequence to complete

" Indentation settings
set autoindent                " Auto indent
set smartindent               " Smart indent
set expandtab                 " Use spaces instead of tabs
set tabstop=4                 " Tab is 4 spaces
set shiftwidth=4              " Use 4 spaces for indent
set softtabstop=4             " 4 spaces when editing

" Search settings
set incsearch                 " Incremental search
set hlsearch                  " Highlight search results
set ignorecase                " Ignore case when searching
set smartcase                 " Case-sensitive if search contains uppercase

" File management
set nobackup                  " No backup files
set nowritebackup             " No backup files during write
set noswapfile                " No swap files

" Performance
set lazyredraw                " Don't redraw while executing macros

" ===== Plugins =====
" Install vim-plug if not installed
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')

" Catppuccin Theme
Plug 'catppuccin/vim', { 'as': 'catppuccin' }

" COC for completion
Plug 'neoclide/coc.nvim', {'branch': 'release'}

" Status Line
Plug 'itchyny/lightline.vim'
Plug 'mengelbrecht/lightline-bufferline'

" File Explorer
Plug 'preservim/nerdtree'
Plug 'ryanoasis/vim-devicons'  " Icons for NERDTree

" Fuzzy Finder
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
Plug 'junegunn/fzf.vim'

" Git Integration
Plug 'tpope/vim-fugitive'
Plug 'airblade/vim-gitgutter'

" Syntax Highlighting & Language Support
Plug 'sheerun/vim-polyglot'  " Language packs

" Editor Enhancement
Plug 'jiangmiao/auto-pairs'   " Auto close pairs
Plug 'tpope/vim-commentary'   " Comment stuff out
Plug 'tpope/vim-surround'     " Quoting/parenthesizing
Plug 'machakann/vim-highlightedyank'  " Highlight yanked text

" Snippets
Plug 'honza/vim-snippets'

call plug#end()

" ===== Theme Configuration =====
" Enable true color support
if exists('+termguicolors')
  set termguicolors
endif

" Set Catppuccin theme
colorscheme catppuccin_mocha  " Options: catppuccin_latte, catppuccin_frappe, catppuccin_macchiato, catppuccin_mocha

" Configure lightline with Catppuccin
let g:lightline = {
      \ 'colorscheme': 'catppuccin',
      \ 'active': {
      \   'left': [ [ 'mode', 'paste' ],
      \             [ 'gitbranch', 'readonly', 'filename', 'modified' ] ],
      \   'right': [ [ 'lineinfo' ],
      \              [ 'percent' ],
      \              [ 'fileformat', 'fileencoding', 'filetype' ] ]
      \ },
      \ 'component_function': {
      \   'gitbranch': 'FugitiveHead'
      \ },
      \ 'tabline': {
      \   'left': [ ['buffers'] ],
      \   'right': [ ['close'] ]
      \ },
      \ 'component_expand': {
      \   'buffers': 'lightline#bufferline#buffers'
      \ },
      \ 'component_type': {
      \   'buffers': 'tabsel'
      \ }
      \ }

" ===== COC Configuration =====
" Install extensions
let g:coc_global_extensions = [
      \ 'coc-json',
      \ 'coc-pairs',
      \ 'coc-python',
      \ 'coc-clangd',
      \ 'coc-snippets',
      \ 'coc-highlight',
      \ 'coc-explorer',
      \ 'coc-git'
      \ ]

" Python path for COC
if has('macunix')
  let g:python3_host_prog = '/usr/local/bin/python3'
elseif has('unix')
  let g:python3_host_prog = '/usr/bin/python3'
endif

" Use tab for trigger completion with characters ahead and navigate
inoremap <silent><expr> <TAB>
      \ coc#pum#visible() ? coc#pum#next(1) :
      \ CheckBackspace() ? "\<Tab>" :
      \ coc#refresh()
inoremap <expr><S-TAB> coc#pum#visible() ? coc#pum#prev(1) : "\<C-h>"

" Make <CR> accept selected completion item
inoremap <silent><expr> <CR> coc#pum#visible() ? coc#pum#confirm()
                              \: "\<C-g>u\<CR>\<c-r>=coc#on_enter()\<CR>"

function! CheckBackspace() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" Use <c-space> to trigger completion
inoremap <silent><expr> <c-space> coc#refresh()

" Use `[g` and `]g` to navigate diagnostics
nmap <silent> [g <Plug>(coc-diagnostic-prev)
nmap <silent> ]g <Plug>(coc-diagnostic-next)

" GoTo code navigation
nmap <silent> gd <Plug>(coc-definition)
nmap <silent> gy <Plug>(coc-type-definition)
nmap <silent> gi <Plug>(coc-implementation)
nmap <silent> gr <Plug>(coc-references)

" Use K to show documentation in preview window
nnoremap <silent> K :call ShowDocumentation()<CR>

function! ShowDocumentation()
  if CocAction('hasProvider', 'hover')
    call CocActionAsync('doHover')
  else
    call feedkeys('K', 'in')
  endif
endfunction

" Highlight the symbol and its references when holding the cursor
autocmd CursorHold * silent call CocActionAsync('highlight')

" Symbol renaming
nmap <leader>rn <Plug>(coc-rename)

" Formatting selected code
xmap <leader>f  <Plug>(coc-format-selected)
nmap <leader>f  <Plug>(coc-format-selected)

" Apply AutoFix to problem on the current line
nmap <leader>qf  <Plug>(coc-fix-current)

" Run the Code Lens action on the current line
nmap <leader>cl  <Plug>(coc-codelens-action)

" Use <leader>a to show all diagnostics
nnoremap <silent><nowait> <leader>a  :<C-u>CocList diagnostics<cr>

" ===== NERDTree Configuration =====
" Toggle NERDTree
nnoremap <C-n> :NERDTreeToggle<CR>
" Exit Vim if NERDTree is the only window left
autocmd BufEnter * if tabpagenr('$') == 1 && winnr('$') == 1 && exists('b:NERDTree') && b:NERDTree.isTabTree() | quit | endif
" If another buffer tries to replace NERDTree, put it in the other window
autocmd BufEnter * if bufname('#') =~ 'NERD_tree_\d\+' && bufname('%') !~ 'NERD_tree_\d\+' && winnr('$') > 1 | let buf=bufnr() | buffer# | execute "normal! \<C-W>w" | execute 'buffer'.buf | endif

" ===== FZF Configuration =====
nnoremap <C-p> :Files<CR>
nnoremap <leader>b :Buffers<CR>
nnoremap <leader>g :Rg<CR>

" ===== Key Mappings =====
" Set leader key
let mapleader = " "

" Better window navigation
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Better indenting in visual mode (stay in visual mode)
vnoremap < <gv
vnoremap > >gv

" Move selected line / block of text up/down
vnoremap J :m '>+1<CR>gv=gv
vnoremap K :m '<-2<CR>gv=gv

" Buffers navigation
nnoremap <leader>bn :bn<CR>    " Next buffer
nnoremap <leader>bp :bp<CR>    " Previous buffer
nnoremap <leader>bd :bd<CR>    " Delete buffer

" Clear search highlighting
nnoremap <leader>h :noh<CR>

" Save and quit shortcuts
nnoremap <leader>w :w<CR>
nnoremap <leader>q :q<CR>
nnoremap <leader>wq :wq<CR>

" ===== COC Configuration File =====
" Create coc-settings.json if it doesn't exist
