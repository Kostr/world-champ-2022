from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import localtime
import datetime

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
            users = User.objects.filter(player__nicevt=True)
        else:
            users = User.objects.all()
    except:
        users = User.objects.all()
    return users

def stats(request):
    users = get_players(request)
    matches = Match.objects.all()

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
                ug = MatchGuess.objects.filter(guesser=user).filter(match=match)[0]

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
        data['user'] = user
        data['winner'] = uscores[user]['winner']
        data['difference'] = uscores[user]['difference']
        data['correct'] = uscores[user]['correct']
        data['missed'] = uscores[user]['missed']
        data['incorrect'] = uscores[user]['incorrect']
        us_list.append(data)

    return render(request, 'stats.html', {'users' : users, 'us_list' : us_list})

def news(request):
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
    yesterday = timezone.make_aware(datetime.datetime.today() - datetime.timedelta(days=1), timezone.get_default_timezone())

    matches = Match.objects.filter(time__lte=now, time__gt=yesterday)

    users = get_players(request)

    mgp = []
    for match in matches:
        data={}
        data['match']=match
        usgp=[]
        for user in users:
            usgp_data={}
            usgp_data['user']=user
            try:
                ug = MatchGuess.objects.filter(guesser=user).filter(match=match)[0]

                usgp_data['guess']= ug
                usgp_data['score']=0

                if ((match.score_1 == None) or (match.score_2 == None) or (ug.guess_score_1 == None) or (ug.guess_score_2 == None)):
                    usgp_data['score']=0
                else:
                    if (((match.score_1 > match.score_2) and (ug.guess_score_1 > ug.guess_score_2)) or
                        ((match.score_1 < match.score_2) and (ug.guess_score_1 < ug.guess_score_2)) or
                        ((match.score_1 == match.score_2) and (ug.guess_score_1 == ug.guess_score_2))):
                        usgp_data['score']+=1

                        if (match.score_1 > match.score_2):
                            if ((match.score_1 - match.score_2) == (ug.guess_score_1 - ug.guess_score_2)):
                                usgp_data['score']+=1
                        else:
                            if ((match.score_2 - match.score_1) == (ug.guess_score_2 - ug.guess_score_1)):
                                usgp_data['score']+=1

                        if ((match.score_1 == ug.guess_score_1) and (match.score_2 == ug.guess_score_2)):
                            usgp_data['score']+=1

            except:
                usgp_data['guess']= None
                usgp_data['score']=0

            usgp.append(usgp_data)
        data['user_guesses']=usgp
        mgp.append(data)

    total_scores_before={}
    for user in users:
        total_scores_before[user] = 0

    matches = Match.objects.filter(time__lte=yesterday)
    for match in matches:
        for user in users:
            try:
                ug = MatchGuess.objects.filter(guesser=user).filter(match=match)[0]
                
                if ((match.score_1 == None) or (match.score_2 == None) or (ug.guess_score_1 == None) or (ug.guess_score_2 == None)):
                    pass
                else:
                    if (((match.score_1 > match.score_2) and (ug.guess_score_1 > ug.guess_score_2)) or
                        ((match.score_1 < match.score_2) and (ug.guess_score_1 < ug.guess_score_2)) or
                        ((match.score_1 == match.score_2) and (ug.guess_score_1 == ug.guess_score_2))):
                        total_scores_before[user]+=1

                        if (match.score_1 > match.score_2):
                            if ((match.score_1 - match.score_2) == (ug.guess_score_1 - ug.guess_score_2)):
                                total_scores_before[user]+=1
                        else:
                            if ((match.score_2 - match.score_1) == (ug.guess_score_2 - ug.guess_score_1)):
                                total_scores_before[user]+=1

                        if ((match.score_1 == ug.guess_score_1) and (match.score_2 == ug.guess_score_2)):
                            total_scores_before[user]+=1
            except:
                pass

    total_scores_after={}
    for user in users:
        total_scores_after[user] = 0

    matches = Match.objects.filter(time__lte=now)
    for match in matches:
        for user in users:
            try:
                ug = MatchGuess.objects.filter(guesser=user).filter(match=match)[0]

                if ((match.score_1 == None) or (match.score_2 == None) or (ug.guess_score_1 == None) or (ug.guess_score_2 == None)):
                    pass
                else:
                    if (((match.score_1 > match.score_2) and (ug.guess_score_1 > ug.guess_score_2)) or
                        ((match.score_1 < match.score_2) and (ug.guess_score_1 < ug.guess_score_2)) or
                        ((match.score_1 == match.score_2) and (ug.guess_score_1 == ug.guess_score_2))):
                        total_scores_after[user]+=1

                        if (match.score_1 > match.score_2):
                            if ((match.score_1 - match.score_2) == (ug.guess_score_1 - ug.guess_score_2)):
                                total_scores_after[user]+=1
                        else:
                            if ((match.score_2 - match.score_1) == (ug.guess_score_2 - ug.guess_score_1)):
                                total_scores_after[user]+=1

                        if ((match.score_1 == ug.guess_score_1) and (match.score_2 == ug.guess_score_2)):
                            total_scores_after[user]+=1
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
    users = get_players(request)
    matches = Match.objects.all().order_by('time')
    guesses = MatchGuess.objects.all()
    match_score_guesses = []

    now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

    for match in matches:
        match_score_guess = {}
        match_score_guess['match'] = match

        mt = match.time
        match_score_guess['enabled'] = (localtime(mt) < now)

        user_guesses = []
        for user in users:
            data = {}
            data['user']=user
            data['victory_point']=0
            data['difference_point']=0
            data['exact_score_point']=0
            try:
                ug = guesses.filter(guesser=user).filter(match=match)[0]
                data['guess']=ug
                
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

            except:
                data['guess']=None

            data['total_point'] = data['victory_point'] + data['difference_point'] + data['exact_score_point']

            for msg in match_score_guesses:
                for usg in msg['user_guesses']:
                    try:
                        if (usg['guess'].guesser == user):
                            data['total_point'] += usg['victory_point']
                            data['total_point'] += usg['difference_point']
                            data['total_point'] += usg['exact_score_point']
                    except:
                        pass
                        

            user_guesses.append(data)

        match_score_guess['user_guesses'] = user_guesses
        match_score_guesses.append(match_score_guess)

    chart_data = []
    for user in users:
        chart_element = {}
        chart_element['user']=user
        data=[]

        for msg in match_score_guesses:
            data_element = {}
            mt = msg['match'].time
            if (localtime(mt) > now):
                continue

            for ug in msg['user_guesses']:
                if (ug['user']==user):
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

        chart_element['data']=data
        chart_data.append(chart_element)

    return render(request, 'charts.html', {'match_score_guesses' : match_score_guesses, 'users' : users, 'chart_data' : chart_data})

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
