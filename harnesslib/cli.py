"""Option declarations shared by the batch and chained runner parsers."""


def add_jobs_arg(parser, *, default, help):
    parser.add_argument("--jobs", "-j", type=int, default=default, help=help)


def add_timeout_arg(parser, *, default, help, short=True):
    flags = ("--timeout", "-t") if short else ("--timeout",)
    parser.add_argument(*flags, type=int, default=default, help=help)


def add_resume_arg(parser, *, help):
    parser.add_argument("--resume", action="store_true", help=help)
