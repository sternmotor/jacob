Makefile syntax and formatting
===============================


Place a bash heredoc in makefile

* Have a include file containing heredoc definition

        define _script
        cat <<EOF
        SHELL is $SHELL, PID is $$
        have a good time
        EOF
        endef
        export shell_info = $(value _script)

* call it in `Makefile`

        include lib/*

        run:
            @ eval "$$shell_info"
