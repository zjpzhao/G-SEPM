/**
 * 2mm.cu: This file is part of the PolyBench/GPU 1.0 test suite.
 *
 *
 * Contact: Scott Grauer-Gray <sgrauerg@gmail.com>
 * Louis-Noel Pouchet <pouchet@cse.ohio-state.edu>
 * Web address: http://www.cse.ohio-state.edu/~pouchet/software/polybench/GPU
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include <unistd.h>
#include <sys/time.h>
#include <cuda.h>

#include "../../common/polybenchUtilFuncts.h"

//define the error threshold for the results "not matching"
#define PERCENT_DIFF_ERROR_THRESHOLD 0.05

#define GPU_DEVICE 0

/* Problem size. */

# define NI 256
# define NJ 256
# define NK 256
# define NL 256

/* Thread block dimensions */
#define DIM_THREAD_BLOCK_X 32
#define DIM_THREAD_BLOCK_Y 8

#define STR_SIZE 256

/* Can switch DATA_TYPE between float and double */

typedef float DATA_TYPE;
typedef double DT;

void init_array(DATA_TYPE* A, DATA_TYPE* B, DATA_TYPE* C, DATA_TYPE* D)
{
	int i, j;
    //四个数组：从A[0]到A[NI*NK]循环赋值
    //A[i][k];B[k][j];C[l][j];D[i][l]
    //C=A*B,E=C*D，最终得到一个方阵
	for (i = 0; i < NI; i++)
	{
		for (j = 0; j < NK; j++)
		{
			A[i*NI + j] = ((DATA_TYPE) i*j) / NI;
		}
	}

	for (i = 0; i < NK; i++)
	{
		for (j = 0; j < NJ; j++)
		{
			B[i*NK + j] = ((DATA_TYPE) i*(j+1)) / NJ;
		}
	}

    for (i = 0; i < NL; i++)
	{
		for (j = 0; j < NJ; j++)
		{
			C[i*NL + j] = ((DATA_TYPE) i*(j+3)) / NL;
		}
	}

    for (i = 0; i < NI; i++)
	{
		for (j = 0; j < NL; j++)
		{
			D[i*NL + j] = ((DATA_TYPE) i*(j+2)) / NK;
		}
	}

}






//读取out.txt文件
void print(DATA_TYPE* E_outputFromGpu){
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
    //i++与++i计算次数是没有区别的
	for (i = 0 ; i < NL ; ++i)
	{
		for (j = 0 ; j < NI ; ++j)
		{
            //sprintf函数，前两个参数固定，第一个是字符数组名，第二个是格式化
            //fputs写字符串：将字符串写入指定文件
			sprintf(str,"%f\t",E_outputFromGpu[i*NI + j]);
			fputs(str,fp);
		}
		sprintf(str,"\n");
		fputs(str,fp);
	}
	fclose(fp);
}

//对比结果
void compareResults(DATA_TYPE *E, DATA_TYPE *E_outputFromGpu)
{
	int i,j,fail;
	fail = 0;

	for (i=0; i < NL; i++)
	{
		for (j=0; j < NI; j++)
		{
			if (percentDiff(E[i*NI + j], E_outputFromGpu[i*NI + j]) > PERCENT_DIFF_ERROR_THRESHOLD)
			{
				fail++;
			}
		}
	}

	// print results
	printf("Non-Matching CPU-GPU Outputs Beyond Error Threshold of %4.2f Percent: %d\n", PERCENT_DIFF_ERROR_THRESHOLD, fail);
}

//GPU initial
void GPU_argv_init()
{
	cudaDeviceProp deviceProp;
	cudaGetDeviceProperties(&deviceProp, GPU_DEVICE);
	printf("setting device %d with name %s\n",GPU_DEVICE,deviceProp.name);
	cudaSetDevice( GPU_DEVICE );
}

//两个kernel函数
__global__ void mm2_kernel1(DATA_TYPE *A, DATA_TYPE *B, DATA_TYPE *C, DT *f)
{
    //分配线程号:blockDim.x是一个threadBlock中含有thread的个数，blockIdx.x是当前是第几个threadBlock
    //threadInx.x表示当前thread在该threadblock内的index
	int j = blockIdx.x * blockDim.x + threadIdx.x;
	int i = blockIdx.y * blockDim.y + threadIdx.y;

	if ((i < NI) && (j < NJ))
	{
		int k;
		for (k = 0; k < NK; k++)
		{
			C[i * NJ + j] += A[i * NK + k] * B[k * NJ + j];
		}
	}

}


__global__ void mm2_kernel2(DATA_TYPE *C, DATA_TYPE *D, DATA_TYPE *E, DT *f)
{
	int j = blockIdx.x * blockDim.x + threadIdx.x;
	int i = blockIdx.y * blockDim.y + threadIdx.y;

	if ((i < NI) && (j < NL))
	{
		int k;
		for (k = 0; k < NJ; k++)
		{
			E[i * NL + j] += C[i * NJ + k] * D[k * NL + j];
		}
	}
}


void mm2_cpu(DATA_TYPE* A, DATA_TYPE* B, DATA_TYPE* C, DATA_TYPE* D, DATA_TYPE* E)
{
	int i, j, k;

  	for (i = 0; i < NI; i++)
	{
		for (j = 0; j < NJ; j++)
		{
			C[i*NJ + j] = 0.0;
			for (k = 0; k < NK; ++k)
			{
				C[i*NJ + j] += A[i*NK + k] * B[k*NJ + j];
			}
		}
	}

	for (i = 0; i < NI; i++)
	{
		for (j = 0; j < NL; j++)
		{
			E[i*NL + j] = 0.0;
			for (k = 0; k < NJ; ++k)
			{
				E[i*NL + j] += C[i*NJ + k] * D[k*NL + j];
			}
		}
	}
}


