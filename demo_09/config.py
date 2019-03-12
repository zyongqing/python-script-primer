RULES = {
    "instance": {
        "sql": "select instance_name || '||' || status from v\$instance;",
        "pipes": [
            "ssh_input",
            "parse_proc",
            "filter_proc",
            "slide_proc",
            "dict_proc",
            "print_json",
        ],
    },
    "tablespace": {
        "sql": "select tablespace_name || '||' || status from dba_tablespaces;",
        "pipes": [
            "ssh_input",
            "parse_proc",
            "filter_proc",
            "slide_proc",
            "print_plain",
        ],
    },
    # "dbfile": {
    #     "sql": "select file_name || '||' || status from dba_data_files;",
    #     "pipes": [
    #         "ssh_input",
    #         "parse_proc",
    #         "filter_proc",
    #         "slide_proc",
    #         "print_plain",
    #     ],
    # },
    # "asmgroup": {
    #     "sql": "select name || '||' || state from v\$asm_diskgroup;",
    #     "pipes": [
    #         "ssh_input",
    #         "parse_proc",
    #         "filter_proc",
    #         "slide_proc",
    #         "dict_proc",
    #         "print_json",
    #     ],
    # },
}
