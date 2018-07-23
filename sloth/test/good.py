# coding        = utf-8
from nltk import  *
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

ar = reversed(a)
print ar
# use map
squares = map(lambda x: x ** 2, a)
# use list comprehension
squares = [x ** 2 for x in a]
squares = [x ** 2 for x in a if x % 2 == 0]
print squares

a = ['a','b','c']
b = [1,2,3]
print dict(zip(a,b))


def get_indexs(array, target='', judge=True):
    for index, item in enumerate(array):
        if judge and item == target:
            yield index
        elif not judge and item != target:
            yield index

array = [1, 2, 3, 4, 1]
result = get_indexs(array, target=1, judge=True)
print(list(result)) # [0, 4]
result = get_indexs(array, 1, True)
print(list(result)) # [0, 4]
result = get_indexs(array, 1)
print(list(result)) # [0, 4]

x1 =['Monty','Python', 'and','the','the','Holy','Holy1', 'Grail']
long_words = [w for w in set(x1) if len(w)>3]
frqents = FreqDist(x1)
freq_words = [w for w in set(x1) if frqents[w]>1]
print freq_words
frqents.plot()
print frqents.items()
print long_words
#print set(x1)
#print sorted(set(x1))
