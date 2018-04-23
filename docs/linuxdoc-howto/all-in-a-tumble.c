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


/* parse-SNIP: user_sum-c */
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
	return a + b;
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
 *  sys_tgkill - send signal to one specific thread
 *  @tgid: the thread group ID of the thread
 *  @pid: the PID of the thread
 *  @sig: signal to be sent
 *
 *  This syscall also checks the @tgid and returns -ESRCH even if the PID
 *  exists but it's not belonging to the target process anymore. This
 *  method solves the problem of threads exiting and PIDs getting reused.
 */
SYSCALL_DEFINE3(tgkill, pid_t, tgid, pid_t, pid, int, sig)
{
	...
}

/* parse-SNAP: */

/* parse-SNIP: rarely_code_styles*/
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


/* parse-SNIP: user_function */
/**
 * user_function_1() - function that can only be called in user context
 * @a: some argument
 *
 * This function calls and returns user_function_2()
 * Since user_function_2() is mentionned in the description, it will
 * be part of the See Also section below the description.
 * This is true for all formats, but mostly useful for manpages
 *
 */
int
user_function_1(int a)
{
  return user_function_2(a);
}

/**
 * user_function_2() - function that can only be called in user context
 * @a: some argument
 *
 * This function makes no sense, it's only a kernel-doc demonstration.
 */
int
user_function_2(int a)
{
  return a;
}
/* parse-SNAP: */

