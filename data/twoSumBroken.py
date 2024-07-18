def twoSum(list, target: int):
        for i in range(len(list)):
            for j in range(i + 1, len(list)):
                if (i!= j and list[i] + list[j] == target):
                    return  [i, j]
        return []