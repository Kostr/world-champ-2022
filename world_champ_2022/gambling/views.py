# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import localtime

from .models import Match, MatchGuess, Command


def score_from_match(match_score_1, match_score_2, guess_score_1, guess_score_2):
    score = 0
    if ((match_score_1 == None) or (match_score_2 == None) or (guess_score_1 == None) or (guess_score_2 == None)):
        return score

    if (((match_score_1 > match_score_2) and (guess_score_1 > guess_score_2)) or
        ((match_score_1 < match_score_2) and (guess_score_1 < guess_score_2)) or
        ((match_score_1 == match_score_2) and (guess_score_1 == guess_score_2))):
        score += 1

    if (match_score_1 > match_score_2):
        if ((match_score_1 - match_score_2) == (guess_score_1 - guess_score_2)):
            score += 1
    else:
        if ((match_score_2 - match_score_1) == (guess_score_2 - guess_score_1)):
            score += 1

    if ((match_score_1 == guess_score_1) and (match_score_2 == guess_score_2)):
        score += 1

    return score

def gambling_list(request):
    matches = Match.objects.select_related('command_1').all().order_by("time")
    guesses = MatchGuess.objects.select_related('match').filter(guesser = request.user)

    anchor = ''
    now = localtime(timezone.now())

    error=''

    if request.POST:
        for match in matches:
            if (('action_' + str(match.id)) in request.POST):
                mt = match.time
                if (localtime(mt) < now):
                    error = u"Время начала матча прошло, ставку изменить невозможно!"
                    break;

                try:
                    mg = [guess for guess in guesses if (guess.match == match)][0]
                    mg.guess_score_1 = request.POST['result1']
                    mg.guess_score_2 = request.POST['result2']
                    mg.save()
                except Exception as e:
                    mg = MatchGuess.objects.create(
                            guesser = request.user,
                            match = match,
                            guess_score_1 = request.POST['result1'],
                            guess_score_2 = request.POST['result2'],
                            )
                    pass
                anchor = 'mg_' + str(match.id)

    guesses = MatchGuess.objects.select_related('match').filter(guesser = request.user)
    match_info_guesses = []
    past_match_info_guesses = []
    for match in matches:
        match_info_guess={}
        match_info_guess['match'] = match
        try:
            match_info_guess['guess'] = [guess for guess in guesses if (guess.match == match)][0]
        except:
            match_info_guess['guess'] = None

        match_info_guess['enabled'] = (localtime(match.time) > now)

        if (match.stage == Match.MATCH_CLASS_GROUP):
            match_info_guess['stage'] = u"Групповой этап. Группа " + match.command_1.group
        else:
            match_info_guess['stage'] = "?"
            for match_class_tuple in Match.MATCH_CLASSES:
                if match_class_tuple[0] == match.stage:
                    match_info_guess['stage'] = match_class_tuple[1]

        if (not match_info_guess['enabled']):
            try:
                match_info_guess['plus_score'] = score_from_match(match.score_1, match.score_2, match_info_guess['guess'].guess_score_1, match_info_guess['guess'].guess_score_2)
            except:
                match_info_guess['plus_score'] = 0
            past_match_info_guesses.append(match_info_guess)
        else:
            match_info_guesses.append(match_info_guess)

    score_choices = [0,1,2,3,4,5,6,7,8,9]
    return render(request, 'gambling/gambling_list.html', {'past_match_info_guesses': past_match_info_guesses, 'match_info_guesses' : match_info_guesses, 'score_choices' : score_choices, 'anchor' : anchor, 'error' : error})
