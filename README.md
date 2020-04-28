# 背景（background）
竞争性内源RNA（ceRNA）是近几年来备受学术界关注的对象，它代表了一种全新的基因表达调控模式，相比miRNA调控网络，ceRNA调控网络更为精细和复杂，涉及更多的RNA分子，包括mRNA、编码基因的假基因、长链非编码RNA和miRNA等，它为科研工作者提供一个全新的视角进行转录组研究，有助于更全面、深入地解释一些生物学现象。  
[TCGA](https://portal.gdc.cancer.gov/)（The cancer genome atlas，癌症基因组图谱）由 National Cancer Institute(NCI，美国国家癌症研究所) 和 National Human Genome Research Institute（NHGRI，美国国家人类基因组研究所）于 2005 年联合启动的项目， 收录了各种人类癌症（包括亚型在内的肿瘤）的临床数据，基因组变异，mRNA表达，miRNA表达，甲基化等数据，是癌症研究者很重要的数据来源。TCGA应用高通量基因组分析技术，通过更好地了解这种疾病的遗传基础，提高了我们诊断，治疗和预防癌症的能力。

## 1 数据下载
本次分析的数据全部是来源于TCGA，TCGA官网提供了很好的[数据下载指南](https://docs.gdc.cancer.gov/Data_Transfer_Tool/Users_Guide/Preparing_for_Data_Download_and_Upload/), 不喜欢看英文的，中文教程可以参考知乎上的这篇文章：https://zhuanlan.zhihu.com/p/63109401    

TCGA数据库的数据主要是使用gdc-client工具下载的(不推荐使用购物车下载，因为数据太大时使用购物车下载很容易断，而且它不支持断点传输），命令如下：  
```bash
conda install -c bioconda gdc-client  # 如果下载完成gdc-client之后，就不用安装了
nohup ./gdc-client download -m gdc_manifest_20200310_115553.txt & # 参考命令，根据你的manifest文件进行下载
```
## 2 数据整合
这一步的目的很简单，就是将之前下载的数据整合到一起，所以实现的方式很多。  

json文件里面记录了每个样本的TCGA编号，我们要根据ensemble id将所有的数据merge到一起。count_merge.py不是很完善，需要一定的手动，需要下载的gz文件放到和count_merge.py一个目录中，然后使用。该脚本使用到json文件中的每个样本的TCGA编号，并且获取该样本对应的压缩包filename，然后将这些文件进行整合。  

*PS: 该代码主要是将数据merge到一起，唯一可能算是困难点的是读取压缩文件的内容，思路上并没有什么难点*
## 3 ID转换ID_convert
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

## 3 基因注释
1. 下载TCGA中的RNA-Seq数据，因为新版的TCGA数据库是用Ensembl id作为基因的命名的，所以这些RNA-Seq基因表达量文件中必然也包含了lncRNA的表达量数据  
2. 获取TCGA RNA表达量的Ensembl id中不同类型RNA的id  
3. 从总的RNA表达量文件中提取各种RNA的表达量数据

gtf(gene transfer format)，主要是用来对基因进行注释, 文件的格式如下：
```
1       havana  gene    11869   14409   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene";
1       havana  transcript      11869   14409   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000456328"; transcript_version "2"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-202"; transcript_source "havana"; transcript_biotype "processed_transcript"; tag "basic"; transcript_support_level "1";
1       havana  exon    11869   12227   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000456328"; transcript_version "2"; exon_number "1"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-202"; transcript_source "havana"; transcript_biotype "processed_transcript"; exon_id "ENSE00002234944"; exon_version "1"; tag "basic"; transcript_support_level "1";
1       havana  exon    12613   12721   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000456328"; transcript_version "2"; exon_number "2"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-202"; transcript_source "havana"; transcript_biotype "processed_transcript"; exon_id "ENSE00003582793"; exon_version "1"; tag "basic"; transcript_support_level "1";
1       havana  exon    13221   14409   .       +       .       gene_id "ENSG00000223972"; gene_version "5"; transcript_id "ENST00000456328"; transcript_version "2"; exon_number "3"; gene_name "DDX11L1"; gene_source "havana"; gene_biotype "transcribed_unprocessed_pseudogene"; transcript_name "DDX11L1-202"; transcript_source "havana"; transcript_biotype "processed_transcript"; exon_id "ENSE00002312635"; exon_version "1"; tag "basic"; transcript_support_level "1";
```
> GFF文件是以tab键分割的9列组成，以下为每一列的对应信息：  
> 1. seq_id：序列的编号，一般为chr或者scanfold编号；  
> 2. source: 注释的来源，一般为数据库或者注释的机构，如果未知，则用点“.”代替
> 3. type: 注释信息的类型，比如Gene、cDNA、mRNA、CDS等;
> 4. start: 该基因或转录本在参考序列上的起始位置；(从1开始，包含);  
> 5. end: 该基因或转录本在参考序列上的终止位置；(从1开始，包含);
> 6. score: 得分，数字，是注释信息可能性的说明，可以是序列相似性比对时的E-values值或者基因预测是的P-values值，.表示为空;
> 7. strand: 该基因或转录本位于参考序列的正链(+)或负链(-)上;
> 8. phase: 仅对注释类型为“CDS”有效，表示起始编码的位置，有效值为0、12. (对于编码蛋白质的CDS来说，本列指定下一个密码子开始的位置。每3个核苷酸翻译一个氨基酸，从0开始，CDS的起始位置，除以3，余数就是这个值，，表示到达下一个密码子需要跳过的碱基个数。该编码区第一个密码子的位置，取值0,1,2。0表示该编码框的第一个密码子第一个碱基位于其5’末端；1表示该编码框的第一个密码子的第一个碱基位于该编码区外；2表示该编码框的第一个密码子的第一、二个碱基位于该编码区外；如果Feature为CDS时，必须指明具体值。)；
> 9. attributes: 一个包含众多属性的列表，格式为“标签＝值”(tag=value)，以多个键值对组成的注释信息描述，键与值之间用“=”，不同的键值用“；”隔开，一个键可以有多个值，不同值用“,”分割。注意如果描述中包括tab键以及“，= ；”，要用URL转义规则进行转义，如tab键用 代替。键是区分大小写的，以大写字母开头的键是预先定义好的，在后面可能被其他注释信息所调用。

我们需要的信息是第9列中的**gene_id, gene_name**和**gene_biotype**。  

annotated_gtf.py的解决思路是：
1. 利用正则表达是匹配这些内容建立字典，以gene_id为key，gene_id,gene_name和gene_biotype组成
2. 遍历要注释的gene，如果字典里面没有，返回[unknown，unknown, unknown]为value的字典
3. 构建含有注释信息的datafram
4. 将含有注释信息的dataframe与要注释的dataframe进行merge  
*PS：该程序的时间复杂度为至少为O(2n),感觉可以进一步优化。*