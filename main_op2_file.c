#include<stdio.h>
#include<stdlib.h>
#define __USE_C99_MATH
#include<string.h>
#include <stdbool.h>
#include<math.h>

void op2(float*, int, int, int, float*, float*);

long int product(int *array, int n) {
    long int product = 1;
    for(int i=0; i<n; i++) {
        product *= array[i];
    }
    return product;
}

int *read_dims(char *filename) {
    FILE *file = fopen(filename,"r");
    
    if(file == NULL) {
        printf("Unable to open file: %s", filename);
        return NULL;
    }

    char firstline[500];
    fgets(firstline, 500, file);
    
    int line_length = strlen(firstline);

    int num_dims = 0;
    for(int i=0; i<line_length; i++) {
        if(firstline[i] == ' ') {
            num_dims++;
        }
    }
    
    int *dims = malloc((num_dims+1)*sizeof(int));
    dims[0] = num_dims;
    const char s[2] = " ";
    char *token;
    token = strtok(firstline, s);
    int i = 0;
    while( token != NULL ) {
        dims[i+1] = atoi(token);
        i++;
        token = strtok(NULL, s);
    }
    fclose(file);
    return dims;
}

float * read_array(char *filename, int *dims, int num_dims) {
    FILE *file = fopen(filename,"r");

    if(file == NULL) {
        printf("Unable to open file: %s", filename);
        return NULL;
    }

    char firstline[500];
    fgets(firstline, 500, file);

    //Ignore first line and move on since first line contains 
    //header information and we already have that. 

    long int total_elements = product(dims, num_dims);

    float *one_d = malloc(sizeof(float) * total_elements);

    for(int i=0; i<total_elements; i++) {
        fscanf(file, "%f", &one_d[i]);
    }
    fclose(file);
    return one_d;
}

int main(int argc, char *argv[]) {
    if(argc != 4) {
        printf("Usage: %s <filename_a> <filename_b> <filename_c>\n", argv[0]);
        return -1;
    }

    // Setting to 0 will write the expected output to the file specified as the third parameter. 
    // Setting to 1 will read the expected output from the file and compare with the given program. 
    int compareOutput = 1;

    bool match = true;

    char a_filename[500];
    char b_filename[500];
    char c_filename[500];

    strcpy(a_filename, argv[1]);
    strcpy(b_filename, argv[2]);
    strcpy(c_filename, argv[3]);
    int *a_dims_original = read_dims(a_filename);
    
    if(a_dims_original == NULL) {
        return -1;
    }

    int a_num_dims = a_dims_original[0];
    int *a_dims = a_dims_original+1;
    float *a_data = read_array(a_filename, a_dims, a_num_dims);
    if(a_data == NULL) {
        return -1;
    }
    
    int *b_dims_original = read_dims(b_filename);
    if(b_dims_original == NULL) {
        return -1;
    }
    int b_num_dims = b_dims_original[0];
    int *b_dims = b_dims_original+1;
    float *b_data = read_array(b_filename, b_dims, b_num_dims);
    if(b_data == NULL) {
        return -1;
    }
    long m = a_dims[0];
    long n = a_dims[1];

    long p = b_dims[1];

    long int output_size = a_dims[0] * b_dims[1];
    
    float *c = malloc(sizeof(float) * output_size);

    op2(a_data, m, n, p, b_data, c);
    

    if(compareOutput) {
        int *c_dims_original = read_dims(c_filename);
        if(c_dims_original == NULL) {
            return -1;
        }
        int c_num_dims = c_dims_original[0];
        int *c_dims = c_dims_original+1;
        float *expected_output = read_array(c_filename, c_dims, c_num_dims);

        if(expected_output == NULL) {
            return -1;
        }

        #ifdef _OPENMP
        #pragma omp parallel for reduction(&&:match) default(shared)
        #endif
        for(int i=0;i<output_size; i++) {
            if((fabs(c[i]-expected_output[i])/c[i])>0.01) {
                match = false;
                printf("At position %d, expected %f but found %f. \n", i, expected_output[i], c[i]);
                #ifndef _OPENMP
                break;
                #endif
            }
        }

        free(c_dims_original);
        free(expected_output);
    } else {
        FILE *file = fopen(c_filename,"w");

        if(file == NULL) {
            printf("Unable to open file: %s", c_filename);
            return -1;
        }

        fprintf(file, "%d %d \n", m, p);
        
        for(int i=0; i<output_size; i++) {
            fprintf(file, "%.6f ", c[i]);
        }

        fclose(file);
    }
    

    free(a_data);
    free(a_dims_original);
    free(b_data);
    free(b_dims_original);
    free(c);

    return !match;
}