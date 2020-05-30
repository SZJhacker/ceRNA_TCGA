[TOC]
# 前沿

目前ceRNA的分析集中在癌症方向，在作物中或者动物中比较少，如果想应用在其他的物种中，必须要要透彻的理解数据和每一步分析的方法和意义。

# 知识背景（background）
竞争性内源RNA（ceRNA）是近几年来备受学术界关注的对象，它代表了一种全新的基因表达调控模式，相比miRNA调控网络，ceRNA调控网络更为精细和复杂，涉及更多的RNA分子，包括mRNA、编码基因的假基因、长链非编码RNA和miRNA等，它为科研工作者提供一个全新的视角进行转录组研究，有助于更全面、深入地解释一些生物学现象。 

ceRNA全称competing endogenous RNA，是一种能够竞争结合RNA的作用元件。通常lncRNA和circRNA会竞争结合miRNA，我们一般把lncRNA和circRNA可以称作ceRNA。ceRNA调控网络全称ceRNA regulation network，指的是有ceRNA参与的整个调控网络。而ceRNA分析指的是对整个ceRNA调控网络进行分析。一般有circRNA-miRNA-mRNA分析或lncRNA-miRNA-mRNA分析。 ceRNA调控网络分析中目前包含四种RNA，即mRNA、miRNA、lncRNA和circRNA。其中**miRNA处于调控的核心地位**，当miRNA被lncRNA或circRNA这类ceRNA竞争结合时，受miRNA调控的mRNA转录水平会上升。ceRNA调控机制作为普遍存在的现象，但是并非任何mRNA，lncRNA，circRNA都能够具有MRE，对于不具有共有MRE的mRNA，lncRNA，circRNA来说，就不存在ceRNA调控机制。



