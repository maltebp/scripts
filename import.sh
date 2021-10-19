
PY="python"

# https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ds () {
    # echo "$@"
    
    dir=$($PY ${SCRIPT_DIR}/ds.py "$@")
    if [ $? -eq 0 ]; then
        cd "${dir}"
        return
    fi
    echo "$dir"
}