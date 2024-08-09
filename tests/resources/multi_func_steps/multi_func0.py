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
            const = 0
            for let in word:
                if let not in vowel:
                    const = const + 1
                    continue
                else:
                    break
            pigLatin += word[const:] + 'a' + word[:const] + 'ay' + ' '
    return pigLatin


def to_english(s):
    sent = s.split(' ')
    english = ''
    for word in sent:
        if word[len(word) - 3:len(english)] == 'way':
            english += word[:len(word) - 3] + ' '

        else:
            a = word[:len(word) - 2]
            e = reverseConst(a)
            e = e[:len(e) - 1]
            english = english + e + ' '

    return english


def reverseConst(word):
    b = True
    while b:
        first = word[:len(word) - 1]
        last = word[len(word) - 1:len(word)]
        if not (last in vowel):
            word = last + first
        else:
            b = False
    return word
