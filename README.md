# G-SEPM
![](https://zenodo.org/badge/356287152.svg)  
We run G-SEPM on Tesla P40 platforms.   
The GPU driver is 418.87.00.  
The NVIDIA Toolkit is CUDA 8.0.61  
The operating system is Ubuntu 16.04.7.  
  
Our experiment follows the steps:  
(1)  The host and kernel codes are compiled by NVCC(NVIDIA CUDA Compiler) with -03, -arch=sm\_20.  
(2) We carry out fault injection campaigns on 17 CUDA applications from the Polybench and Ronidia benchmark suite.  For each test program, we run inject.sh to randomly inject 1000 bit-flip errors at the PTX level.   
(3)  All the heuristic proposed features are collected by running ins_fea.py.  
(4)  Based on the collected dataset, we utilize SVM, AdaBoost, Decision tree, and Random forest for training.  
