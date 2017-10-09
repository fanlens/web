#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple base 62 encoding, useful for converting ints into strings with less characters"""
# based on https://stackoverflow.com/a/1119769/4354645
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode(num: int, alphabet: str = ALPHABET) -> str:
    """
    Encode a number in Base 62 (or different alphabet)
    :param num: The number to encode
    :param alphabet: The alphabet to use for encoding
    :return: num converted to base62
    """
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num //= base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def decode(string: str, alphabet: str = ALPHABET) -> int:
    """
    Decode a Base 62 (or different alphabet) encoded string into the number
    :param string: The encoded string
    :param alphabet: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num
