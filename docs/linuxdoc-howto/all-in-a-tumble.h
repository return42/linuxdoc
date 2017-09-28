/* parse-markup: reST */

/**
 * DOC: About Examples
 *
 * The file ``all-in-a-tumble.h`` includes all the referred examples of the
 * linuxdoc-HOWTO documentation. It is also used as a test of the kernel-doc
 * parser, to see how kernel-doc content will be rendered and where the parser
 * might fail.
 *
 * The content itself is nonsense / don’t look to close ;-)
 */

// testing:
//
// .. kernel-doc::  ./all-in-a-tumble.c
//     :export:  ./all-in-a-tumble.h

EXPORT_SYMBOL_GPL_FUTURE(user_function)

/**
 * block_touch_buffer - mark a buffer accessed
 * @bh: buffer_head being touched
 *
 * Called from touch_buffer().
 */
DEFINE_EVENT(block_buffer, block_touch_buffer,

	TP_PROTO(struct buffer_head *bh),

	TP_ARGS(bh)
);

/**
 * block_dirty_buffer - mark a buffer dirty
 * @bh: buffer_head being dirtied
 *
 * Called from mark_buffer_dirty().
 */
DEFINE_EVENT(block_buffer, block_dirty_buffer,

	TP_PROTO(struct buffer_head *bh),

	TP_ARGS(bh)
);

// The parse-SNIP/SNAP comments are used to include the C sorce code as snippets
// into a reST document. These are the examples of the kernel-doc-HOWTO book.

/* parse-SNIP: theory-of-operation */
/**
 * DOC: Theory of Operation
 *
 * The whizbang foobar is a dilly of a gizmo.  It can do whatever you
 * want it to do, at any time.  It reads your mind.  Here's how it works.
 *
 * foo bar splat
 * -------------
 *
 * The only drawback to this gizmo is that is can sometimes damage hardware,
 * software, or its subject(s).
 *
 * DOC: multiple DOC sections
 *
 * It's not recommended to place more than one "DOC:" section in the same
 * comment block. To insert a new "DOC:" section, create a new comment block and
 * to create a sub-section use the reST markup for headings, see documentation
 * of function rst_mode()
 */
/* parse-SNAP: */


/* parse-SNIP: my_struct */
/**
 * struct my_struct - a struct with nested unions and structs
 * @arg1: first argument of anonymous union/anonymous struct
 * @arg2: second argument of anonymous union/anonymous struct
 * @arg3: third argument of anonymous union/anonymous struct
 * @arg4: fourth argument of anonymous union/anonymous struct
 * @bar.st1.arg1: first argument of struct st1 on union bar
 * @bar.st1.arg2: second argument of struct st1 on union bar
 * @bar.st2.arg1: first argument of struct st2 on union bar
 * @bar.st2.arg2: second argument of struct st2 on union bar
 * @bar.st3.arg2: second argument of struct st3 on union bar
 */
struct my_struct {
    /* Anonymous union/struct*/
    union {
        struct {
            int arg1;
            int arg2;
        };
        struct {
            void *arg3;
            int arg4;
        };
    };
    union {
        struct {
            int arg1;
            int arg2;
        } st1;           /* bar.st1 is undocumented, cause a warning */
        struct {
            void *arg1;  /* bar.st3.arg1 is undocumented, cause a warning */
	    int arg2;
        } st2, st3;
    } bar;               /* bar is undocumented, cause a warning */

    /* private: */
    int undoc_privat;    /* is undocumented but private, no warning */

    /* public: */
    int undoc_public;    /* is undocumented, cause a warning */

};
/* parse-SNAP: */

/* parse-SNIP: my_long_struct */
/**
 * struct my_long_struct - short description with &my_struct->a and &my_struct->b
 * @foo: The Foo member.
 *
 * Longer description
 */
struct my_long_struct {
	int foo;
        /**
         * @bar: The Bar member.
         */
        int bar;
        /**
         * @baz: The Baz member.
         *
         * Here, the member description may contain several paragraphs.
         */
        int baz;
        /** @foobar: Single line description. */
        int foobar;
};
/* parse-SNAP: */


