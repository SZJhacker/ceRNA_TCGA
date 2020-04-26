# 背景（background）
竞争性内源RNA（ceRNA）是近几年来备受学术界关注的对象，它代表了一种全新的基因表达调控模式，相比miRNA调控网络，ceRNA调控网络更为精细和复杂，涉及更多的RNA分子，包括mRNA、编码基因的假基因、长链非编码RNA和miRNA等，它为科研工作者提供一个全新的视角进行转录组研究，有助于更全面、深入地解释一些生物学现象。  
[TCGA](https://portal.gdc.cancer.gov/)（The cancer genome atlas，癌症基因组图谱）由 National Cancer Institute(NCI，美国国家癌症研究所) 和 National Human Genome Research Institute（NHGRI，美国国家人类基因组研究所）于 2005 年联合启动的项目， 收录了各种人类癌症（包括亚型在内的肿瘤）的临床数据，基因组变异，mRNA表达，miRNA表达，甲基化等数据，是癌症研究者很重要的数据来源。TCGA应用高通量基因组分析技术，通过更好地了解这种疾病的遗传基础，提高了我们诊断，治疗和预防癌症的能力。


下载TCGA数据的表达数据，进行ceRNA分析，不同的目录代表不同的分析
1. 下载TCGA中的RNA-Seq数据，因为新版的TCGA数据库是用Ensembl id作为基因的命名的，所以这些RNA-Seq基因表达量文件中必然也包含了lncRNA的表达量数据  
2. 获取TCGA RNA表达量的Ensembl id中属于lncRNA的id  
3. 从总的RNA表达量文件中提取lncRNA的表达量数据

## 1 数据下载
本次分析的数据全部是来源于TCGA，TCGA官网提供了很好的[数据下载指南](https://docs.gdc.cancer.gov/Data_Transfer_Tool/Users_Guide/Preparing_for_Data_Download_and_Upload/), 不喜欢看英文的，中文教程可以参考知乎上的这篇文章：https://zhuanlan.zhihu.com/p/63109401    

TCGA数据库的数据主要是使用gdc-client工具下载的(不推荐使用购物车下载，因为数据太大时使用购物车下载很容易断，而且它不支持断点传输），命令如下：  
```bash
conda install -c bioconda gdc-client  # 如果下载完成gdc-client之后，就不用安装了
nohup ./gdc-client download -m gdc_manifest_20200310_115553.txt & # 参考命令，根据你的manifest文件进行下载
```
## 2 数据整合
这一步的目的很简单，就是将之前下载的数据整合到一起，所以实现的方式很多。  
json文件里面记录了每个样本的TCGA编号，我们要根绝ensemble id将所有的数据merge到一起。count_merge.py不是很完善，需要一定的手动，需要下载的gz文件放到和count_merge.py一个目录中，然后使用。该脚本使用到json文件中的每个样本的TCGA编号，并且获取该样本对应的压缩包filename，然后将这些文件进行整合。
## 2 ID转换ID_convert
### 背景
ID转换代买最主要的思路就是：**找对原ID和你要注释的ID的对应关系**，对应关系记录在：ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/  

每个数据库都有自己独特的检索ID编号（例如Entrez ID,Ensembl ID 等等），也就是说同一个基因在不同的数据库中会有不同的名称。熟悉和使用这些id是我们后续分析的基础。关于常用的数据库的背景知识，我推荐大家可以通过《[超精华生信ID总结，想踏入生信大门的你-值得拥有](https://cloud.tencent.com/developer/article/1358527)》进行了解。  

python，R等多种编程语言已经实现了这些对应关系的包，使我们可以不用区ncbi的官网下载id对应关系的文件。
> MyGene.info 是一个由 NIH(美国国立卫生研究院)/NIGMS 资助，用于提供简单易用的 REST Web 服务来查询/检索基因注释数据的 API。 MyGene.info 目前包含了 NCBI Entrez、Ensembl、Uniprot、UCSC 在内的 20 多个数据库，MyGene.info 会每周从这些数据库中进行数据更新。虽然 MyGene.info 中包含的各个数据源可能有数据使用限制，但 MyGene.info 本身的服务是免费的，其源码托管在：  
https://github.com/biothings/mygene.py。  

虽然 MyGene.info 是一个在线的 web 服务，但它同时也提供了基于 R 和 Python 的第三方模块，源码均在 GitHub 上开源：  
MyGene R Client：https://github.com/biothings/mygene.R  
MyGene Python Client：https://github.com/biothings/mygene.py  
mygene 本质上是一个方便的 Python 模块，通过这个模块我们可以访问 MyGene.info 的基因查询 Web 服务。

### 代码功能
TCGA数据使用ensemble id作为基因名称，所以ID_convert.py主要是完成对ensemble id的转换，新增的id内容包括：Entrez id, officical gene symbol, gene name。 如果需要增加或替换其他id，可以参考mygene的官方文档对代码中mg.querymany()中的fields进行修改。

