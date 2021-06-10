#!/bin/bash

echo "" | tr -d '\n' > index.html

for i in *.zip
    do
        FILESIZE=$(stat -c%s "$i")
        echo "<a href=\"$i\">$i</a><td>$FILESIZE.0B</td>" >> index.html
    done
