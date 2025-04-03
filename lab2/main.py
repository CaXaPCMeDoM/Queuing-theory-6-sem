import math
import numpy as np
import matplotlib.pyplot as plt


def calculate_characteristics(lambd, mu, n):
    rho = lambd / (n * mu)
    if rho >= 1:
        return {
            'P0': 0,
            'P_queued': 1,
            'Lq': float('inf'),
            'Wq': float('inf'),
            'W': float('inf'),
            'rho': rho
        }

    sum_part = 0.0
    for k in range(n):
        sum_part += ((lambd / mu) ** k) / math.factorial(k)
    second_part = ((lambd / mu) ** n) / (math.factorial(n) * (1 - rho))
    P0 = 1 / (sum_part + second_part)

    numerator = ((lambd / mu) ** n) / math.factorial(n)
    denominator = (1 - rho)
    P_queued = (numerator / denominator) * P0

    Lq = (P_queued * rho) / (1 - rho)
    Wq = Lq / lambd
    W = Wq + (1 / mu)

    return {
        'P0': P0,
        'P_queued': P_queued,
        'Lq': Lq,
        'Wq': Wq,
        'W': W,
        'rho': rho
    }


lambd = 10  # заявок/час
mu = 3  # заявок/час на канал
n = 4



chars = calculate_characteristics(lambd, mu, n)
print("Характеристики системы при n=4, μ=3:")
for key, value in chars.items():
    print(f"{key}: {value:.4f}")

n_values = range(4, 11)
wq_list = []
lq_list = []



for n in n_values:
    chars = calculate_characteristics(lambd, mu, n)
    wq_list.append(chars['Wq'])
    lq_list.append(chars['Lq'])

plt.figure(figsize=(10, 6))
plt.plot(n_values, wq_list, marker='o', label='Wq (часы)')
plt.plot(n_values, lq_list, marker='s', label='Lq (заявки)')
plt.xlabel('Количество каналов (n)')
plt.ylabel('Значение')
plt.title('Зависимость Wq и Lq от количества каналов')
plt.legend()
plt.grid(True)
plt.show()



mu_values = np.linspace(3, 5, 10)
n = 4
wq_mu = []
lq_mu = []

for mu in mu_values:
    chars = calculate_characteristics(lambd, mu, n)
    wq_mu.append(chars['Wq'])
    lq_mu.append(chars['Lq'])

plt.figure(figsize=(10, 6))
plt.plot(mu_values, wq_mu, marker='o', label='Wq (часы)')
plt.plot(mu_values, lq_mu, marker='s', label='Lq (заявки)')
plt.xlabel('Интенсивность обслуживания (μ)')
plt.ylabel('Значение')
plt.title('Зависимость характеристик от μ при n=4')
plt.legend()
plt.grid(True)
plt.show()