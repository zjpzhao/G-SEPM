/**
 * 2DConvolution.cu: This file is part of the PolyBench/GPU 1.0 test suite.
 *
 *
 * Contact: Scott Grauer-Gray <sgrauerg@gmail.com>
 * Louis-Noel Pouchet <pouchet@cse.ohio-state.edu>
 * Web address: http://www.cse.ohio-state.edu/~pouchet/software/polybench/GPU
 */

#include <unistd.h>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <cuda.h>

#include "../../common/polybenchUtilFuncts.h"

//define the error threshold for the results "not matching"
#define PERCENT_DIFF_ERROR_THRESHOLD 0.05

#define GPU_DEVICE 0

/* Problem size */

#define NI 128
#define NJ 128

/* Thread block dimensions */
#define DIM_THREAD_BLOCK_X 32
#define DIM_THREAD_BLOCK_Y 8

/*Define size of str*/
#define STR_SIZE 256

/* Can switch DATA_TYPE between float and double */
typedef float DATA_TYPE;



void conv2D(DATA_TYPE* A, DATA_TYPE* B)
{
	int i, j;
	DATA_TYPE c11, c12, c13, c21, c22, c23, c31, c32, c33;

	c11 = +0.2;  c21 = +0.5;  c31 = -0.8;
	c12 = -0.3;  c22 = +0.6;  c32 = -0.9;
	c13 = +0.4;  c23 = +0.7;  c33 = +0.10;


	for (i = 1; i < NI - 1; ++i) // 0
	{
		for (j = 1; j < NJ - 1; ++j) // 1
		{
			B[i*NJ + j] = c11 * A[(i - 1)*NJ + (j - 1)]  +  c12 * A[(i + 0)*NJ + (j - 1)]  +  c13 * A[(i + 1)*NJ + (j - 1)]
				+ c21 * A[(i - 1)*NJ + (j + 0)]  +  c22 * A[(i + 0)*NJ + (j + 0)]  +  c23 * A[(i + 1)*NJ + (j + 0)] 
				+ c31 * A[(i - 1)*NJ + (j + 1)]  +  c32 * A[(i + 0)*NJ + (j + 1)]  +  c33 * A[(i + 1)*NJ + (j + 1)];
		}
	}
}



void init(DATA_TYPE* A)
{
	int i, j;

	for (i = 0; i < NI; ++i)
    	{
		for (j = 0; j < NJ; ++j)
		{
			A[i*NJ + j] = (float)rand()/RAND_MAX;
        	}
    	}
}

/*
void init(DATA_TYPE* A)
{
	FILE *fp;

	fp = fopen("source.txt","r");
	if(!fp){
		printf("The file was not opened\n");
		return;
	}
	
	double val=0;
	fscanf(fp,"%lf",val);
	
	int i,j;
	for(i = 0 ; i < NI ; ++i )
	    for(j = 0 ; j < NJ ; ++j)
	     {
		fscanf(fp,"%lf",A[i*NJ + j]);
             }
	fclose(fp);
}
*/
//output the result of B from GPU
void printgpub(DATA_TYPE* B_outputFromGpu){
	FILE* fp;
	fp=fopen("out.txt","w");
	char str[STR_SIZE];

        if(!fp)
	{
		printf("Error writing!");
		return;
	}
	//sprintf(str,"%d",NI);
	//fputs(str,fp);
	int i,j;

	for (i = 0 ; i < NI ; ++i)
	{
		for (j = 0 ; j < NJ ; ++j)
		{
			sprintf(str,"%e\t",B_outputFromGpu[i*NJ + j]);
			fputs(str,fp);
		}
		sprintf(str,"\n");
		fputs(str,fp);
	}
	fclose(fp);
}

/*
void printcpub(DATA_TYPE* B){
        FILE* fp;
        fp=fopen("cpu.out","w");
        char str[STR_SIZE];

        if(!fp)
        {
                printf("Error writing!");
                return;
        }
        //sprintf(str,"%d",NI);
        //fputs(str,fp);
        int i,j;

        for (i = 0 ; i < NI ; ++i)
        {
                for (j = 0 ; j < NJ ; ++j)
                {
                        sprintf(str,"%f\t",B[i*NJ + j]);
                        fputs(str,fp);
                }
                sprintf(str,"\n");
                fputs(str,fp);
        }
	fclose(fp);
}


void printa(DATA_TYPE* A){
        FILE* fp;
        fp=fopen("A.out","w");
        char str[STR_SIZE];

        if(!fp)
        {
                printf("Error writing!");
                return;
        }
        //sprintf(str,"%d",NI);
        //fputs(str,fp);
        int i,j;

        for (i = 0 ; i < NI ; ++i)
        {
                for (j = 0 ; j < NJ ; ++j)
                {
                        sprintf(str,"%f\t",A[i*NJ + j]);
                        fputs(str,fp);
                }
                sprintf(str,"\n");
                fputs(str,fp);
        }
        fclose(fp);
}

*/
void compareResults(DATA_TYPE* B, DATA_TYPE* B_outputFromGpu)
{
	int i, j, fail;
	fail = 0;
	
	// Compare a and b
	for (i=1; i < (NI-1); i++) 
	{
		for (j=1; j < (NJ-1); j++) 
		{
			if (percentDiff(B[i*NJ + j], B_outputFromGpu[i*NJ + j]) > PERCENT_DIFF_ERROR_THRESHOLD) 
			{
				fail++;
			}
		}
	}
	
	// Print results
	printf("Non-Matching CPU-GPU Outputs Beyond Error Threshold of %4.2f Percent: %d\n", PERCENT_DIFF_ERROR_THRESHOLD, fail);
	
}


