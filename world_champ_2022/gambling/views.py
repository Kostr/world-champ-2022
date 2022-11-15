# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse

from .models import Match, MatchGuess, Command
import datetime
from django.utils import timezone
from django.utils.timezone import localtime


def score_for_guess(user, match):
	data = {}
	data['user']=user
	data['victory_point']=0
	data['difference_point']=0
	data['exact_score_point']=0
	try:
		ug = MatchGuess.objects.all().filter(guesser=user).filter(match=match)[0]
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

	except Exception as e:
		#print str(e)
		data['guess']=None

	data['total_point'] = data['victory_point'] + data['difference_point'] + data['exact_score_point']
	print(data)
	return data


def gambling_list(request):
	matches = Match.objects.all().order_by("time")

	anchor = ''
	now = localtime(timezone.now())

	error=''

	if request.POST:
		for match in matches:
			if (('action_' + str(match.id)) in request.POST) :
				mt = match.time
				if (localtime(mt) < now):
					error = u"Время начала матча прошло, ставку изменить невозможно!"
					break;

				try:
					mg = MatchGuess.objects.all().filter(match = match).filter(guesser = request.user)[0]
					# alter
					mg.guess_score_1 = request.POST['result1']
					mg.guess_score_2 = request.POST['result2']
					mg.save()
				except Exception as e:
					#print str(e)
					# create
					mg = MatchGuess.objects.create(
							guesser = request.user,
							match = match,
							guess_score_1 = request.POST['result1'],
							guess_score_2 = request.POST['result2'],
							)
					pass
				anchor = 'mg_' + str(match.id)

	#now = datetime.datetime.now()
	#now = utc=pytz.UTC
	#now = timezone.now()

	match_info_guesses = []
	past_match_info_guesses = []
	for match in matches:
		match_info_guess={}
		match_info_guess['match'] = match
		try:
			mg = MatchGuess.objects.all().filter(match = match).filter(guesser = request.user)[0]
			match_info_guess['guess'] = mg
		except:
			match_info_guess['guess'] = None

		mt = match.time
		match_info_guess['enabled'] = (localtime(mt) > now)

		if (match.stage == Match.MATCH_CLASS_GROUP):
			match_info_guess['stage'] = u"Групповой этап. Группа " + match.command_1.group
		else:
			match_info_guess['stage'] = "?"
			for match_class_tuple in Match.MATCH_CLASSES:
				if match_class_tuple[0] == match.stage:
					match_info_guess['stage'] = match_class_tuple[1]

		mt = match.time
		if (localtime(mt) < now):
			match_info_guess['plus_score'] = score_for_guess(request.user, match)['total_point']
			past_match_info_guesses.append(match_info_guess)
		else:
			match_info_guesses.append(match_info_guess)

	score_choices = [0,1,2,3,4,5,6,7,8,9]
	#match_guesses = MatchGuess.objects.all().filter(guesser = request.user).order_by('match__time')
	return render(request, 'gambling/gambling_list.html', {'past_match_info_guesses': past_match_info_guesses, 'match_info_guesses' : match_info_guesses, 'score_choices' : score_choices, 'anchor' : anchor, 'error' : error})
	#return HttpResponse(u"Данное устройство уже внесено в таблицу!")
