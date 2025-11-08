class SlotConfig:
    # +---------------+--------------------+--------------------+--------------------+
    # | Параметр      | HONEST             | AGGRESSIVE         | GENEROUS           |
    # +---------------+--------------------+--------------------+--------------------+
    # | RTP           | 95%                | 92%                | 96%                |
    # | House Edge    | 5%                 | 8%                 | 4%                 |
    # | Для кого      | Баланс             | Казино+            | Щедрый             |
    # +---------------+--------------------+--------------------+--------------------+

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
            'number_win': 0.027,  # 2.7%
            'color_win': 0.486,   # 48.6%
            'range_win': 0.486,   # 48.6%
            'dozen_win': 0.324,   # 32.4%
            'column_win': 0.324,  # 32.4%
        },
        'multipliers': {
            'number': 35,
            'color': 1.25,
            'range': 1.25,
            'dozen': 2,
            'column': 2,
        },
        'color_bias': 0.0,
    }

    AGGRESSIVE = {
        'name': 'Казино-ориентированная (94.6% RTP)',
        'description': 'Увеличенный доход казино, честные шансы для игроков',
        'probabilities': {
            'number_win': 0.025,  # 2.5%
            'color_win': 0.470,   # 47%
            'range_win': 0.470,   # 47%
            'dozen_win': 0.315,   # 31.5%
            'column_win': 0.315,  # 31.5%
        },
        'multipliers': {
            'number': 35,
            'color': 1.25,
            'range': 1.25,
            'dozen': 2,
            'column': 2,
        },
        'color_bias': 0.03,
    }

    GENEROUS = {
        'name': 'Щедрая рулетка (98.6% RTP)',
        'description': 'Максимальный стимул для игроков, высокий выигрыш',
        'probabilities': {
            'number_win': 0.029,  # 2.9%
            'color_win': 0.500,   # 50%
            'range_win': 0.500,   # 50%
            'dozen_win': 0.333,   # 33.3%
            'column_win': 0.333,  # 33.3%
        },
        'multipliers': {
            'number': 35,
            'color': 1.25,
            'range': 1.25,
            'dozen': 2,
            'column': 2,
        },
        'color_bias': -0.02,
    }

    ANIMATION_SETTINGS = {
        'total_steps': 20,
        'start_frame_time': 0.05,
        'frame_acceleration': 0.02,
        'final_frame_duration': 2.0,
    }
