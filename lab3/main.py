import matplotlib.pyplot as plt

def calculate_metrics(lambd, mu, m):
    rho = lambd / mu
    if rho == 1:
        p_loss = 1 / (m + 2)
        L = (m + 1) / 2
        Lq = sum((k - 1) * (1 / (m + 2)) for k in range(1, m + 2))
        p0 = 1 / (m + 2)
    else:
        rho_m_plus_1 = rho ** (m + 1)
        denominator = 1 - rho ** (m + 2)
        p_loss = (1 - rho) * rho_m_plus_1 / denominator

        # Расчет L
        sum_L = 0.0
        for k in range(m + 2):
            sum_L += k * (1 - rho) * (rho ** k) / denominator
        L = sum_L

        # Расчет Lq
        Lq = 0.0
        for k in range(1, m + 2):
            Lq += (k - 1) * (1 - rho) * (rho ** k) / denominator

        p0 = (1 - rho) / denominator

    # эффективная интенсивность входящего потока
    lambd_eff = lambd * (1 - p_loss)

    # среднее время ожидания и пребывания
    Wq = Lq / lambd_eff if lambd_eff != 0 else 0
    W = L / lambd_eff if lambd_eff != 0 else 0

    # коэффициент загрузки
    rho_effective = 1 - p0

    return {
        'P_loss': p_loss,
        'L': L,
        'Lq': Lq,
        'Wq': Wq,
        'W': W,
        'rho_effective': rho_effective
    }

lambd = 8  # заявок в час
mu = 10    # заявок в час
max_m_to_test = 15  # Максимальная длина очереди для анализа

m_values = list(range(0, max_m_to_test + 1))
p_loss_values = []
wq_values = []

for m in m_values:
    metrics = calculate_metrics(lambd, mu, m)
    p_loss_values.append(metrics['P_loss'])
    wq_values.append(metrics['Wq'])
    print(f"m={m}: P_loss={metrics['P_loss']:.4f}, Wq={metrics['Wq']:.4f} часов")

optimal_m = None
for m, p_loss in zip(m_values, p_loss_values):
    if p_loss <= 0.05:
        optimal_m = m
        break

print(f"\nОптимальная длина очереди m={optimal_m} (вероятность потерь {p_loss_values[optimal_m]:.2%} ≤ 5%)")

plt.figure(figsize=(10, 6))
plt.plot(m_values, p_loss_values, marker='o', linestyle='-', color='b')
plt.axhline(y=0.05, color='r', linestyle='--', label='Порог 5%')
plt.xlabel('Длина очереди (m)')
plt.ylabel('Вероятность потерь')
plt.title('Зависимость вероятности потерь от длины очереди')
plt.legend()
plt.grid(True)

plt.figure(figsize=(10, 6))
plt.plot(m_values, wq_values, marker='o', linestyle='-', color='g')
plt.xlabel('Длина очереди (m)')
plt.ylabel('Среднее время ожидания (часы)')
plt.title('Зависимость среднего времени ожидания от длины очереди')
plt.grid(True)

plt.show()