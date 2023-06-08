#!/bin/bash

# https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

#-------------------------------------------------------------------------------
# Loading config files

# Load the default one to reset the variables
source "${SCRIPT_DIR}/_config.sh"

if [[ -f "${SCRIPT_DIR}/config.sh" ]]; then
    source "${SCRIPT_DIR}/config.sh"
fi

runpython() {
    if [[ ! -f "${PYTHON_PATH}" ]]; then
        echo "Invalid PYTHON_PATH: '${PYTHON_PATH}'"
        return
    fi
    "$PYTHON_PATH" "$@"
}

#-------------------------------------------------------------------------------

startssh() {
    eval "$(ssh-agent -s)"
    ssh-add "${SSH_KEY}"
}


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


#-------------------------------------------------------------------------------
# Git stuff

gupdate() {
    git rm -r --cached '*' && git add -A
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


#-------------------------------------------------------------------------------
to_windows_path() {
    if [ ! $# -eq 1 ]; then
        return -1
    fi

    bashpath="$1"

    # Converts posix path to windows path, because 'start' starts a cmd'
    # process The first -e block replaces drive (/x/... to x:\...) if it
    # exists, and second replaces remaining forwardslashes
    windowspath=$( echo "$bashpath" | sed -e 's|^\/\([a-zA-Z]\)\/|\1:\\|' -e 's|\/|\\|g')
    echo "$windowspath"
}

copypath() {
    unset p

    if [ $# -eq 0 ]; then
        p=$(pwd -W)
    elif [ -f "$1" ]; then
        realfile=$(realpath "$1")
        p=$(to_windows_path "$realfile")
        echo $p
    elif [ -d "$1" ]; then
        realdir=$(realpath "$1")
        p=$(to_windows_path "$realdir")
    else
        echo "Unknown file or directory '$1'"
        return -1;
    fi

    if [[ -n "$p" ]]; then
        echo "$p" | clip
        echo "Copied '$p' to clipboard"
    fi
}

mcd() {
    mkdir "$1" && cd "$1"
}


#-------------------------------------------------------------------------------
# Mark Text
md() {
    if [[ ! -f "${MARK_TEXT_PATH}" ]]; then
        echo "Invalid MARK_TEXT_PATH: '${MARK_TEXT_PATH}'"
        return
    fi

    if [ $# -eq 0 ]; then
        start "" "${MARK_TEXT_PATH}"
        return
    fi

    fullpath=$(realpath "$1")

    if [ ! -e "$fullpath" ]; then
        read -p "File $1 not found - create it? [y/n] " -n 1 -r
        echo  # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Creating new file"
            touch "$fullpath"
        else
            return
        fi
        
    fi
    start "" "${MARK_TEXT_PATH}" "${fullpath}"
}

#-------------------------------------------------------------------------------
# Typora

typo() {
    if [[ ! -f "$TYPORA_PATH" ]]; then
        echo "Invalid TYPORA_PATH: '${TYPORA_PATH}'"
        return
    fi

    if [ $# -eq 0 ]
    then
        start "" "${TYPORA_PATH}" ""
    else
        fullpath=$(realpath "$1")
        # Converts posix path to windows path, because 'start' starts a cmd'
        # process The first -e block replaces drive (/x/... to x:\...) if it
        # exists, and second replaces remaining forwardslashes
        FILE=$( echo "$fullpath" | sed -e 's|^\/\([a-zA-Z]\)\/|\1:\\|' -e 's|\/|\\|g')

        if [ ! -e "$FILE" ]; then
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
        start "" "${TYPORA_PATH}" "$FILE"
    fi
}

# ------------------------------------------------------------------------------
unity() {
    if [[ ! -f "$UNITY_PATH" ]]; then
        echo "Invalid UNITY_PATH: '${UNITY_PATH}'"
        return
    fi

    if [ $# -eq 0 ]
    then
        start "" "${UNITY_PATH}"
    else
        start "" "${UNITY_PATH}" "-projectPath" "."
    fi
}


# ------------------------------------------------------------------------------

note() {
    if [[ ! -f "$NOTE_PATH" ]]; then
        echo "Invalid NOTE_PATH: '${NOTE_PATH}'"
        return
    fi

    if [[ ! -f "$TYPORA_PATH" ]]; then
        echo "Invalid TYPORA_PATH: '${TYPORA_PATH}'"
        return
    fi

    typo "${NOTE_PATH}"
}

todo() {
    if [[ -f "${TODO_PATH}" || -d "${TODO_PATH}" ]]
    then
        code "${TODO_PATH}"
    else
        echo "Invalid TODO_PATH: '${TODO_PATH}'"
    fi    
}

# ------------------------------------------------------------------------------


ds() {
    # We cannot 'cd' in the Python script, so we return the directory from the
    # script, and 'cd' here
    dir=$(runpython ${SCRIPT_DIR}/ds.py "$@")
    if [ $? -eq 0 ]; then
        cd "${dir}"
        return
    fi
    echo "$dir"
}


draw() {
    if [[ ! -f "${DRAW_IO_PATH}" ]]; then
        echo "Invalid DRAW_IO_PATH: '${DRAW_IO_PATH}'"
        return
    fi
    start "" "${DRAW_IO_PATH}" "$@"
}


msbuild() {
    if [[ ! -f "${MSBUILD_PATH}" ]]; then
        echo "Invalid MSBUILD_PATH: '${MSBUILD_PATH}'"
        return
    fi
    "${MSBUILD_PATH}" "$@"
}


mstest() {
    if [[ ! -f "${MSTEST_PATH}" ]]; then
        echo "Invalid MSTEST_PATH: '${MSTEST_PATH}'"
        return
    fi
    "${MSTEST_PATH}" "$@"
}


vs() {
    if [[ ! -f "${VISUAL_STUDIO_PATH}" ]]; then
        echo "Invalid VISUAL_STUDIO_PATH: '${VISUAL_STUDIO_PATH}'"
        return
    fi

    if [[ $# -eq 0 ]]; then
        start "" "${VISUAL_STUDIO_PATH}"
    fi

    if [[ -d "$1" ]]; then
        # Get name of first .sln file in directory
        solution="$(ls "$1" | grep ".sln" | head -n1)"
        
        if [[ -z "${solution}" ]]; then
            echo "Error: no .sln file in directory '$1'"
            return
        fi

        start "" "${VISUAL_STUDIO_PATH}" "$1/${solution}"
        return
    fi

    if [[ -f "$1" ]]; then
        start "" "${VISUAL_STUDIO_PATH}" "$1"
    else
        echo "Error: cannot find solution '$1'"
    fi
}


pdf() {
    if [[ ! -f "${PDF_READER_PATH}" ]]; then
        echo "Invalid PDF_READER_PATH: '${PDF_READER_PATH}'"
        return
    fi
    if [[ $# -eq 0 ]]; then
        start "" "${PDF_READER_PATH}"
    else
        start "" "${PDF_READER_PATH}" "$@"
    fi
}


sub() {
    if [[ ! -f "${SUBLIME_TEXT_PATH}" ]]; then
        echo "Invalid SUBLIME_TEXT_PATH: '${SUBLIME_TEXT_PATH}'"
        return
    fi
    if [[ $# -eq 0 ]]; then
        start "" "${SUBLIME_TEXT_PATH}"
    else
        start "" "${SUBLIME_TEXT_PATH}" "$@"
    fi
}

#-------------------------------------------------------------------------------
# Loading local scripts last, so that I may override global scripts on the local
# machine

if [[ -n ${LOCAL_SCRIPT_FILES+x} ]]; then
    for local_script in ${LOCAL_SCRIPT_FILES[@]}; do
        source "${SCRIPT_DIR}/${local_script}"
    done
fi