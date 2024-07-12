# First argument is the input folder with the views, second the resulting file, third is the rectangular resolution of one view in the result
TOTAL=$(shopt -s nullglob; files=($1/*); echo ${#files[@]};)
montage "$1/*.png" -tile "$TOTAL"x1 -geometry $3x$3+0+0 "$2"
