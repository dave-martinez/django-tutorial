from allauth.account.decorators import verified_email_required
from django.contrib import messages
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    paginate_by = 10

    def get_queryset(self):
        return Question.objects.all().order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = [
            {'label': 'Published', 'value': Question.objects.filter(
                pub_date__lte=timezone.now()).count()},
            {'label': 'Total questions',
                'value': context['latest_question_list'].count()},
        ]
        return context

    @ method_decorator(verified_email_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, *args, **kwargs):
        if self.get_object().pub_date > timezone.now():
            messages.error(request, "This poll is not available yet.")
            return redirect('polls:index')
        return super().get(request, *args, **kwargs)

    @method_decorator(verified_email_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice."
        })
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(
            reverse('polls:results', args=(question.id,))
        )
