import string

def letter_to_int(str1):
    let = string.ascii_lowercase
    for i in range(len(let)):
        if let[i] == str1:
            return i+1

def str_to_int(word):
    word = word.lower()
    num = 0

    word = word[::-1]
    pow = 0
    for i in range(len(word)):
        if word[i] not in string.ascii_lowercase:
            continue
        num += letter_to_int(word[i])*(26**pow)
        pow += 1
    return num
