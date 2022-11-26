/* parse-SNIP: EXP_SYMB */
EXP_SYMB(foo)

int foo(int a, ...)
/* parse-SNAP: */

/* parse-SNIP: API_EXP */
int bar(int a, int b);
/* parse-SNAP: */