void GPU_argv_init()
{
	cudaDeviceProp deviceProp;
	cudaGetDeviceProperties(&deviceProp, GPU_DEVICE);
	printf("setting device %d with name %s\n",GPU_DEVICE,deviceProp.name);
	cudaSetDevice( GPU_DEVICE );
}


__global__ void Convolution2D_kernel(DATA_TYPE *A, DATA_TYPE *B)
{
	int j = blockIdx.x * blockDim.x + threadIdx.x;
	int i = blockIdx.y * blockDim.y + threadIdx.y;
    if(i==0 && j==0);
	DATA_TYPE c11, c12, c13, c21, c22, c23, c31, c32, c33;

	c11 = +0.2;  c21 = +0.5;  c31 = -0.8;
	c12 = -0.3;  c22 = +0.6;  c32 = -0.9;
	c13 = +0.4;  c23 = +0.7;  c33 = +0.10;

	if ((i < NI-1) && (j < NJ-1) && (i > 0) && (j > 0))
	{
		B[i * NJ + j] =  c11 * A[(i - 1) * NJ + (j - 1)]  + c21 * A[(i - 1) * NJ + (j + 0)] + c31 * A[(i - 1) * NJ + (j + 1)] 
			+ c12 * A[(i + 0) * NJ + (j - 1)]  + c22 * A[(i + 0) * NJ + (j + 0)] +  c32 * A[(i + 0) * NJ + (j + 1)]
			+ c13 * A[(i + 1) * NJ + (j - 1)]  + c23 * A[(i + 1) * NJ + (j + 0)] +  c33 * A[(i + 1) * NJ + (j + 1)];
	}
}


void convolution2DCuda(DATA_TYPE* A, DATA_TYPE* B, DATA_TYPE* B_outputFromGpu)
{
	double t_start, t_end;

	DATA_TYPE *A_gpu;
	DATA_TYPE *B_gpu;

	cudaMalloc((void **)&A_gpu, sizeof(DATA_TYPE) * NI * NJ);
	cudaMalloc((void **)&B_gpu, sizeof(DATA_TYPE) * NI * NJ);
	cudaMemcpy(A_gpu, A, sizeof(DATA_TYPE) * NI * NJ, cudaMemcpyHostToDevice);
	
	dim3 block(DIM_THREAD_BLOCK_X, DIM_THREAD_BLOCK_Y);
	dim3 grid((size_t)ceil( ((float)NI) / ((float)block.x) ), (size_t)ceil( ((float)NJ) / ((float)block.y)) );
	t_start = rtclock();
	Convolution2D_kernel<<<grid,block>>>(A_gpu,B_gpu);
	cudaThreadSynchronize();
	t_end = rtclock();
	fprintf(stdout, "GPU Runtime: %0.6lfs\n", t_end - t_start);//);

	cudaMemcpy(B_outputFromGpu, B_gpu, sizeof(DATA_TYPE) * NI * NJ, cudaMemcpyDeviceToHost);

//	printgpub(B_outputFromGpu);
	
	cudaFree(A_gpu);
	cudaFree(B_gpu);
}


int main(int argc, char *argv[])
{
//	double t_start, t_end;

	DATA_TYPE* A;
	DATA_TYPE* B;  
	DATA_TYPE* B_outputFromGpu;
	
	A = (DATA_TYPE*)malloc(NI*NJ*sizeof(DATA_TYPE));
	B = (DATA_TYPE*)malloc(NI*NJ*sizeof(DATA_TYPE));
	B_outputFromGpu = (DATA_TYPE*)malloc(NI*NJ*sizeof(DATA_TYPE));

	//initialize the arrays
	init(A);
	//printa(A);
	GPU_argv_init();

	convolution2DCuda(A, B, B_outputFromGpu);
 
	printgpub(B_outputFromGpu);
	
//	t_start = rtclock();
//	conv2D(A, B);
	//printcpub(B);
//	t_end = rtclock();
//	fprintf(stdout, "CPU Runtime: %0.6lfs\n", t_end - t_start);//);
	
//	compareResults(B, B_outputFromGpu);

	free(A);
	free(B);
	free(B_outputFromGpu);
	
	return 0;
}

