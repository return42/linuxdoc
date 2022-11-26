/* parse-SNIP: EXP_SYMB */
/**
 * foo() - function that can only be called in user context
 * @a: some argument
 * @...: ellipsis operator
 *
 * This function makes no sense, it's only a kernel-doc demonstration.
 *
 * Example:
 * x = foo(42);
 *
 * Return:
 * Returns first argument
 */
int foo(int a, ...)
{
	return a;
}
/* parse-SNAP: */

/* parse-SNIP: API_EXP */
/**
 * bar() - function that can only be called in user context
 * @a: some argument
 * @...: ellipsis operator
 *
 * This function makes no sense, it's only a kernel-doc demonstration.
 *
 * Example:
 * x = bar(42);
 *
 * Return:
 * Returns first argument
 */
API_EXP int bar(int a, ...)
{
	return a;
}

/* parse-SNIP: internal_function */
/**
 * internal_function() - the answer
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
