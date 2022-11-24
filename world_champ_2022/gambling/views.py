# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.decorators.http import require_POST, require_GET
import datetime
import json

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

@login_required
@require_POST
def predict(request, match_pk):
    match = Match.objects.filter(pk=match_pk).first()
    if (not match):
        return JsonResponse({"error": 1}, status=400)

    now = localtime(timezone.now())
    guess = MatchGuess.objects.filter(guesser = request.user, match = match_pk).first()

    if (localtime(match.time) < now):
        return JsonResponse({"error": 2}, status=400)

    if (guess):
        guess.guess_score_1 = request.POST.get('result1')
        guess.guess_score_2 = request.POST.get('result2')
        guess.save()
    else:
        guess = MatchGuess.objects.create(
                   guesser = request.user,
                   match = match,
                   guess_score_1 = request.POST.get('result1'),
                   guess_score_2 = request.POST.get('result2'),
                   )

    return JsonResponse({"match": match_pk}, status=200)

@login_required
@require_GET
def gambling_list(request):
    matches = Match.objects.select_related('command_1', 'command_2').all().order_by("time")
    guesses = MatchGuess.objects.select_related('match').filter(guesser = request.user)

    now = localtime(timezone.now())

    error=request.GET.get('error')

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
    return render(request, 'gambling/gambling_list.html', {'past_match_info_guesses': past_match_info_guesses, 'match_info_guesses' : match_info_guesses, 'score_choices' : score_choices, 'error' : error})

def get_players(request):
    try:
        if (request.user.player.nicevt) and (not request.user.is_superuser):
            users = User.objects.select_related('player').filter(player__nicevt=True)
        else:
            users = User.objects.select_related('player').all()
    except:
        users = User.objects.select_related('player').all()
    return users

@require_GET
def stats(request):
    return render(request, 'gambling/stats.html')

@require_GET
def stats_JSON(request):
    users = get_players(request)
    matches = Match.objects.all()
    guesses = MatchGuess.objects.select_related('guesser', 'match').all()

    uscores = {}
    for user in users:
        uscores[user] = {}
        uscores[user]['missed'] = 0
        uscores[user]['winner'] = 0
        uscores[user]['difference'] = 0
        uscores[user]['correct'] = 0
        uscores[user]['incorrect'] = 0

    for match in matches:
        if ((match.score_1 == None) or (match.score_2 == None)):
            continue

        match_guesses = [guess for guess in guesses if (guess.match == match)]
        for user in users:
            ug_list = [guess for guess in match_guesses if (guess.guesser.pk == user.pk)]
            if (not ug_list):
                uscores[user]['missed']+=1
                continue

            ug = ug_list[0]

            if ((ug.guess_score_1 == None) or (ug.guess_score_2 == None)):
                uscores[user]['missed']+=1
            else:
                if (((match.score_1 > match.score_2) and (ug.guess_score_1 > ug.guess_score_2)) or
                    ((match.score_1 < match.score_2) and (ug.guess_score_1 < ug.guess_score_2)) or
                    ((match.score_1 == match.score_2) and (ug.guess_score_1 == ug.guess_score_2))):
                    uscores[user]['winner']+=1

                    if (match.score_1 > match.score_2):
                        if ((match.score_1 - match.score_2) == (ug.guess_score_1 - ug.guess_score_2)):
                            uscores[user]['winner']-=1
                            uscores[user]['difference']+=1
                    else:
                        if ((match.score_2 - match.score_1) == (ug.guess_score_2 - ug.guess_score_1)):
                            uscores[user]['winner']-=1
                            uscores[user]['difference']+=1

                    if ((match.score_1 == ug.guess_score_1) and (match.score_2 == ug.guess_score_2)):
                        uscores[user]['difference']-=1
                        uscores[user]['correct']+=1
                else:
                    uscores[user]['incorrect']+=1

    us_list = []
    for user in users:
        data = {}
        data['user'] = { 'first_name' : user.first_name, 'last_name' : user.last_name, 'money' : user.player.money }
        data['winner'] = uscores[user]['winner']
        data['difference'] = uscores[user]['difference']
        data['correct'] = uscores[user]['correct']
        data['missed'] = uscores[user]['missed']
        data['incorrect'] = uscores[user]['incorrect']
        us_list.append(data)

    return HttpResponse(json.dumps({'us_list' : us_list}))

@require_GET
def news(request):
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    yesterday = timezone.make_aware(datetime.datetime.today() - datetime.timedelta(days=1), timezone.get_default_timezone())

    guesses = MatchGuess.objects.select_related('guesser', 'match').all()
    users = get_players(request)

    score_change=[]
    total_scores_before={}
    total_scores_after={}
    matches_before = Match.objects.filter(time__lte=yesterday)
    matches_after = Match.objects.select_related('command_1', 'command_2').filter(time__gt=yesterday, time__lte=now)
    for user in users:
        total_scores_before[user] = 0
        user_guesses = [guess for guess in guesses if (guess.guesser.pk == user.pk)]
        for match in matches_before:
            ug_list = [guess for guess in user_guesses if (guess.match == match)]
            if (ug_list):
                ug = ug_list[0]
                total_scores_before[user] += score_from_match(match.score_1, match.score_2, ug.guess_score_1, ug.guess_score_2)
        total_scores_after[user] = total_scores_before[user]
        for match in matches_after:
            ug_list = [guess for guess in user_guesses if (guess.match == match)]
            if (ug_list):
                ug = ug_list[0]
                total_scores_after[user] += score_from_match(match.score_1, match.score_2, ug.guess_score_1, ug.guess_score_2)
        data={}
        data['user']=user
        data['before']=total_scores_before[user]
        data['after']=total_scores_after[user]
        data['diff']=total_scores_after[user]-total_scores_before[user]
        score_change.append(data)

    mgp = []
    for match in matches_after:
        data={}
        data['match']=match
        usgp=[]
        match_guesses = [guess for guess in guesses if (guess.match.pk == match.pk)]
        for user in users:
            usgp_data={}
            usgp_data['user']=user
            ug_list = [guess for guess in match_guesses if (guess.guesser.pk == user.pk)]
            if (ug_list):
                ug = ug_list[0]
                usgp_data['guess'] = ug
                usgp_data['score'] = score_from_match(match.score_1, match.score_2, ug.guess_score_1, ug.guess_score_2)
            else:
                usgp_data['guess'] = None
                usgp_data['score'] = 0

            usgp.append(usgp_data)
        data['user_guesses']=usgp
        mgp.append(data)

    return render(request, 'gambling/news.html', {'mgp' : mgp, 'score_change' : score_change})

