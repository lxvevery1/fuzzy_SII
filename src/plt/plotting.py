import matplotlib.pyplot as plt
import numpy as np


def plot_comparison_Q(correspondences_mamdani, correspondences_larsen, A, B):
    """
    Строит графики сравнения методов импликации Мамдани и Ларсена.
    """
    num_rules = len(correspondences_mamdani)

    for rule_idx in range(num_rules):
        # Получаем матрицы для текущего правила
        mamdani_matrix = np.array(correspondences_mamdani[rule_idx])
        larsen_matrix = np.array(correspondences_larsen[rule_idx])

        # Создаем фигуру
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        fig.suptitle(f"Сравнение методов импликации для правила {rule_idx + 1}")

        # График для Мамдани
        ax = axes[0]
        c = ax.imshow(mamdani_matrix, cmap="viridis", aspect="auto")
        ax.set_title("Импликация Мамдани")
        ax.set_xlabel("a")
        ax.set_ylabel("b")
        ax.set_xticks(range(len(B.columns)))
        ax.set_xticklabels(B.columns)
        ax.set_yticks(range(len(A.columns)))
        ax.set_yticklabels(A.columns)
        fig.colorbar(c, ax=ax)

        # График для Ларсена
        ax = axes[1]
        c = ax.imshow(larsen_matrix, cmap="viridis", aspect="auto")
        ax.set_title("Импликация Ларсена")
        ax.set_xlabel("a")
        ax.set_ylabel("b")
        ax.set_xticks(range(len(B.columns)))
        ax.set_xticklabels(B.columns)
        ax.set_yticks(range(len(A.columns)))
        ax.set_yticklabels(A.columns)
        fig.colorbar(c, ax=ax)

        plt.tight_layout()
        plt.show()


def plot_comparison_curve(correspondences_mamdani, correspondences_larsen, A, B):
    """
    Строит график разницы значений между методами импликации Мамдани и Ларсена.
    """
    num_rules = len(correspondences_mamdani)

    # Для каждой матрицы различий создаем кривую
    for rule_idx in range(num_rules):
        mamdani_matrix = np.array(correspondences_mamdani[rule_idx])
        larsen_matrix = np.array(correspondences_larsen[rule_idx])

        # Вычисляем разницу между матрицами
        difference_matrix = mamdani_matrix - larsen_matrix

        # Суммируем разности по строкам, чтобы получить общий эффект для каждого значения
        aggregated_difference = difference_matrix.sum(axis=0)  # Сумма по строкам

        # График кривой разности
        plt.figure(figsize=(8, 5))
        plt.plot(
            range(len(aggregated_difference)),
            aggregated_difference,
            label=f"Разница для правила {rule_idx + 1}",
            marker="o",
        )
        plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        plt.xticks(ticks=range(len(B.columns)), labels=B.columns)
        plt.title(f"Разница между методами для правила {rule_idx + 1}")
        plt.xlabel("Температура")
        plt.ylabel("Разница значений (Мамдани - Ларсен)")
        plt.legend()
        plt.grid(True)
        plt.show()


def plot_mamdani_larsen(x, mamdani_values, larsen_values):
    """
    Строит график с результатами агрегации Мамдани и Ларсена.

    Parameters:
    - x: numpy.ndarray или список, значения по оси X.
    - mamdani_values: numpy.ndarray или список, значения агрегации Мамдани.
    - larsen_values: numpy.ndarray или список, значения агрегации Ларсена.
    """
    plt.figure(figsize=(10, 6))

    # Построение графиков
    plt.plot(x, mamdani_values, label="Мамдани", color="blue", linewidth=2)
    plt.plot(
        x, larsen_values, label="Ларсен", color="orange", linestyle="--", linewidth=2
    )

    # Настройка графика
    plt.title("Агрегация Мамдани и Ларсена", fontsize=14)
    plt.xlabel("X", fontsize=12)
    plt.ylabel("Значение функции принадлежности", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)

    # Отображение графика
    plt.show()
