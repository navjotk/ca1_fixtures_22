#include<stdio.h>
#include<stdlib.h>
#define __USE_C99_MATH

#include <stdbool.h>

bool test_case1();
void op2(float*, int, int, int, float*, float*);

int main() {
    bool tc1 = test_case1();

    printf("Test case 1: %s\n", tc1?"T":"F");

    return !tc1;
}

bool test_case1() {
    int m = 3;
    int n = 3;
    int p = 3;

    float a_def[9] = {1,2,3,    4,5,6,    7,8,9};
    float b_def[9] = {2,3,4,   5,6,7,     8,9,10};
    float c_expected[9] = {36,42,48,    81,96,111,    126,150,174};

    float *a = malloc(sizeof(float) * m * n);
    float *b = malloc(sizeof(float) * n * p);
    float *c = malloc(sizeof(float) * m * p);

    for(int i=0;i<(m*n); i++) {
        a[i] = a_def[i];
    }

    for(int i=0;i<(n*p); i++) {
        b[i] = b_def[i];
    }

    for(int i=0;i<(m*p); i++) {
        c[i] = 0;
    }

    op2(a, m, n, p, b, c);

    bool match = true;

    for(int i=0;i<(m*p); i++) {
        if(c[i]!=c_expected[i]) {
            match = false;
            printf("At position %d, expected %f but found %f. \n", i, c_expected[i], c[i]);
            //break;
        }
    }
    free(a);
    free(b);
    free(c);
    return match;
}