@require_GET
def results(request):
    return render(request, 'gambling/charts.html')

@require_GET
def results_JSON(request):
    users = get_players(request)
    matches = Match.objects.all().order_by('time').prefetch_related('command_1', 'command_2')
    guesses = MatchGuess.objects.all().prefetch_related('guesser', 'match')

    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

    past_matches = [match for match in matches if (localtime(match.time) < now)]
    chart_data = []
    for user in users:
        chart_element = {}
        chart_element['user']={ 'first_name': user.first_name, 'last_name' : user.last_name, 'money' : user.player.money }
        chart_element['data']=[]
        user_guesses = [guess for guess in guesses if guess.guesser.pk == user.pk]
        user_score = 0
        for match in past_matches:
            match_data = {'score': user_score, 'prediction' : u'отсутствует', 'match' : '', 'match_score' : '', 'earned_points' : 0}
            match_data['match'] = match.command_1.name + " - " + match.command_2.name
            match_data['match_score'] = {
                "score_1" : match.score_1,
                "score_2" : match.score_2,
                "extra_score_1" : match.extra_score_1,
                "extra_score_2" : match.extra_score_2,
                "penalty_score_1" : match.penalty_score_1,
                "penalty_score_2" : match.penalty_score_2,
            }
            for guess in user_guesses:
                if (guess.match.pk == match.pk):
                    if ((guess.guess_score_1 != None) and (guess.guess_score_2 != None)):
                        match_data['prediction'] = str(guess.guess_score_1) + " - " + str(guess.guess_score_2)
                    match_data['earned_points'] = score_from_match(match.score_1, match.score_2, guess.guess_score_1, guess.guess_score_2)
                    user_score += match_data['earned_points']
                    match_data['score'] = user_score
                    break

            chart_element['data'].append(match_data)
        chart_data.append(chart_element)

    return HttpResponse(json.dumps({'chart_data' : chart_data}))

@require_GET
def tournament(request):
    commands = Command.objects.all()
    matches = Match.objects.select_related('command_1', 'command_2').all()

    group_names = commands.values_list('group', flat=True).distinct().order_by('group')

    group_matches = matches.filter(stage = Match.MATCH_CLASS_GROUP)

    commands_data = []
    for command in commands:
        command_data={}
        command_data['command'] = command
        command_data['group'] = command.group
        command_data['win'] = 0;
        command_data['draw'] = 0;
        command_data['loose'] = 0;
        command_data['matches_played'] = 0;
        command_data['score'] = 0;
        command_data['goal_difference'] = 0;
        command_data['goals'] = 0;
        command_data['place_score'] = 0;
        command_group_matches = [match for match in group_matches if (match.command_1 == command) or (match.command_2 == command)]
        for command_group_match in command_group_matches:
            if ((command_group_match.score_1 == None) or (command_group_match.score_2 == None)):
                continue

            command_data['matches_played'] += 1;

            if (command_group_match.command_1 == command):
                if (command_group_match.score_1 > command_group_match.score_2):
                    command_data['win'] += 1;
                    command_data['score'] += 3;
                if (command_group_match.score_1 == command_group_match.score_2):
                    command_data['draw'] += 1;
                    command_data['score'] += 1;
                if (command_group_match.score_1 < command_group_match.score_2):
                    command_data['loose'] += 1;
                command_data['goal_difference'] += command_group_match.score_1
                command_data['goal_difference'] -= command_group_match.score_2

                command_data['goals'] += command_group_match.score_1

            if (command_group_match.command_2 == command):
                if (command_group_match.score_1 < command_group_match.score_2):
                    command_data['win'] += 1;
                    command_data['score'] += 3;
                if (command_group_match.score_1 == command_group_match.score_2):
                    command_data['draw'] += 1;
                    command_data['score'] += 1;
                if (command_group_match.score_1 > command_group_match.score_2):
                    command_data['loose'] += 1;

                command_data['goal_difference'] += command_group_match.score_2
                command_data['goal_difference'] -= command_group_match.score_1

                command_data['goals'] += command_group_match.score_2

        command_data['place_score'] += (command_data['score']*100000)
        command_data['place_score'] += (command_data['goal_difference']*100)
        command_data['place_score'] += (command_data['goals']*1)

        commands_data.append(command_data)

    group_tables = []
    for group_name in group_names:
        group_table = {}
        group_table['group_name'] = group_name
        group_table['commands_list'] = []
        group_commands = commands.filter(group = group_name)
        for e in commands_data:
            if (e['command'] in group_commands):
                group_table['commands_list'].append(e)
        group_table['commands_list'].sort(key=lambda x: x['place_score'], reverse=True)
        group_tables.append(group_table)

    return render(request, 'gambling/tournament.html', {'group_tables' : group_tables})
