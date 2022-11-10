#include<stdio.h>
#include<stdlib.h>
#define __USE_C99_MATH
#include<string.h>
#include <stdbool.h>
#include<math.h>

void op1(float*, int, int, float*, int, float*, int);

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
        printf("Usage: %s <filename_input> <filename_kernel> <filename_expected_output>\n", argv[0]);
        return -1;
    }
    
    // Setting to 0 will write the expected output to the file specified as the third parameter. 
    // Setting to 1 will read the expected output from the file and compare with the given program. 
    int compareOutput = 1;

    bool match = true;

    char input_filename[500];
    char kernel_filename[500];
    char output_filename[500];

    strcpy(input_filename, argv[1]);
    strcpy(kernel_filename, argv[2]);
    strcpy(output_filename, argv[3]);

    int *input_dims_original = read_dims(input_filename);
    
    if(input_dims_original == NULL) {
        return -1;
    }

    int input_num_dims = input_dims_original[0];
    int *input_dims = input_dims_original+1;
    float *input_data = read_array(input_filename, input_dims, input_num_dims);
    if(input_data == NULL) {
        return -1;
    }
    
    int *kernel_dims_original = read_dims(kernel_filename);
    if(kernel_dims_original == NULL) {
        return -1;
    }
    int kernel_num_dims = kernel_dims_original[0];
    int *kernel_dims = kernel_dims_original+1;
    float *kernel_data = read_array(kernel_filename, kernel_dims, kernel_num_dims);
    if(kernel_data == NULL) {
        return -1;
    }

    long int total_input_size = product(input_dims, input_num_dims);
    
    float *output = malloc(sizeof(float) * total_input_size);

    op1(input_data, input_dims[1], input_dims[2], kernel_data, kernel_dims[0], output, input_dims[0]);

    if(compareOutput) {
        int *output_dims_original = read_dims(output_filename);
        if(output_dims_original == NULL) {
            return -1;
        }
        int output_num_dims = output_dims_original[0];
        int *output_dims = output_dims_original+1;
        float *expected_output = read_array(output_filename, output_dims, output_num_dims);

        if(expected_output == NULL) {
            return -1;
        }

        for(int i=0;i<total_input_size; i++) {
            if(fabs(output[i]-expected_output[i])>0.000001) {
                match = false;
                printf("At position %d, expected %f but found %f. \n", i, expected_output[i], output[i]);
                break;
            }
        }

        free(output_dims_original);
        free(expected_output);
    } else {
        FILE *file = fopen(output_filename,"w");

        if(file == NULL) {
            printf("Unable to open file: %s", output_filename);
            return -1;
        }

        if (file != NULL) {
            for(int i=0; i<input_num_dims; i++) {
                fprintf(file, "%d ", input_dims[i]);
            }
            fprintf(file, "\n");
        }

        for(int i=0; i<total_input_size; i++) {
            fprintf(file, "%.6f ", output[i]);
        }

        fclose(file);
    }
    

    free(input_data);
    free(input_dims_original);
    free(kernel_data);
    free(kernel_dims_original);
    free(output);

    return !match;
}