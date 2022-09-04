#!/bin/sh
if [ "$1" == "-h" ] ; then
    echo "Seive flags"
    exit 0
fi

rm -f ./res/*
rm -f ./bin/*
rm -f ./ir/*

ls ../Feature_Extraction/ir > ./data/IR_Candidates.in

cat ./data/IR_Candidates.in | parallel -j 15 bash Flag_Seive_Core.sh