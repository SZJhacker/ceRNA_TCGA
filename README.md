# 背景（background）
下载TCGA数据的表达数据，进行ceRNA分析，不同的目录代表不同的分析

## ID_convert
### 背景
同时，每个数据库都有自己独特的检索ID编号（例如Entrez ID,Ensembl ID 等等），也就是说同一个基因在不同的数据库中会有不同的名称。熟悉和使用这些id是我们后续分析的基础。  
MyGene.info 是一个由 NIH(美国国立卫生研究院)/NIGMS 资助，用于提供简单易用的 REST Web 服务来查询/检索基因注释数据的 API。 MyGene.info 目前包含了 NCBI Entrez、Ensembl、Uniprot、UCSC 在内的 20 多个数据库，MyGene.info 会每周从这些数据库中进行数据更新。虽然 MyGene.info 中包含的各个数据源可能有数据使用限制，但 MyGene.info 本身的服务是免费的，其源码托管在：  
https://github.com/biothings/mygene.info。  
虽然 MyGene.info 是一个在线的 web 服务，但它同时也提供了基于 R 和 Python 的第三方模块，源码均在 GitHub 上开源：  
MyGene R Client：https://github.com/biothings/mygene.R  
MyGene Python Client：https://github.com/biothings/mygene.py  
mygene 本质上是一个方便的 Python 模块，通过这个模块我们可以访问 MyGene.info 的基因查询 Web 服务。

