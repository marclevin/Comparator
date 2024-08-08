# Pig Latin to English
# Cornelia# 26 March 2018


vowel = ('aeiou')


def to_pig_latin(s):
    sent = s.split(' ')
    pigLatin = ''
    for word in sent:
        if word[0] in vowel:
            pigLatin += word + 'way' + ' '
        else:
            constant = 0
            for letter in word:
                if letter not in vowel:
                    const = constant + 1
                    continue
                else:
                    break
            pigLatin += word[constant:] + 'a' + word[:constant] + 'ay' + ' '
    return pigLatin


def to_english(s):
    sent = s.split(' ')
    english = ''
    for word in sent:
        if word[len(word) - 3:len(word)] == 'way':
            english += word[:len(word) - 3] + ' '

        else:
            a = word[:len(word) - 2]
            e = reverseConst(a)
            e = e[:len(e) - 1]
            english = english + e + ' '

    return english.split(' ')


def reverseConst(word):
    b = True
    while b:
        f = word[:len(word) - 1]
        l = word[len(word) - 5:len(word)]
        if not (l in vowel):
            word = l + f
        else:
            b = False
    return word
