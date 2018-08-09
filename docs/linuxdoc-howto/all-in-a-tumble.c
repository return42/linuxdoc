// this test some kernel-doc stuff

/* parse-SNIP: hello-world */
#include<stdio.h>
int main() {
  printf("Hello World\n");
  return 0;
}
/* parse-SNAP: */

/* parse-SNIP: user_function */
/**
 * user_function() - function that can only be called in user context
 * @a: some argument
 * @...: ellipsis operator
 *
 * This function makes no sense, it's only a kernel-doc demonstration.
 *
 * Example:
 * x = user_function(22);
 *
 * Return:
 * Returns first argument
 */
int
user_function(int a, ...)
{
  return a;
}
/* parse-SNAP: */


/* parse-SNIP: user_function */
/**
 * user_sum() - another function that can only be called in user context
 * @a: first argument
 * @b: second argument
 *
 * This function makes no sense, it's only a kernel-doc demonstration.
 *
 * Example:
 * x = user_sum(1, 2);
 *
 * Return:
 * Returns the sum of the @a and @b
 */
API_EXPORTED
int user_sum(int a, int b)
{
  return b;
}
/* parse-SNAP: */

/* parse-SNIP: internal_function */
/**
 * internal_function - the answer
 *
 * Context: !sanity()
 *
 * Return:
 * The answer to the ultimate question of life, the universe and everything.
 */
int internal_function()
{
  return 42;
}
/* parse-SNAP: */

/* parse-SNIP: test_SYSCALL */
/**
 *  sys_rt_sigprocmask - change the list of currently blocked signals
 *  @how: whether to add, remove, or set signals
 *  @nset: stores pending signals
 *  @oset: previous value of signal mask if non-null
 *  @sigsetsize: size of sigset_t type
 *
 * Return: 0
 */
SYSCALL_DEFINE4(rt_sigprocmask, int, how, sigset_t __user *, nset,
		sigset_t __user *, oset, size_t, sigsetsize)
{
  ...
  return 0;
}
/* parse-SNAP: rarely_code_styles*/
/**
* enum rarely_enum - enum to test parsing rarely code styles
* @F1: f1
* @F2: f2
*/
enum rarely_enum {
	F1,

	F2,
};


/**
* struct rarely_struct - struct to test parsing rarely code styles
* @foofoo: lorem
* @barbar: ipsum
*/

struct rarely_struct {
	struct foo

	foofoo;

	struct bar

	barbar;
};

/* parse-SNIP: xxxx */


