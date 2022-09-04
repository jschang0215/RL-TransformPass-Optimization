# Feature Extraction

This folder contains code extraction operations. First we generate random c code using csmith, then extract feature.

## 1. Random Program Generator

**[Csmith](https://github.com/csmith-project/csmith) is used for random C code generator.** Csmith is in `../csmith`. We also tested with [yarpgen](https://github.com/intel/yarpgen) but it did not have effect on memory usage when applying flags. Code with code size > 500kB is used. Generated code is tested whether it terminates in 10 seconds.

* `src/`: C code generated using csmtih
* `bin/`: Binary file compiled with `-O0` option
* `ir/`: IR file of the generated c code

## 2. Feature Extractor

**We developed a LLVM pass to extract code feature in IR level.** The LLVM pass is applied to each source code by `opt` option. The extracted feature is saved in `feature/`.

* `run.sh` : Wrapper shell script for obtaining features
  * `feature_extract_core.sh`: Core shell script
  * `Erase_Printf.py`: `printf()` function is erased in all source code
* `Feature.cpp/.h`: LLVM pass code that extract feature. Used by applying in `opt`option
  * `build_pass.sh`: Build LLVM pass code
  * `build/`: `.so` file of the feature extractor (this is used outside of this folder)
* `feature/`: Extracted feature for each original source code

## Etc

* `etc/`: Used for script configuration
* `old/`: Prototypes that are not used
* `Microbench_Paths.txt`: Microbench file paths. We did not use [microbench](https://github.com/VerticalResearchGroup/microbench) since it did not have difference in memory usage when applying any flags
* `src_backup.zip`: Back up of the original source code (Generating the source codes was difficult!)