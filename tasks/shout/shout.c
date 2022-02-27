#include <stdio.h>
#include <stdlib.h>

void __attribute__((section(".flags"))) print_flag() {
    char flag[64];
    FILE* f = fopen("flag.txt", "r");
    fread(flag, 1, 63, f);
    puts(flag);
    fflush(stdout);
}

void shout() {
    char shout[1024];
    puts("Shout here: ");
    fflush(stdout);
    gets(shout);
    puts("Too weak, try again.");
    fflush(stdout);
}

int main() {
    shout();
    return 0;
}
