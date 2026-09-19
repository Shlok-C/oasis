# go through the entire src/ folder and compile every file into a pdf with the same name in the output folder.

for file in src/*; do
    if [ -f "$file" ]; then 
        filename="${file##*/}"
        name="${filename%.*}"
        echo "$file ->" "$name".pdf
        
        typst compile "$file" out/"$name.pdf"
    fi
done