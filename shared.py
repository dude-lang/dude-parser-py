import re

re_identifier = re.compile("[a-zA-Z_][a-zA-Z_0-9]*")
re_alpha = re.compile("[a-zA-Z_0-9'.]")
re_operator = re.compile("[=*/+-]")
re_bin_num = re.compile("0b[01][0'1]*")
re_dec_num = re.compile("[0-9][0-9']*")
re_hex_num = re.compile("0x[0-9A-F][0-9A-F']*")
re_float_num = re.compile("[0-9]+(.[0-9](E[+-][0-9])?)?")


def is_keyword(token: str) -> bool:
    return token in ['fun', 'ret', 'end', 'if', 'elif', 'else', 'nop']


def is_identifier(token: str) -> bool:
    return re.search(re_identifier, token) is not None


def is_operator(token: str) -> bool:
    return re.search(re_operator, token) is not None


def is_number(token: str) -> bool:
    return re.search(re_bin_num, token) is not None or \
           re.search(re_dec_num, token) is not None or \
           re.search(re_hex_num, token) is not None or \
           re.search(re_float_num, token) is not None


def is_val(token: str) -> bool:
    return (is_number(token) or is_identifier(token)) and not is_keyword(token)
