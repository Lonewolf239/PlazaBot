class SlotConfig:
    """
    +---------------+--------------------+--------------------+--------------------+
    | Параметр      | HONEST             | AGGRESSIVE         | GENEROUS           |
    +---------------+--------------------+--------------------+--------------------+
    | RTP           | 95%                | 92%                | 96%                |
    | House Edge    | 5%                 | 8%                 | 4%                 |
    | Для кого      | Баланс             | Казино+            | Щедрый             |
    +---------------+--------------------+--------------------+--------------------+
    """
    HONEST = {
        'name': 'Честный слот (95% RTP)',
        'description': 'Идеальный баланс: справедливые шансы для игроков, стабильная прибыль для казино',
        'probabilities': {
            'jackpot': 0.001,  # 0.1%
            'big_win': 0.01,  # 1.0%
            'medium_win': 0.10,  # 10%
            'small_win': 0.15,  # 15%
            'break_even': 0.45,  # 45%
            'loss': 0.285,  # 28.5%
        },
        'multipliers': {
            'jackpot': 21.55,
            'big_win': 6.90,
            'medium_win': 2.16,
            'small_win': 1.29,
            'break_even': 1.0,
        }
    }

    AGGRESSIVE = {
        'name': 'Казино-ориентированный (92% RTP)',
        'description': 'Увеличенный доход казино, честные шансы выигрыша для игроков',
        'probabilities': {
            'jackpot': 0.001,  # 0.1%
            'big_win': 0.009,  # 0.9%
            'medium_win': 0.10,  # 10%
            'small_win': 0.15,  # 15%
            'break_even': 0.40,  # 40%
            'loss': 0.341,  # 34.1%
        },
        'multipliers': {
            'jackpot': 22.73,
            'big_win': 7.27,
            'medium_win': 2.27,
            'small_win': 1.36,
            'break_even': 1.0,
        }
    }

    GENEROUS = {
        'name': 'Щедрый слот (96% RTP)',
        'description': 'Максимальный стимул для игроков с честными шансами',
        'probabilities': {
            'jackpot': 0.001,  # 0.1%
            'big_win': 0.012,  # 1.2%
            'medium_win': 0.10,  # 10%
            'small_win': 0.15,  # 15%
            'break_even': 0.50,  # 50%
            'loss': 0.227,  # 22.7%
        },
        'multipliers': {
            'jackpot': 19.30,
            'big_win': 6.17,
            'medium_win': 1.93,
            'small_win': 1.16,
            'break_even': 1.0
        }
    }


class RouletteConfig:
    """
    +---------------------+---------------------+---------------------+---------------------+
    | Параметр            | HONEST              | AGGRESSIVE          | GENEROUS            |
    +---------------------+---------------------+---------------------+---------------------+
    | RTP                 | 97.3%               | 94.6%               | 98.6%               |
    | House Edge          | 2.7%                | 5.4%                | 1.4%                |
    | Для кого            | Справедливо         | Казино+             | Максимум игроков    |
    +---------------------+---------------------+---------------------+---------------------+
    """
    HONEST = {
        'name': 'Честная рулетка (97.3% RTP)',
        'description': 'Справедливые шансы для игроков, стабильная прибыль казино',
        'probabilities': {
            'number_win': 0.027,
            'dozen_win': 0.324,
            'column_win': 0.324,
            'color_win': 0.486,
            'parity_win': 0.486,
            'half_win': 0.486,
        },
        'multipliers': {
            'number': 35,
            'dozen': 2,
            'column': 2,
            'color': 1.25,
            'parity': 1.25,
            'half': 1.25,
        },
        'color_bias': 0.0,
    }

    AGGRESSIVE = {
        'name': 'Казино-ориентированная (94.6% RTP)',
        'description': 'Увеличенный доход казино, честные шансы для игроков',
        'probabilities': {
            'number_win': 0.025,
            'dozen_win': 0.310,
            'column_win': 0.310,
            'color_win': 0.465,
            'parity_win': 0.465,
            'half_win': 0.465,
        },
        'multipliers': {
            'number': 35,
            'dozen': 2,
            'column': 2,
            'color': 1.25,
            'parity': 1.25,
            'half': 1.25,
        },
        'color_bias': 0.03,
    }

    GENEROUS = {
        'name': 'Щедрая рулетка (98.6% RTP)',
        'description': 'Максимальный стимул для игроков, высокий выигрыш',
        'probabilities': {
            'number_win': 0.029,
            'dozen_win': 0.333,
            'column_win': 0.333,
            'color_win': 0.500,
            'parity_win': 0.500,
            'half_win': 0.500,
        },
        'multipliers': {
            'number': 35,
            'dozen': 2,
            'column': 2,
            'color': 1.25,
            'parity': 1.25,
            'half': 1.25,
        },
        'color_bias': -0.02,
    }

    ANIMATION_SETTINGS = {
        'total_steps': 42,
        'start_frame_time': 0.05,
        'frame_acceleration': 0.02,
        'final_frame_duration': 2.0,
    }


