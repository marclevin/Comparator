def lengthOfLastWord(s):
    words = s.strip().split()
    if not words:
        return 0

    return len(words[(- 1)])
