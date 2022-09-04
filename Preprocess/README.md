# Preprocessing

This folder contains preprocessing operations. First we sieve useful flags, then apply PCA on raw feature obtained from `Feature_Extraction`, and cluster PCA results.

## 1. Flag Sieve

**Sieve useful flags.** Flags in `data/Flag_Candidates` are tested on each IR in `data/IR_Candidates` by applying flag and profiling memory usage. 32 flags are found to reduce memory usage.

* `Flag_Seive.sh`: Wrapper shell script
  * `Flag_Seive_Core.sh`: Core shell script
  * `Result_to_Csv.py`: Save result to csv file `data/Flag_Profile.csv`
  * `Flag_ZTest.py`: Z-test is used to test whether flag has effect of memory usage
* `data/Flag_Profile.csv`: Memory usage for each ir code (`data/IR_Candidates.in`) applying each flags (`data/Flag_Candidates.in`) 
  * `data/IR_Candidates.in`: IR files used for sieving flags
  * `data/Flag_Candidates.in`: Flag used as candidates for sieving flags
* `Valid_IR.txt`: IR files that have difference in memory usage when applying any flag
* `Valid_Flags.txt`: Flag lists that are used as RL actions

## 2. PCA

**Apply PCA on features.** PCA is used to reduce dimension of the raw feature. PCA model is trained using `../Feature_Extraction/feature/` files. Trained model is saved to `data/pca_train.pkl`. 

* `Feature_PCA_Train.py`: Train PCA model and save and save into files in `pca_result/`
* `data/pca_train.pkl`: Trained PCA model
  * `data/str_scalar.pkl`: Mean and stdev used when training PCA is saved
* `pca_result/`: Raw feature applied PCA is saved
* `Feature_PCA_Result.txt`: Number of PCA components (this info is used in RL)

## 3. Clustering

**Cluster PCA results to improve RL performance.** PCA results are clustered using KMeans. Cluster number is determined by *Elbow Method*.

* `Cluster_IR.py`: Cluster PCA results and save KMeans model and save into folders in `cluster_pca_result/`
* `cluster_pca_result/cluster_CLUSTERIDX`: PCA feature result is grouped into clusters

## 4. Results

* PCA components were 15 (PCA model sotred in `./data/pca_train.pkl`)

* Clustering number was determined as 4 by Elbow method

  * Clustered IR code result

    ```
    # Cluster ( 0 ) element:  37
    # Cluster ( 1 ) element:  76
    # Cluster ( 2 ) element:  59
    # Cluster ( 3 ) element:  47
    ```

## 5. Etc

* `Massif_Parser.py`: Parser for parsing massif.out files
  * `msparser/`: Library code for massif parsing
* `old`: Files used as prototype
* `ir`, `bin`: Temporary folder used in scripts

## 5. Appendix

Csmith with 200 code of > 300kB code size, 100 codes of 500kB code size were used for memory usage testing. Following are flags that have effect on memory usage. (The floating number is the p-value from the Z-test)

```
-adce 0.999383655544035 21
-always-inline 0.9999439682843305 4
-argpromotion 0.998094947474157 32
-constmerge 0.9999439682843305 4
-dce 0.999383655544035 21
-deadargelim 0.9994957219135052 6
-dse 0.999383655544035 21
-globaldce 0.9999439682843305 4
-globalopt 0.9741680710658474 106
-gvn 0.999383655544035 21
-instcombine 0.9999439682843305 4
-aggressive-instcombine 0.9995517591177366 48
-ipsccp 0.9142565938414166 201
-lcssa 0.999383655544035 21
-licm 0.999383655544035 21
-loop-deletion 0.9999439682843305 4
-loop-extract 0.9999439682843305 4
-loop-reduce 0.9999439682843305 4
-loop-rotate 0.9999439682843305 4
-loop-simplify 0.9999439682843305 4
-loop-unroll 0.9999439682843305 4
-loweratomic 0.9999439682843305 4
-lowerinvoke 0.9999439682843305 4
-lowerswitch 0.9999439682843305 4
-memcpyopt 0.9999439682843305 4
-mergefunc 0.9999439682843305 4
-mergereturn 0.9999439682843305 4
-reassociate 0.9999439682843305 4
-sroa 0.999383655544035 21
-sccp 0.999383655544035 21
-simplifycfg 0.9999439682843305 4
-sink 0.999383655544035 21
-strip 0.999383655544035 21
-tailcallelim 0.9999439682843305 4
```