[TCGA](https://portal.gdc.cancer.gov/)（The cancer genome atlas，癌症基因组图谱）由 National Cancer Institute(NCI，美国国家癌症研究所) 和 National Human Genome Research Institute（NHGRI，美国国家人类基因组研究所）于 2005 年联合启动的项目， 收录了各种人类癌症（包括亚型在内的肿瘤）的临床数据，基因组变异，mRNA表达，miRNA表达，甲基化等数据，是癌症研究者很重要的数据来源。TCGA应用高通量基因组分析技术，通过更好地了解这种疾病的遗传基础，提高了我们诊断，治疗和预防癌症的能力。

# 数据分析流程
## 1 数据下载
本次分析的数据全部是来源于TCGA，TCGA官网提供了很好的[数据下载指南](https://docs.gdc.cancer.gov/Data_Transfer_Tool/Users_Guide/Preparing_for_Data_Download_and_Upload/), 不喜欢看英文的，中文教程可以参考知乎上的这篇文章：https://zhuanlan.zhihu.com/p/63109401    

TCGA数据库的数据主要是使用gdc-client工具下载的(不推荐使用购物车下载，因为数据太大时使用购物车下载很容易断，而且它不支持断点传输），命令如下：  
```bash
conda install -c bioconda gdc-client  # 如果下载完成gdc-client之后，就不用安装了
nohup ./gdc-client download -m gdc_manifest_20200310_115553.txt & # 参考命令，根据你的manifest文件进行下载
```
## 2 数据整合
这一步的目的很简单，就是将之前下载的数据整合到一起，所以实现的方式很多。  

json文件里面记录了每个样本的TCGA的[barcode编号](https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/)，我们要根据ensemble id将所有的数据merge到一起。count_merge.py不是很完善，需要一定的手动，需要下载的gz文件放到和count_merge.py一个目录中，然后使用。该脚本使用到json文件中的每个样本的TCGA编号，并且获取该样本对应的压缩包filename，然后将这些文件进行整合。  

*PS: 该代码主要是将数据merge到一起，唯一可能算是困难点的是读取压缩文件的内容，思路上并没有什么难点*  
**代码运行**:
```bash
python3 count_merge.py -j metadata.cart.2020-03-10.json -o summary_counts.csv # 参考命令，该文件必须和下载数据的压缩包在同一个文件夹下，后期考虑优化。
```
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
**代码运行**：
```bash
./ID_convert.py -i summary_counts.csv -o converted_expr.csv
```

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

gtf文件python也有相应的包进行解析，如：gtfparse， gffutils等。但是目前好像没有哪个是比较权威的机构做的，所以打算自己实现。

我们需要的信息是第9列中的**gene_id, gene_name**和**gene_biotype**。  

annotated_gtf.py的解决思路是：
1. 利用正则表达是匹配gtf文件中的注释内容构建元组列表，以gene_id,gene_name和gene_biotype为每个元组的内容
2. 将这些含有注释信息的元组列表组成gtf_frame
3. 将含有注释信息的gtf_frame与要注释的文件dataframe进行merge

*PS：该程序的时间复杂度为至少为O(2n),但是时间运行时间比较长，感觉可以进一步优化。*  
**运行代码**:
```bash
./annotated_gtf.py -i summary_counts.csv -o gene_symbol.csv &
```
## 4 RNA类型分离
上一部我们完成了基因的注释，其中gene_biotype那一列记录了基因的类型。

我们需要lncRNA或mRNA的表达矩阵，在上述文件中提去相应的gene_biotype那一列就行，这个感觉不用编程写代码，linux命令就可以完成，awk,sed,grep这三大文本操作工具都可以完成，以下是grep命令
```bash
egrep 'gene_biotype|lncRNA' gene_symbol.csv > lncRNA_symbol.csv # egrep基本等同于grep -E,使用扩展正则
egrep 'gene_biotype|protein_coding' gene_symbol.csv > mRNA_symbol.csv
```

## 5 差异基因分析
### 背景知识
泊松分布是二项分布n很大而p很小时的一种极限形式, 泊松分布理解可参考知乎上“[甜心小馒头](https://www.zhihu.com/question/26441147/answer/429569625)”的讲解示例。
### R代码分析
目前了解的还不是很透彻，虽然完成了差异分析，但是还是有盲点，后期会更新这部分的心得。目前R在这方面做的应该是比较多的，其他的编程语言有没有相应的包替换R完成差异表达分析还没了解，因为这个不仅涉及到常用的P值检验或者矫正，更多的是对样本基因表达均一化的处理思路，例如edgeR包就有对这方面的
```R
library("TCGAbiolinks")
library('limma')
library('edgeR')
library('ggplot2')
library('ggpubr')
library('ggthemes')
library('pheatmap')

setwd('H:/my_python/ceRNA') #设置工作目录
rt=read.csv('mRNA_symbol.csv',header = T,check.names = F) #读取表达矩
rt=as.matrix(rt) #将dataframe转化为matrix
rownames(rt) = rt[,2] #获取基因名称
exp = rt[,4:ncol(rt)] #组成新的表达矩阵
barcode=colnames(exp) #获取所有样本的barcode
dataSmTP <- TCGAquery_SampleTypes(barcode = barcode,typesample = "TP") #获取癌症组织的barcode
dataSmNT <- TCGAquery_SampleTypes(barcode = barcode, typesample = "NT") #获取为正常组织的barcode
exp = exp[,c(dataSmNT,dataSmTP)] #将列表按照类型重新排列，为下一步分组做准备
dimnames=list(rownames(exp),colnames(exp))
data=matrix(as.numeric(as.matrix(exp)),nrow=nrow(exp),dimnames=dimnames)
data=avereps(data) #将相同名称的基因表达量合并取均值

group=c(rep("normal",3),rep("tumor",304)) #按照癌症和正常样品数目修改
design <- model.matrix(~group)
y <- DGEList(counts=data,group=group)# 创建DGEList类型变量
keep <- filterByExpr(y)
y <- y[keep,,keep.lib.size=FALSE] #将低表达基因过滤掉，从生物学角度，有生物学意义的基因的表达量必须高于某一个阈值。从统计学角度上， low count的数据不太可能有显著性差异，而且在多重试验矫正阶段还会拖后腿。keep.lib.size=FALSE表示重新计算文库大小。
y <- calcNormFactors(y)# 计算标准化因子
y <- estimateCommonDisp(y)# 计算离散度
y <- estimateTagwiseDisp(y)
et <- exactTest(y,pair = c("normal","tumor")) # 显著性检验
ordered_tags <- topTags(et, n=100000) # n=100000是为了输出所以基因

allDiff=ordered_tags$table
allDiff=allDiff[is.na(allDiff$FDR)==FALSE,]
newData=y$counts

# 保存差异分析结果
write.csv(allDiff,file="case_vs_control_mRNA_edgerOut.csv",quote=F)
etSig <- allDiff[which(allDiff$PValue < 0.05 & abs(allDiff$logFC) > 1),] # 差异基因筛选
etSig[which(etSig$logFC > 0), "up_down"] <- "Up" # 加入一列，up_down 体现上调信息
etSig[which(etSig$logFC < 0), "up_down"] <- "Down" # 加入一列，up_down 体现上下调信息
write.csv(etSig,file="case_vs_control_P0.05_FC1_mRNA_edgerOut.csv",quote = F)
write.csv(newData,file="mRNA_normalizeExp.csv",quote=F) #输出所有基因校正后的表达值
write.csv(newData[rownames(etSig),],file="mRNA_diffExp.csv",quote=F) #输出差异基因校正后的表达值

##newvolcano
allDiff$logP <- -log10(allDiff$FDR) #对矫正后的P值进行log10转换
allDiff <- cbind(symbol=rownames(allDiff),allDiff)
allDiff$Group = "not-signigicant" #增加group
allDiff$Group[which((allDiff$FDR < 0.05) & (allDiff$logFC > 2))]="up-regulated" #设置上调基因
allDiff$Group[which((allDiff$FDR < 0.05) & (allDiff$logFC < -2))]="down-regulated" #设置下调基因

allDiff$Label="" #增加label列，对后期要展示基因加标签
allDiff <- allDiff[order(allDiff$FDR),]
upgenes <- head(allDiff$symbol[which(allDiff$Group=='up-regulated')],10) #上调基因中FDR最小的10个
downgenes <- head(allDiff$symbol[which(allDiff$Group=='down-regulated')],10) #下调基因中FDR最小的10个
deg.top10.genes <- c(as.character(upgenes),as.character(downgenes)) #将前十上调基因和下调基因合并
allDiff$Label[match(deg.top10.genes,allDiff$symbol)] <- deg.top10.genes

ggscatter(allDiff,x="logFC", y="logP", color = "Group",palette = c('#2f5688','#BBBBBB','#CC0000'),size = 1,label = allDiff$Label,font.label = 8,repel = T,xlab = 'log2FoldChange',ylab = "-log10(Adjust P-value")+theme_base()
ggsave("mRNA_regulate.eps")
dev.off()

## heatmap
pheatmap(newData[rownames(etSig),], scale="row")
ggsave("mRNA_heatmap.eps")
dev.off()
```

## 6 ceRNA网络构建
### 构建思路（lncRNA-miRNA-mRNA）

1. 筛选差异表达的lncRNA（上个步骤中已经完成）
2. 靶定lncRNAs的miRNA预测。可以通过miRcode和starBase上找lncRNA潜在的MREs
3. miRNA靶定的mRNA预测。通过miRTarBase预测。

### 执行步骤
1. 提取miRcode数据空中miRNA靶定的lncRNA。
```bash
 for i in $(cut -d , -f 1 lncRNA_diffExp.csv );do grep $i mircode_highconsfamilies.txt >> lncRNA_mircode.tsv;done #差异表达lncRNA与miRNA的关系对找出来
```
*ps:mircode_highconsfamilies.txt是miRcode里面的数据，可以从miRcode官网下载。该方法运行较慢，要对后面的文件进行多次遍历，后期考虑更快的方法。*  
2. 差异lncRNA和差异miRNA的关系对（lncRNA-miRNA）
```bash
for i in $(awk -F ',' '{print $1}' miRNA_diffExp.csv);do grep -i ${i#*-} lncRNA_mircode.tsv >> lncRNA_miRNA.tsv;done #在差异表达的lnRNA与miRNA的关系对文件中中找出显著差异表达的关系对
```
*ps:不想动脑子的方法，时间复杂度高，为O(n\*n),有生之年或许考虑优化。*  
3. 将miRNA前体转换成成熟miRNA，TCGA中miRNA的表达矩阵中miRNA为前体
# Reference
《[ceRNA网络构建](https://cloud.tencent.com/developer/news/398064)》  
《[ceRNA network构建笔记](https://www.jianshu.com/p/b7e4830c0b01)》