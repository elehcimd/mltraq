def define_env(env):
    @env.macro
    def include_code(pathname, title=None, lang="py", linesnum=True, hl_lines=None, ln_src=None, ln_out=None):
        """Include a source code file

        Args:
            pathname (_type_): _description_
            title (_type_, optional): _description_. Defaults to None.
            lang (str, optional): _description_. Defaults to "py".
            linesnum (bool, optional): _description_. Defaults to True.
            hl_lines (_type_, optional): _description_. Defaults to None.
            ln_src (_type_, optional): _description_. Defaults to None.
            ln_out (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if hl_lines:
            hl_lines = f'hl_lines="{hl_lines}"'
        else:
            hl_lines = ""

        if title:
            title = f'title="{title}"'
        else:
            title = ""

        if linesnum:
            linesnum = 'linenums="1"'
        else:
            linesnum = ""

        code_src_lines = open(f"{pathname}.src").readlines()
        code_out_lines = open(f"{pathname}.out").readlines()

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

        code_src = "".join(code_src_lines[ln_src[0] - 1 : ln_src[1]])
        code_out = "".join(code_out_lines[ln_out[0] - 1 : ln_out[1]])

        return (
            f"```{lang} {title} {linesnum} {hl_lines}\n{code_src}\n```\n"
            f'```title="Output" linenums="1"\n{code_out}\n```\n'
        )
