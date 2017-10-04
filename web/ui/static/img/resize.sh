#!/bin/sh
for size in 512 256 128 64;
  do convert $1.$2 -resize $size $1-$size.$2;
done;
mv $1.$2 $1-orig.$2