void mm2Cuda(DATA_TYPE* A, DATA_TYPE* B, DATA_TYPE* C, DATA_TYPE* D, DATA_TYPE* E, DATA_TYPE* E_outputFromGpu, DT* f)
{
	double t_start, t_end;

	DATA_TYPE *A_gpu;
	DATA_TYPE *B_gpu;
	DATA_TYPE *C_gpu;
	DATA_TYPE *D_gpu;
	DATA_TYPE *E_gpu;
	DT *F_gpu;



	cudaMalloc((void **)&A_gpu, sizeof(DATA_TYPE) * NI * NK);
	cudaMalloc((void **)&B_gpu, sizeof(DATA_TYPE) * NK * NJ);
	cudaMalloc((void **)&C_gpu, sizeof(DATA_TYPE) * NI * NJ);
	cudaMalloc((void **)&D_gpu, sizeof(DATA_TYPE) * NJ * NL);
	cudaMalloc((void **)&E_gpu, sizeof(DATA_TYPE) * NI * NL);
    cudaMalloc((void **)&F_gpu, sizeof(DT) *2);


	cudaMemcpy(A_gpu, A, sizeof(DATA_TYPE) * NI * NK, cudaMemcpyHostToDevice);
	cudaMemcpy(B_gpu, B, sizeof(DATA_TYPE) * NK * NJ, cudaMemcpyHostToDevice);
	cudaMemcpy(C_gpu, C, sizeof(DATA_TYPE) * NK * NJ, cudaMemcpyHostToDevice);
	cudaMemcpy(D_gpu, D, sizeof(DATA_TYPE) * NJ * NL, cudaMemcpyHostToDevice);
	cudaMemcpy(E_gpu, E, sizeof(DATA_TYPE) * NI * NL, cudaMemcpyHostToDevice);
	cudaMemcpy(F_gpu, f, sizeof(DT) *2, cudaMemcpyHostToDevice);



	//dim3 block(32,8)：也就是说32*8个thread
	dim3 block(DIM_THREAD_BLOCK_X, DIM_THREAD_BLOCK_Y);
	//dim3 grid1(512/32=16,512/8=64)

	dim3 grid1((size_t)ceil( ((float)NJ) / ((float)block.x) ), (size_t)ceil( ((float)NI) / ((float)block.y)) );
	dim3 grid2((size_t)ceil( ((float)NL) / ((float)block.x) ), (size_t)ceil( ((float)NI) / ((float)block.y)) );
	t_start = rtclock();
	//这是调用mm2_kernel1函数
	mm2_kernel1<<<grid1,block>>>(A_gpu, B_gpu, C_gpu, F_gpu);
	cudaDeviceSynchronize();

	mm2_kernel2<<<grid2,block>>>(C_gpu, D_gpu, E_gpu, F_gpu);
	cudaDeviceSynchronize();

	t_end = rtclock();
	fprintf(stdout, "GPU Runtime: %0.6lfs\n", t_end - t_start);

	cudaMemcpy(E_outputFromGpu, E_gpu, sizeof(DATA_TYPE) * NI * NL, cudaMemcpyDeviceToHost);

    cudaMemcpy(f, F_gpu, sizeof(DT) *2, cudaMemcpyDeviceToHost);

	cudaFree(A_gpu);
	cudaFree(B_gpu);
	cudaFree(C_gpu);
	cudaFree(D_gpu);
	cudaFree(E_gpu);
}


int main(int argc, char** argv)
{
	double t_start, t_end;

	DATA_TYPE* C;
	DATA_TYPE* A;
	DATA_TYPE* B;
	DATA_TYPE* D;
	DATA_TYPE* E;
	DATA_TYPE* E_outputFromGpu;




	C = (DATA_TYPE*)malloc(NI*NJ*sizeof(DATA_TYPE));
	A = (DATA_TYPE*)malloc(NI*NK*sizeof(DATA_TYPE));
	B = (DATA_TYPE*)malloc(NK*NJ*sizeof(DATA_TYPE));
	D = (DATA_TYPE*)malloc(NJ*NL*sizeof(DATA_TYPE));
	E = (DATA_TYPE*)malloc(NI*NL*sizeof(DATA_TYPE));
	E_outputFromGpu = (DATA_TYPE*)malloc(NI*NL*sizeof(DATA_TYPE));

	DT* f;
    f = (DT*)malloc(2*sizeof(DT));


  	init_array(A, B, C, D);

	GPU_argv_init();

	mm2Cuda(A, B, C, D, E, E_outputFromGpu, f);

	print(E_outputFromGpu);
	printf("%x %x\n",*(int *)&(f[0]),*(int *)&(f[1]));

	//printf("%f %f\n",f[0],f[1]);
	t_start = rtclock();
	mm2_cpu(A, B, C, D, E);
	t_end = rtclock();
	fprintf(stdout, "CPU Runtime: %0.6lfs\n", t_end - t_start);
	compareResults(E, E_outputFromGpu);

	free(C);
	free(A);
	free(B);
	free(D);
	free(E);
	free(E_outputFromGpu);

  	return 0;
}
