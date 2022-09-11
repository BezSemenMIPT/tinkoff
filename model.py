import math
import numpy as np
"""
класс NGramsCounter, который подсчитывает число
n-грамм от 1 (одиночные слова) до order (последовательность order слов).
Входом является строка (тогда n-граммы будут по символам) или список слов.
###############################################################################
#                                  class NGramsCounter
###############################################################################
class NGramsCounter:
    """
    Подсчитывает число n-грамм с n=[1...order]. На их основе можно вычислять
    условную вероятность данного слова перед которым шло (order-1) других слов.
    Словами могут быть символы, строки или числа (индексы слов).
    """

    def __init__(self, order = 1):
        if order < 1:
            print("NGramsCounter: order must be > 0, got: ", order)
            order = 1

        self.order = order           # глубина дерева (макс. длина n-grams)
        self.root  = {}              # корень дерева (наш словарь)
        self.ngrams= [0]*(order+1)   # число n-grams диной n=1,2,...,order
    #---------------------------------------------------------------------------
    def add(self, lst):
        """
        Добавляем новые примеры из списка слов lst.
        Если слова это символы, то lst может быть строкой, иначе это список
        Структура дерева: node = {word: [count, node] }.
        Все возможные n-граммы (w_1...w_order) являются ветками дерева.
        Длина веток  меньше ли равна order. Все они начинаются от self.root.
        """

        print("NGramsCounter::add", end='')
        for n in range(self.order):              # сколько каких n-grams добавилось
            self.ngrams[n+1] += max(len(lst) - n , 0)

        for i in range( len(lst) ):              # бежим по тексту
            node = self.root
            for n, w in enumerate(lst[i: i+self.order]):
                if w in node: node[w][0] += 1    # это слово уже было
                else:         node[w] = [1, {}]  # новое слово
                node = node[w][1]                # на следующий узел дерева

            if i % 64000 == 0:
                print('\r', " "*32,'\r', f"{i*100/len(lst):.1f}%", end='')
        print('\r', " "*32, '\r', end='')
    #---------------------------------------------------------------------------
    def counts(self, lst):
        """
        Возвращает: N(w1...wn),   - число ngrams, где w_i - элементы списка lst
                    N(w1...wn-1), - число ngrams на 1 короче
                    узел          - ветки, выходящие из wn (если n=order, то это {})
        Если len(lst) > order, то по её последним order символам
        Если len(lst) == 1, то возвращает N(w), ngrams[1]
        """

        if len(lst) == 0:
            print("NGramsCounter::counts len(lst) must be > 0, got: ", len(lst))
            return 0, 0, self.root

        if len(lst) > self.order:
            lst = lst[-self.order : ]            # последние order символов

        node = self.root                         # корневой пучок веток
        n_prv, n_cur  = self.ngrams[1], self.ngrams[1]

        for i,w in enumerate(lst):               # по списку слов lst
            if w in node:                        # если слово есть в пучке
                n_prv = n_cur
                n_cur = node[w][0]
                node  = node[w][1]               # берём пучок веток из него
            else:
                if i==len(lst)-1:
                    return 0, n_cur, node        # последнее слово wn не нашли
                else:
                    return 0, 0,     node        # N(w1...wn-1) == 0

        return n_cur, n_prv, node
    #---------------------------------------------------------------------------
    def prob(self, lst, cond=True):
        """
        Вероятность P(lst[0],...,lst[n-2] => lst[n-1]), при n=1: P(lst[0])
        Если cond=False, то безусловная вероятность P(lst[0],...,lst[n-1])
        Если слова это символы, то lst может быть строкой, иначе это список.
        """

        n_cur, n_prv, _ = self.counts(lst)
        if n_cur == 0:
            return 0                              # слово не нашли - вероятность 0

        return n_cur/(n_prv if cond else self.ngrams[len(lst)])

    #---------------------------------------------------------------------------
    def branches(self, lst = []):
        """
        Cлова после списка слов lst в виде пар (слово, сколько): [(w1,cont1),...]
        Просто branches() - это словарь
        Если слова это символы, то lst может быть строкой, иначе это список.
        """

        if len(lst)==0:
            node = self.root
        else:
            n_cur, _, node = self.counts(lst)
            if n_cur == 0:
                return []

        res = [(w, node[w][0]) for w in node]      # пары (слово,вероятность)
        return sorted(res, key=lambda kv: -kv[1])  # сортированы по убыванию вероятности

    #---------------------------------------------------------------------------
    def unique(self, n = None):
        """
        Число уникальных n-грамм (число ветвей дерева длиной n)
        """
        if not n:
            return [ self.unique_rec(self.root, i) for i in range(1, self.order+1) ]
        return self.unique_rec(self.root, n)

    #---------------------------------------------------------------------------
    def unique_rec(self, node, n):
        if n <= 0:
            return 1
        s = 0
        for w in node:
            s += self.unique_rec(node[w][1], n-1)
        return s

    #---------------------------------------------------------------------------
    def all_branches(self):
        """
        Возвращает все ветви дерева node с их числом появления в тексте.
        """
        branches = []
        self.all_branches_rec(self.root,  [],  0, branches)
        return branches

    #---------------------------------------------------------------------------
    def all_branches_rec(self,
                         node,         # текущий узел дерева
                         cur,          # текущая к node ветка при спуске вниз
                         n_cur,        # число таких веток было в тексте
                         branches):    # все ветви дерева от корня
        if not node:
            branches.append( (cur, n_cur) )

        for n in node:                  # по всем детям из узла
            nxt = cur[:] + [n]          # делаем копию пути и добавляем ребёнка
            self.all_branches_rec(node[n][1], nxt, node[n][0], branches)
