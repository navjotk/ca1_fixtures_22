#include<stdio.h>
#include<stdlib.h>
#define __USE_C99_MATH

#include <stdbool.h>

bool test_case1();
void op1(float*, int, int, float*, int, float*, int);

int main() {
    bool tc1 = test_case1();

    printf("Test case 1: %s\n", tc1?"T":"F");
    return !tc1;
}

bool test_case1() {
    int height = 5;
    int width = 5;
    int b = 1;
    int filter_size = 3;

    float input_def[25] = {7,2,3,3,8,   4,5,3,8,4,    3,3,2,8,4,    2,8,7,2,7,    5,4,4,5,4};
    float filter_def[9] = {1,0,-1,   1,0,-1,   1,0,-1};
    float expected_output[25] = {7,2,3,3,8,   4,6,-9,-8,4,    3,-3,-2,-3,4,    2,-3,0,-2,7,    5,4,4,5,4};

    float *input = malloc(sizeof(float) * b * height * width);
    float *filter = malloc(sizeof(float) * filter_size * filter_size);
    float *output = malloc(sizeof(float) * b * height * width);

    for(int i=0;i<(height*width); i++) {
        input[i] = input_def[i];
    }

    for(int i=0;i<(filter_size*filter_size); i++) {
        filter[i] = filter_def[i];
    }

    for(int i=0;i<(height*width); i++) {
        output[i] = 0;
    }

    op1(input, height, width, filter, filter_size, output, 1);

    bool match = true;

    for(int i=0;i<(height*width); i++) {
        if(output[i]!=expected_output[i]) {
            match = false;
            printf("At position %d, expected %f but found %f. \n", i, expected_output[i], output[i]);
            //break;
        }
    }
    free(input);
    free(filter);
    free(output);
    return match;
}