
PY="python"

# https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

bashrc() {
    if [ "$1" == "-a" ];
    then
        code ~/.bashrc
    else
        code --wait ~/.bashrc && source "$HOME/.bashrc"
    fi
}

scripts() {
    if [ "$1" == "-a" ];
    then
        code -n "$SCRIPT_DIR"
    else
        code -n --wait "$SCRIPT_DIR" && source "$HOME/.bashrc"
    fi
}

reload() {
    source "$HOME/.bashrc"
}

#------------------------------------------------------------------------
# Git stuff

gupdate() {
    git rm -r --cached . && git add .
}


gcom() {

    if [ $# -eq 0 ]
    then
        git add -A && git commit
    else
        git add -A && git commit -m "$1"
    fi
}

gacp() {
    if [ $# -eq 0 ]
    then
        git add -A && git commit && git push
    else
        git add -A && git commit -m "$1" && git push
    fi
}

gdiff() {
    if [ -z "$2" ]
      then
        git difftool -y "$1"
      else
        git difftool -y "$1" "$2"
    fi
}

gtree() {
    git log --graph --simplify-by-decoration --pretty=format:'%d' --all
}


#------------------------------------------------------------------------
# Typora

typo() {
    TYPO="C:\Program Files\Typora\Typora.exe"
    if [ $# -eq 0 ]
    then
        start "" "$TYPO" ""
    else
        fullpath=$(realpath "$1")
        # Converts posix path to windows path, because 'start' starts a cmd process
        # The first -e block replaces drive (/x/... to x:\...) if it exists, and
        # second replaces remaining forwardslashes
        FILE=$( echo "$fullpath" | sed -e 's|^\/\([a-zA-Z]\)\/|\1:\\|' -e 's|\/|\\|g')
        if [ ! -f "$FILE" ]; then
            read -p "$1 not found - create it? [y/n] " -n 1 -r
            echo    # (optional) move to a new line
            if [[ $REPLY =~ ^[Yy]$ ]]
            then
                echo "Creating new file"
                touch "$FILE"
            else
                return
            fi
            
        fi
        start "" "$TYPO" "$FILE"
    fi
}


ds () {
    
    # We cannot 'cd' in the Python script, so we return the directory from the script, and 'cd' here
    dir=$($PY ${SCRIPT_DIR}/ds.py "$@")
    if [ $? -eq 0 ]; then
        cd "${dir}"
        return
    fi
    echo "$dir"
}


draw() {
    start "" "C:\Program Files\draw.io\draw.io.exe" "$@"
}