/* parse-SNIP: my_union */
/**
 * union my_union - short description
 * @a: first member
 * @b: second member
 *
 * Longer description
 */
union my_union {
    int a;
    int b;
};
/* parse-SNAP: */


/* parse-SNIP: my_enum */
/**
 * enum my_enum - log level
 * @QUIET: logs nothing
 * @INFO: logs info messages
 * @WARN: logs warn and info messages
 * @DEBUG: logs debug, warn and info messages
 */

enum my_enum {
  QUIET,
  INFO,
  WARN,
  DEBUG
};
/* parse-SNAP: */


/* parse-SNIP: my_typedef */
/**
 * typedef my_typedef - useless typdef of int
 *
 */
typedef int my_typedef;
/* parse-SNAP: */


/**
 * rst_mode - short description of this function
 * @a: first argument
 * @b: second argument
 * Context: :c:func:`in_gizmo_mode`.
 *
 * Long description. This function has two integer arguments. The first is
 * ``parameter_a`` and the second is ``parameter_b``.
 *
 * As long as the reST / sphinx-doc toolchain uses `intersphinx
 * <http://www.sphinx-doc.org/en/stable/ext/intersphinx.html>`__ you can refer
 * definitions *outside* like :c:type:`struct media_device <media_device>`.  If
 * the description of ``media_device`` struct is found in any of the intersphinx
 * locations, a hyperref to this target is generated a build time.
 *
 * Example:
 *   int main() {
 *     printf("Hello World\n");
 *     return 0;
 *   }
 *
 * Return: Sum of ``parameter_a`` and the second is ``parameter_b``.
 *
 * highlighting:
 * The highlight pattern, are non regular reST markups. They are only available
 * within kernel-doc comments, helping C developers to write short and compact
 * documentation.
 *
 * - user_function() : function
 * - @a : name of a parameter
 * - &struct my_struct : name of a structure (including the word struct)
 * - &union my_union : name of a union
 * - &my_struct->a or &my_struct.b -  member of a struct or union.
 * - &enum my_enum : name of a enum
 * - &typedef my_typedef : name of a typedef
 * - %CONST : name of a constant.
 * - $ENVVAR : environmental variable
 *
 * The kernel-doc parser translates the pattern above to the corresponding reST
 * markups. You don't have to use the *highlight* pattern, if you prefer *pure*
 * reST, use the reST markup.
 *
 * - :c:func:`user_function` : function
 * - ``a`` : name of a parameter
 * - :c:type:`struct my_struct <my_struct>` : name of a structure (including the word struct)
 * - :c:type:`union my_union <my_union>` : name of a union
 * - :c:type:`my_struct->a <my_struct>` or :c:type:`my_struct.b <my_struct>` -  member of a struct or union.
 * - :c:type:`enum my_enum <my_enum>` : name of a enum
 * - :c:type:`typedef my_typedef <my_typedef>` : name of a typedef
 * - ``CONST`` : name of a constant.
 * - ``\$ENVVAR`` : environmental variable
 *
 * Since the prefixes ``$...``, ``&...`` and ``@...`` are used to markup the
 * highlight pattern, you have to escape them in other uses: $lorem, \&lorem,
 * \%lorem and \@lorem. To esacpe from function highlighting, use lorem\().
 *
 * Parser Mode:
 * This is an example with activated reST additions, in this section you will
 * find some common inline markups.
 *
 * Within the *reST mode* the kernel-doc parser pass through all markups to the
 * reST toolchain, except the *vintage highlighting* but including any
 * whitespace. With this, the full reST markup is available in the comments.
 *
 * This is a link to the `Linux kernel source tree
 * <https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/>`_.
 *
 * This description is only to show some reST inline markups like *emphasise*
 * and **emphasis strong**. The following is a demo of a reST list markup:
 *
 * Definition list:
 * :def1: lorem
 * :def2: ipsum
 *
 * Ordered List:
 * - item one
 * - item two
 * - item three with
 *   a linebreak
 *
 * Literal blocks:
 * The next example shows a literal block::
 *
 *     +------+          +------+
 *     |\     |\        /|     /|
 *     | +----+-+      +-+----+ |
 *     | |    | |      | |    | |
 *     +-+----+ |      | +----+-+
 *      \|     \|      |/     |/
 *       +------+      +------+
 *
 * Highlighted code blocks:
 * The next example shows a code block, with highlighting C syntax in the
 * output.
 *
 * .. code-block:: c
 *
 *     // Hello World program
 *     #include<stdio.h>
 *     int main\()
 *     {
 *        printf("Hello World");
 *     }
 *
 *
 * reST sectioning:
 *
 * colon markup: sectioning by colon markup in reST mode is less ugly. ;-)
 *
 * A kernel-doc section like *this* section is translated into a reST
 * *subsection*. This means, you can only use the following *sub-levels* within a
 * kernel-doc section.
 *
 * a subsubsection
 * ^^^^^^^^^^^^^^^
 *
 * lorem ipsum
 *
 * a paragraph
 * """""""""""
 *
 * lorem ipsum
 *
 */

