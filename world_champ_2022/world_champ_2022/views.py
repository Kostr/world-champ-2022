from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import localtime
import datetime
import json

from gambling.models import Match, MatchGuess, Command


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def login_redirect(request):
    return HttpResponseRedirect('/login')

def start_page(request):
    return render(request, 'home.html')

def get_players(request):
    try:
        if (request.user.player.nicevt) and (not request.user.is_superuser):
            users = User.objects.select_related('player').filter(player__nicevt=True)
        else:
            users = User.objects.select_related('player').all()
    except:
        users = User.objects.select_related('player').all()
    return users

def stats(request):
    return render(request, 'stats.html')

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

        for user in users:
            try:
                ug = [guess for guess in guesses if (guess.guesser.pk == user.pk) and (guess.match == match)][0]

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
            except:
                uscores[user]['missed']+=1

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

def news(request):
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    yesterday = timezone.make_aware(datetime.datetime.today() - datetime.timedelta(days=1), timezone.get_default_timezone())

    guesses = MatchGuess.objects.select_related('guesser', 'match').all()

    users = get_players(request)

    mgp = []
    matches = Match.objects.filter(time__lte=now, time__gt=yesterday)
    for match in matches:
        data={}
        data['match']=match
        usgp=[]
        for user in users:
            usgp_data={}
            usgp_data['user']=user
            try:
                ug = [guess for guess in guesses if (guess.guesser.pk == user.pk) and (guess.match == match)][0]
                usgp_data['guess'] = ug
                usgp_data['score'] = 0
                usgp_data['score'] += score_from_match(match.score_1, match.score_2, ug.guess_score_1, ug.guess_score_2)
            except:
                usgp_data['guess'] = None
                usgp_data['score'] = 0

            usgp.append(usgp_data)
        data['user_guesses']=usgp
        mgp.append(data)

    total_scores_before={}
    total_scores_after={}
    for user in users:
        total_scores_before[user] = 0
        total_scores_after[user] = 0

    matches = Match.objects.filter(time__lte=yesterday)
    for match in matches:
        for user in users:
            try:
                ug = [guess for guess in guesses if (guess.guesser.pk == user.pk) and (guess.match == match)][0]
                total_scores_before[user] += score_from_match(match.score_1, match.score_2, ug.guess_score_1, ug.guess_score_2)
            except:
                pass

    matches = Match.objects.filter(time__lte=now)
    for match in matches:
        for user in users:
            try:
                ug = [guess for guess in guesses if (guess.guesser.pk == user.pk) and (guess.match == match)][0]
                total_scores_after[user] += score_from_match(match.score_1, match.score_2, ug.guess_score_1, ug.guess_score_2)
            except:
                pass

    score_change=[]
    for user in users:
        data={}
        data['user']=user
        data['before']=total_scores_before[user]
        data['after']=total_scores_after[user]
        data['diff']=total_scores_after[user]-total_scores_before[user]
        score_change.append(data)

    return render(request, 'news.html', {'mgp' : mgp, 'score_change' : score_change})   

def results(request):
    return render(request, 'charts.html')

def results_JSON(request):
    users = get_players(request)
    matches = Match.objects.all().order_by('time').prefetch_related('command_1', 'command_2')
    guesses = MatchGuess.objects.all().prefetch_related('guesser', 'match')
    match_score_guesses = []

    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

    total_points = {}
    for user in users:
        total_points[user.pk] = 0

    for match in matches:
        match_score_guess = {}
        match_score_guess['match'] = match

        mt = match.time
        match_score_guess['enabled'] = (localtime(mt) < now)

        for user in users:
            data = {}
            data['user']=user
            data['victory_point']=0
            data['difference_point']=0
            data['exact_score_point']=0

            ug = None
            for mg in guesses:
                if ((mg.guesser != user) or (mg.match != match)):
                    continue
                ug = mg
                break
            data['guess']=ug

            if (ug):
                if ((match.score_1 == None) or (match.score_2 == None) or (ug.guess_score_1 == None) or (ug.guess_score_2 == None)):
                    data['victory_point']=0
                    data['difference_point']=0
                    data['exact_score_point']=0
                else:
                    if (((match.score_1 > match.score_2) and (ug.guess_score_1 > ug.guess_score_2)) or
                        ((match.score_1 < match.score_2) and (ug.guess_score_1 < ug.guess_score_2)) or
                        ((match.score_1 == match.score_2) and (ug.guess_score_1 == ug.guess_score_2))):
                        data['victory_point']=1

                        if (match.score_1 > match.score_2):
                            if ((match.score_1 - match.score_2) == (ug.guess_score_1 - ug.guess_score_2)):
                                data['difference_point']=1
                        else:
                            if ((match.score_2 - match.score_1) == (ug.guess_score_2 - ug.guess_score_1)):
                                data['difference_point']=1

                        if ((match.score_1 == ug.guess_score_1) and (match.score_2 == ug.guess_score_2)):
                            data['exact_score_point']=1

            total_points[user.pk] += data['victory_point'] + data['difference_point'] + data['exact_score_point']
            data['total_point'] = total_points[user.pk]
            match_score_guess[user.pk] = data

        match_score_guesses.append(match_score_guess)

    chart_data = []
    for user in users:
        chart_element = {}
        chart_element['user']=user
        data=[]

        for msg in match_score_guesses:
            data_element = {}
            if (not msg['enabled']):
                continue

            ug = msg[user.pk]

            data_element['score'] = ug['total_point']
            try:
                data_element['prediction'] = str(ug['guess'].guess_score_1) + " - " + str(ug['guess'].guess_score_2)
            except:
                data_element['prediction'] = u'отсутствует'

            data_element['match'] = msg['match'].command_1.name + " - " + msg['match'].command_2.name

            if (msg['match'].penalty_score_1 != None):
                if (msg['match'].extra_score_1 != None):
                    data_element['match_score'] = str(msg['match'].score_1) + " - " + str(msg['match'].score_2) + u', ДВ ' + str(msg['match'].extra_score_1) + " - " + str(msg['match'].extra_score_2) + u', пен. ' + str(msg['match'].penalty_score_1) + " - " + str(msg['match'].penalty_score_2)
                else:
                    data_element['match_score'] = str(msg['match'].score_1) + " - " + str(msg['match'].score_2) + u', пен. ' + str(msg['match'].penalty_score_1) + " - " + str(msg['match'].penalty_score_2)
            else:
                if (msg['match'].extra_score_1 != None):
                    data_element['match_score'] = str(msg['match'].score_1) + " - " + str(msg['match'].score_2) + u', ДВ ' + str(msg['match'].extra_score_1) + " - " + str(msg['match'].extra_score_2)
                else:
                    data_element['match_score'] = str(msg['match'].score_1) + " - " + str(msg['match'].score_2)

            data_element['earned_points'] = ug['victory_point'] + ug['difference_point'] + ug['exact_score_point']
            data.append(data_element)

        chart_element['user']={ 'first_name': user.first_name, 'last_name' : user.last_name, 'money' : user.player.money }
        chart_element['data']=data
        chart_data.append(chart_element)

    return HttpResponse(json.dumps({'chart_data' : chart_data}))

def tournament(request):
    commands = Command.objects.all()
    matches = Match.objects.all()

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
        command_group_matches = group_matches.filter(Q(command_1=command) | Q(command_2=command))
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

    return render(request, 'tournament.html', {'group_tables' : group_tables})
