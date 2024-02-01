from textwrap import indent


def remove_comments(s):
    """
    Given a string `s` that represents the contents of a Python source file,
    return it stripped from comments.
    """
    s = s.strip()
    lines_nocomments = []
    lines = s.splitlines()
    for line in lines:
        pos = line.find("#")
        if pos == 0:
            # The entire line is a comment
            continue
        if pos >= 0:
            # The line is partially a comment
            line = line[:pos]
        lines_nocomments.append(line)

    return "\n".join(lines_nocomments) + "\n"


def define_env(env):
    @env.macro
    def include_code(
        pathname, title="", lang="py", linesnum=True, hl_lines=None, ln_src=None, ln_out=None, drop_comments=True
    ):
        """
        Include a Python source file, specifying how to render it, what to highlight, and if to retain comments.
        """

        if hl_lines:
            hl_lines = f'hl_lines="{hl_lines}"'
        else:
            hl_lines = ""

        if linesnum:
            linesnum = 'linenums="1"'
        else:
            linesnum = ""

        code_src_lines = open(f"{pathname}.src").readlines()
        code_out_lines = open(f"{pathname}.out").readlines()

        # ln_src: Limit code to lines between m and n, given a format string "m-n"
        # ln_out: Same as ln_src but for he output
        if ln_src:
            ln_src = [int(v) for v in ln_src.split("-")]
            assert len(ln_src) == 2
        else:
            ln_src = [1, len(code_src_lines)]
        if ln_out:
            ln_out = [int(v) for v in ln_out.split("-")]
            assert len(ln_out) == 2
        else:
            ln_out = [1, len(code_out_lines)]

        # Assemble code multi-line string
        code_src = "".join(code_src_lines[ln_src[0] - 1 : ln_src[1]])
        if drop_comments:
            code_src = remove_comments(code_src)
        # Assemble output multi-line string
        code_out = "".join(code_out_lines[ln_out[0] - 1 : ln_out[1]])

        code_block = f'```{lang} {linesnum} {hl_lines}\n{code_src}\n```\n```{lang} title="Output"\n{code_out}\n```\n'

        # To add line numbers to the output block, add the string 'linenums="1"'.

        indented_code_block = indent(code_block, " " * 4)

        return f'!!! Example "{title}"\n{indented_code_block}'

    @env.macro
    def include_mk(pathname, path_prefix=".", snippet="snippet"):
        """
        Include part of another file.
        """

        data = open(f"{pathname}").read()
        pos_begin = data.find(f"<!-- {snippet}:begin -->")
        pos_end = data.find(f"<!-- {snippet}:end -->")
        assert pos_begin != -1
        assert pos_end != -1
        data = data[pos_begin:pos_end]

        data = data.replace("](", f"]({path_prefix}/")

        lines = data.splitlines()
        return "\n".join(lines[1:-1])

    @env.macro
    def include_mltraq_version():
        """
        Return the mltraq version.
        """
        import mltraq

        return mltraq.__version__

    @env.macro
    def include_current_date():
        """
        Return the current time as a yyyy-mm-dd string.
        """
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d")
