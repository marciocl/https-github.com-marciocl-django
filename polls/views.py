from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from .models import Choice, Question

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:10]
    return render(request, "polls/index.html", {"latest_question_list": latest_question_list})

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    total_votes = question.choices.aggregate(total=Sum('votes'))['total'] or 0

    choices_data = []
    for choice in question.choices.all():
        percentage = round((choice.votes / total_votes * 100), 1) if total_votes > 0 else 0
        choices_data.append({
            'text': choice.choice_text,
            'votes': choice.votes,
            'percentage': percentage,
        })

    return render(request, "polls/results.html", {
        "question": question,
        "choices_data": choices_data,
        "total_votes": total_votes,
    })

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choices.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Por favor, selecione uma opção válida para votar.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        messages.success(request, "O seu voto foi registado com sucesso!")
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))