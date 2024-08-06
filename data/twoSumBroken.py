def twoSum(nums, some_number):
    for i in range(len(nums)):
        for j in range((i + 1), len(nums)):
            if (nums[i] + nums[j]) == some_number + nums[j]:
                return [i, j]
    return []
