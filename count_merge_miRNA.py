#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from argparse import ArgumentParser
import pandas as pd
import json

def read_count(sample):
    submitter_id, file_name = sample['associated_entities'][0]['entity_submitter_id'].strip(), sample['file_name'].strip()
    raw_frame = pd.read_table(file_name, sep='\t', usecols=['miRNA_region', 'read_count']).rename(columns={'read_count':submitter_id})

    # miRNA中的数据只需要保留mature miRNA的表达矩阵
    mature_miRNA = raw_frame[raw_frame['miRNA_region'].str.contains('mature')]
    uni_mature_miRNA = mature_miRNA.groupby('miRNA_region', as_index=False).sum()
    uni_mature_miRNA['miRNA_region'] = uni_mature_miRNA['miRNA_region'].str.replace("mature,", "")
    return uni_mature_miRNA

def main():
    parser = ArgumentParser(description="Merging the gene counts record from gzip file, which must be in the same directory as this script ")
    parser.add_argument('-j', '--jsonfile', help="The json file for metadata from cart", required=True)
    parser.add_argument('-o', '--countsfile', help="The file records all counting information for counts", default='summary_counts.csv')
    args = parser.parse_args()

    with open(args.jsonfile, 'r') as jsonfile:
        jsonfile_iter = iter(json.load(jsonfile))
        sample_first = next(jsonfile_iter)
        init_frame = read_count(sample_first)
        # print(init_frame.head())

        for sample_next_info in jsonfile_iter:
            sample_next = read_count(sample_next_info)
            init_frame = pd.merge(init_frame, sample_next, on=['miRNA_region'])
        init_frame.to_csv(args.countsfile,index=False)


if __name__ == '__main__':
    main()

