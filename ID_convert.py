#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import mygene, argparse
import pandas as pd

def convert_id(names):
    """默认对ensemble_id进行转换，后期可以考虑扩充"""
    mg = mygene.MyGeneInfo()
    gene_id = mg.querymany(names, scopes="ensembl.gene", fields=["entrezgene", "symbol", "name"], species='human', as_dataframe=True, df_index=False)
    return gene_id.rename(columns={u"query":"ensemble_id",u"symbol":"official_gene_symbol", u"name":"gene_name",u"entrezgene":"entrez_id"})

def main():
    parser = argparse.ArgumentParser(description="ID 转换")
    parser.add_argument('-i', '--infile', help='含有基因id的文件')
    parser.add_argument('-o', '--outfile', help='输出文件')
    args = parser.parse_args()

    geneExpr = pd.read_csv(args.infile)
    geneExpr["ensemble_id"] = geneExpr["ensemble_id"].str.replace(r'\.\d', '') # 去掉ensemble后面的版本号，方法很多，例如列表解析式
    collections_id = convert_id(geneExpr["ensemble_id"])
    geneExpr_converted_id = pd.merge(collections_id, geneExpr, on=['ensemble_id']).fillna("unknown")
    geneExpr_converted_id.to_csv(args.outfile, index=False )
    # collections_id.to_csv(args.outfile)
main()