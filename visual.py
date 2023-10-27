import pygame
import datetime
import DB

BACKGROUND_COLOR = (255, 255, 255)
FONT_COLOR = (0, 0, 0)
GOOD_CIRCLE_COLOR = (209, 240, 194)
BAD_CIRCLE_COLOR = (242, 232, 201)
NONE_CIRCLE_COLOR = BACKGROUND_COLOR
CURRENT_DAY_COLOR = (227, 37, 107)
HISTORY_CIRCLE_COLOR = (231, 232, 230)




# period in ('month, 'week', custom < 45)
def create_activities_img(activities, dates, matrix) -> str:
    y, m, d = str(datetime.date.today()).split('-')
    current_day = int(d), int(m)
    circle_d = 70
    days_line_height = 35
    months_line_height = 35
    w = circle_d * len(dates)
    h = months_line_height + days_line_height + circle_d * len(activities)
    surface_circles = pygame.Surface((w, h))
    surface_circles.fill(BACKGROUND_COLOR)
    last_month = None
    for i, date in enumerate(dates):
        day, month = date
        if last_month != month:
            rendered_month = font.render(months[month], True, FONT_COLOR)
            rect_month = rendered_month.get_rect(center=(circle_d * i + circle_d // 2, months_line_height// 2))
            surface_circles.blit(rendered_month, rect_month)
            last_month = month
        rendered_day = font.render(str(day), True, FONT_COLOR)
        rect_day = rendered_day.get_rect(center=(circle_d * i + circle_d // 2, months_line_height + days_line_height // 2))
        surface_circles.blit(rendered_day, rect_day)

        for row in range(len(matrix)):
            x = circle_d * i + circle_d // 2
            y = months_line_height + days_line_height + row * circle_d + circle_d // 2
            if date == current_day:
                pygame.draw.circle(surface_circles, CURRENT_DAY_COLOR, (x, y), circle_d // 2 - 1)
            else:
                pygame.draw.circle(surface_circles, FONT_COLOR, (x, y), circle_d // 2 - 1)
            if matrix[row][i] == 1:
                pygame.draw.circle(surface_circles, GOOD_CIRCLE_COLOR, (x, y), circle_d // 2 - 2)
            elif matrix[row][i] == 0:
                pygame.draw.circle(surface_circles, BAD_CIRCLE_COLOR, (x, y), circle_d // 2 - 2)
            elif matrix[row][i] == -1:
                pygame.draw.circle(surface_circles, HISTORY_CIRCLE_COLOR, (x, y), circle_d // 2 - 2)
            else:
                pygame.draw.circle(surface_circles, NONE_CIRCLE_COLOR, (x, y), circle_d // 2 - 2)
    top_space = 20
    title_space = 100
    left_space = 20
    bottom_space = 20
    text_width = 300
    right_space = 20
    between_space = 0
    H = surface_circles.get_height() + top_space + title_space + bottom_space
    W = surface_circles.get_width() + left_space + text_width + right_space + between_space
    all_surface = pygame.Surface((W, H))
    all_surface.fill(BACKGROUND_COLOR)
    x = left_space + text_width + between_space
    y = top_space + title_space
    all_surface.blit(surface_circles, surface_circles.get_rect(topleft=(x, y)))
    for i, act in enumerate(activities):
        if len(act) > 21:
            last_space = -1
            for j in reversed(range(21)):
                if act[j] == ' ':
                    last_space = j
                    break
            if last_space == -1:
                last_space = 21
            act1 = act[:last_space]
            act2 = act[last_space + 1:last_space + 1 + 21]
            act_text_1 = font.render(act1, True, FONT_COLOR)
            dif = (circle_d - act_text_1.get_height() * 2) // 2
            x = left_space
            y = months_line_height + top_space + title_space + days_line_height + i * circle_d + dif
            all_surface.blit(act_text_1, (x, y))
            act_text_2 = font.render(act2, True, FONT_COLOR)
            y += act_text_1.get_height()
            all_surface.blit(act_text_2, (x, y))
        else:
            act_text = font.render(act, True, FONT_COLOR)
            H = months_line_height + top_space + title_space + days_line_height + i * circle_d + (circle_d - act_text.get_height()) // 2
            all_surface.blit(act_text, (left_space, H))
    title = title_font.render('Your Journal', True, FONT_COLOR)
    all_surface.blit(title, (left_space, top_space))

    pygame.image.save(all_surface, 'krya.jpg')
    return 'krya.jpg'


# period in ('year', 'season', 'month, 'week', custom <= 366)
def create_activity_img_by_period(user, activity_name, period) -> str:
    if period == 'week':
        start = 0
        end = 7
        return create_activity_img(user, activity_name, start, end)
    return ''


def create_activity_img(user, activity_name, start, end) -> str:
    surface = pygame.Surface((500, 50))
    week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    for i, text in enumerate(week):
        rendered_text = font.render(text, True, (255, 255, 255))
        surface.blit(rendered_text, (10 + 40 * i, 10))
    pygame.image.save(surface, 'krya.jpg')
    return 'krya.jpg'


# create_activity_img(1, 1, 1, 1)
pygame.font.init()
shrift_destination = 'shrifts\\RobotoMono.ttf'
font = pygame.font.Font(shrift_destination, 21)
title_font = pygame.font.Font(shrift_destination, 70)
months = {
    1: 'янв',   2: 'фев',   3: 'март',
    4: 'апр',   5: 'май',   6: 'июн',
    7: 'июл',   8: 'авг',   9: 'сент',
    10: 'окт',  11: 'нояб', 12: 'дек',
}

# create_activities_img(
#                         ['бeгал и скакал по лесу среди берёзок',
#                          'прыгал через забор между РФ и РБ и не видел разницы',
#                          'спал',
#                          'рррррррррррррррррррррррррррррррРРРРРРРРРРРРРРРРРРРРРРРРРРРРРРР'],
#                         [(30, 1), (31, 1), (1, 2), (2, 2), (3, 2), (26, 10), (5, 2)],
#                         [
#                             [1, 0, 0, 1, 1, 0, None],
#                             [1, 1, 1, 1, 1, 1, None],
#                             [0, 0, 0, 0, 0, 0, None],
#                             [0, 0, 1, 0, 0, 1, None],
#                         ]
# )
# TODO нормальный нейминг файлов

