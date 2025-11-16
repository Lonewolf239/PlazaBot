from typing import List, Dict, Any
from io import BytesIO
from matplotlib import rcParams
import matplotlib.pyplot as plt

rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False


class PLT:
    @staticmethod
    def build_profit_chart(db_records: List[Dict[str, Any]]) -> BytesIO:
        if not db_records:
            return PLT._create_empty_chart()
        transaction_ids = []
        amounts = []
        balances_before = []
        balances_after = []
        for record in sorted(db_records, key=lambda x: x['transaction_id']):
            try:
                transaction_ids.append(record['transaction_id'])
                amounts.append(float(record['amount']))
                balances_before.append(float(record['balance_before_withdrawal']))
                balances_after.append(float(record['balance_after_withdrawal']))
            except (ValueError, TypeError, KeyError) as e:
                print(f"Ошибка при обработке записи: {e}")
                continue
        if not amounts:
            return PLT._create_empty_chart()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('График прибыли', fontsize=16, fontweight='bold')
        ax1.bar(transaction_ids, amounts, color='#2ecc71', alpha=0.7, edgecolor='#27ae60')
        ax1.set_xlabel('ID транзакции', fontsize=11)
        ax1.set_ylabel('Размер вывода $', fontsize=11)
        ax1.set_title('Размер каждого вывода средств', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_facecolor('#f8f9fa')
        for i, v in enumerate(amounts):
            ax1.text(transaction_ids[i], v + max(amounts) * 0.01, f'{v:.2f}',
                     ha='center', va='bottom', fontsize=9)
        ax2.plot(transaction_ids, balances_before, marker='o', linestyle='-',
                 linewidth=2, markersize=6, label='Баланс до вывода', color='#3498db')
        ax2.plot(transaction_ids, balances_after, marker='s', linestyle='-',
                 linewidth=2, markersize=6, label='Баланс после вывода', color='#e74c3c')
        ax2.set_xlabel('ID транзакции', fontsize=11)
        ax2.set_ylabel('Баланс $', fontsize=11)
        ax2.set_title('Баланс до и после вывода средств', fontsize=12, fontweight='bold')
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_facecolor('#f8f9fa')
        total_withdrawn = sum(amounts)
        avg_withdrawal = total_withdrawn / len(amounts) if amounts else 0
        max_withdrawal = max(amounts) if amounts else 0
        stats_text = (
            f'Всего выведено: {total_withdrawn:.2f} $.\n'
            f'Среднее значение: {avg_withdrawal:.2f} $.\n'
            f'Максимум: {max_withdrawal:.2f} $.\n'
            f'Количество транзакций: {len(amounts)}'
        )
        fig.text(0.99, 0.01, stats_text, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                 ha='right', va='bottom')
        plt.tight_layout(rect=[0, 0.08, 1, 0.96])
        img_byte_arr = BytesIO()
        plt.savefig(img_byte_arr, format='PNG', dpi=100, bbox_inches='tight')
        img_byte_arr.seek(0)
        plt.close(fig)
        return img_byte_arr

    @staticmethod
    def _create_empty_chart() -> BytesIO:
        """Создает пустой график при отсутствии данных"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Нет данных для отображения',
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        img_byte_arr = BytesIO()
        plt.savefig(img_byte_arr, format='PNG', dpi=100)
        img_byte_arr.seek(0)
        plt.close(fig)
        return img_byte_arr
