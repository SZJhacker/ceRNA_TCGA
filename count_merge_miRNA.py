#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from argparse import ArgumentParser
import pandas as pd
import json


def main():
    parser = ArgumentParser(description="Merging the gene counts record from gzip file, which must be in the same directory as this script ")
    parser.add_argument('-j', '--jsonfile', help="The json file for metadata from cart", required=True)
    parser.add_argument('-o', '--countsfile', help="The file records all counting information for counts", default='summary_counts.csv')
    args = parser.parse_args()

    with open(args.jsonfile, 'r') as jsonfile:
        jsonfile_iter = iter(json.load(jsonfile))
        sample_first = next(jsonfile_iter)
        submitter_id, file_name = sample_first['associated_entities'][0]['entity_submitter_id'].strip(), sample_first['file_name'].strip()
        init_frame = pd.read_table(file_name, sep='\t', usecols=['miRNA_ID', 'read_count']).rename(columns={'read_count':submitter_id})

        for sample_next_info in jsonfile_iter:
            submitter_id, file_name = sample_next_info['associated_entities'][0]['entity_submitter_id'].strip(), sample_next_info[
                'file_name'].strip()
            sample_next = pd.read_table(file_name, sep='\t', usecols=['miRNA_ID', 'read_count']).rename(columns={'read_count':submitter_id})
            init_frame = pd.merge(init_frame, sample_next, on=['miRNA_ID'])
        init_frame.to_csv(args.countsfile, index=False)


if __name__ == '__main__':
    main()