int rst_mode(int a, char *b)
{
  return a + b;
}


/* parse-markup: kernel-doc */

/**
 * vintage - short description of this function
 * @parameter_a: first argument
 * @parameter_b: second argument
 * Context: in_gizmo_mode().
 *
 * This is a test of a typical markup from *vintage* kernel-doc.  Don't look to
 * close here, it is only for testing some kernel-doc parser stuff.
 *
 * Long description. This function has two integer arguments. The first is
 * @parameter_a and the second is @parameter_b.
 *
 * Example: user_function(22);
 *
 * Return: Sum of @parameter_a and @parameter_b.
 *
 * highlighting:
 *
 * - vintage()    : function
 * - @parameter_a : name of a parameter
 * - $ENVVAR      : environmental variable
 * - &my_struct   : name of a structure (up to two words including ``struct``)
 * - %CONST       : name of a constant.
 *
 * Parser Mode: *vintage* kernel-doc mode
 *
 * Within the *vintage kernel-doc mode* ignores any whitespace or inline
 * markup.
 *
 * - Inline markup like *emphasis* or **emphasis strong**
 * - Literals and/or block indent:
 *
 *      a + b
 *
 * In kernel-doc *vintage* mode, there are no special block or inline markups
 * available. Markups like the one above result in ambiguous reST markup which
 * could produce error messages in the subsequently sphinx-build
 * process. Unexpected outputs are mostly the result.
 *
 * This is a link https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/
 * to the Linux kernel source tree
 *
 * colon markup: sectioning by colon markup in vintage mode is partial ugly. ;-)
 *
 */
int vintage(int parameter_a, char parameter_b)
{
  return a + b;
}

/* some C&P for extended tests
 */

/**
* struct nfp_flower_priv - Flower APP per-vNIC priv data
* @nn:                Pointer to vNIC
* @mask_id_seed:      Seed used for mask hash table
* @flower_version:    HW version of flower
* @mask_ids:          List of free mask ids
* @mask_table:        Hash table used to store masks
* @flow_table:        Hash table used to store flower rules
*/
struct nfp_flower_priv {
      struct nfp_net *nn;
      u32 mask_id_seed;
      u64 flower_version;
      struct nfp_fl_mask_id mask_ids;
      DECLARE_HASHTABLE(mask_table, NFP_FLOWER_MASK_HASH_BITS);
      DECLARE_HASHTABLE(flow_table, NFP_FLOWER_HASH_BITS);
};

/**
 * enum foo - foo
 * @F1: f1
 * @F2: f2
 */
enum foo {
	F1,

	F2,
};


/**
* struct something - Lorem ipsum dolor sit amet.
* @foofoo: lorem
* @barbar: ipsum
*/

struct something {
	struct foo

	foofoo;

	struct bar

	barbar;
};

