#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from argparse import ArgumentParser
import pandas as pd
import re

def gtf_frame_construct(gtf_file):
    gtf_list = []
    with open(gtf_file) as gtf:
        for line in gtf:
            line_list = line.split('\t')
            if len(line_list)>2 and line_list[2]=='gene':
                ensemble_id, genename, gene_biotype = re.search(r'gene_id \"(.+?)\"\;.+gene_name "(.+?)"\;.+gene_biotype \"(.+?)\"\;', line).groups()
                gtf_list.append((ensemble_id, genename, gene_biotype))

    return pd.DataFrame(gtf_list, columns=['ensemble_id', 'gene_symbol', 'gene_biotype'])


def main():
    parser = ArgumentParser(description="利用gtf文件进行注释，依赖于ensemble id")
    parser.add_argument("-i", "--infile", help="需要进行注释的文件，目前只识别csv文件，并且对ensemble id进行注释")
    parser.add_argument("-o", "--outfile", help="输出文件名，目前也只输出csv文件")
    parser.add_argument("-g", "--gtf", help="指定gtf文件名，默认是Homo_sapiens.GRCh38.99.chr.gtf", default="Homo_sapiens.GRCh38.99.chr.gtf")
    args = parser.parse_args()

    gtf_frame = gtf_frame_construct(args.gtf)
    file_need_annotated = pd.read_csv(args.infile)
    file_need_annotated['ensemble_id'] = file_need_annotated['ensemble_id'].str.replace(r'\.\d+', '') # 去掉ensemble_id的版本号
    file_annotated = pd.merge(gtf_frame, file_need_annotated, on=['ensemble_id'], how='inner')
    file_annotated.to_csv(args.outfile, index=False)


if __name__ == '__main__':
    main()