class RouletteV2Config:
    HONEST = {
        'name': 'Честная Рулетка V2 (Среднее ХЭ 52.88%)',
        'description': 'Идеальный баланс: справедливые шансы для игроков, стабильная прибыль казино',
        'house_edge': 52.88,
        'rtp': 47.12,
        'multipliers': {
            '1_number': 15,
            '2_numbers': 14,
            '3_numbers': 13,
            '4_numbers': 12,
            '5_numbers': 11,
            '6_numbers': 10,
        },
        'probabilities': {
            '1_number': 1 / 90,
            '2_numbers': 2 / 90,
            '3_numbers': 3 / 90,
            '4_numbers': 4 / 90,
            '5_numbers': 5 / 90,
            '6_numbers': 6 / 90,
        }
    }


class CoinConfig:
    """
    +-----------------+-------------+-------------+-------------+
    | Параметр        | HONEST      | AGGRESSIVE  | GENEROUS    |
    +-----------------+-------------+-------------+-------------+
    | RTP             | 95%         | 75%         | 98%         |
    | House Edge      | 5%          | 25%         | 2%          |
    | Теория          | 50% побед   | 37.5% побед | 49% побед   |
    +-----------------+-------------+-------------+-------------+
    """

    HONEST = {
        'name': 'Честная Монетка (95% RTP)',
        'description': 'Идеальный баланс: 50% побед, стабильная прибыль для казино',
        'rtp': 95,
        'house_edge': 5,
        'target_audience': 'Сбалансированная игра для всех',
        'multiplier': 2,
    }

    AGGRESSIVE = {
        'name': 'Казино-ориентированная Монетка (75% RTP)',
        'description': 'Высокий доход казино: только 37.5% побед для игроков',
        'rtp': 75,
        'house_edge': 25,
        'target_audience': 'Максимальная прибыль казино',
        'multiplier': 2,
    }

    GENEROUS = {
        'name': 'Щедрая Монетка (98% RTP)',
        'description': 'Привлечение игроков: 49% побед (почти честная)',
        'rtp': 98,
        'house_edge': 2,
        'target_audience': 'Привлечение новых игроков, лояльность',
        'multiplier': 2,
    }

    ANIMATION_SETTINGS = {
        'total_steps': 20,
        'start_frame_time': 0.05,
        'frame_acceleration': 0.02,
        'final_frame_duration': 2.0,
    }


class DiceConfig:
    """Конфигурации для игры в кости"""
    HONEST = {
        'multipliers': {
            'sum_2': 35,
            'sum_3': 17,
            'sum_4': 11,
            'sum_5': 8,
            'sum_6': 6,
            'sum_7': 5,
            'sum_8': 6,
            'sum_9': 8,
            'sum_10': 11,
            'sum_11': 17,
            'sum_12': 35,
            'parity': 1.95,
            'doubles': 5,
            'compare': 1.95,
            'range': 1.95
        },
        'probabilities': {
            2: 1 / 36, 3: 2 / 36, 4: 3 / 36, 5: 4 / 36, 6: 5 / 36, 7: 6 / 36,
            8: 5 / 36, 9: 4 / 36, 10: 3 / 36, 11: 2 / 36, 12: 1 / 36
        }
    }

    ANIMATION_SETTINGS = {
        'frames': 20,
        'delay': 0.1
    }


class MinesConfig:
    """
    Конфигурация для игры Mines (Тапер)

    +-------------------+-------------------+-------------------+-------------------+
    | Параметр          | HONEST            | AGGRESSIVE        | GENEROUS          |
    +-------------------+-------------------+-------------------+-------------------+
    | Мин для RTP       | 15 (15%)          | 20 (20%)          | 10 (10%)          |
    | Макс коефф        | 1.5x              | 1.8x              | 1.2x              |
    | Стратегия         | Баланс            | Казино+           | Привлечение       |
    | Расчитано на      | Регулярные игроки | Агрессивные игры  | Новые игроки      |
    +-------------------+-------------------+-------------------+-------------------+
    """

    HONEST = {
        'name': 'Честный Тапер (Баланс)',
        'description': 'Идеальный баланс: справедливые шансы для игроков, стабильная прибыль казино',
        'bombs_count': 10,
        'min_coef': 0.01,
        'max_coef': 1.5,
        'rtp': 95,
        'house_edge': 5,
        'target_audience': 'Сбалансированная игра для всех'
    }

    AGGRESSIVE = {
        'name': 'Казино-ориентированный Тапер (92% RTP)',
        'description': 'Увеличенный доход казино, честные шансы для игроков',
        'bombs_count': 15,
        'min_coef': 0.01,
        'max_coef': 1.8,
        'rtp': 92,
        'house_edge': 8,
        'target_audience': 'Максимальная прибыль казино'
    }

    GENEROUS = {
        'name': 'Щедрый Тапер (97% RTP)',
        'description': 'Максимальный стимул для игроков с честными шансами',
        'bombs_count': 5,
        'min_coef': 0.01,
        'max_coef': 1.2,
        'rtp': 97,
        'house_edge': 3,
        'target_audience': 'Привлечение новых игроков, лояльность'
    }
