import numpy as np


def nonlin(x, deriv=False):  # Сигмоида и её производная
    return x * (1 - x) if deriv else 1 / (1 + np.exp(-x))


X = np.array([[0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]])
y = np.array([[1, 1, 1, 1]]).T

np.random.seed(1)
syn0 = 2 * np.random.random((3, 1)) - 1  # Инициализация весов

for i in range(100000):
    l0 = X
    l1 = nonlin(np.dot(l0, syn0))  # Прямое распространение
    l1_error = y - l1  # Ошибка
    l1_delta = l1_error * nonlin(l1, True)  # Дельта ошибки
    syn0 += np.dot(l0.T, l1_delta)  # Обновление весов


print("Результат:", l1)
