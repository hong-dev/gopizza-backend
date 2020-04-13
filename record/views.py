import json
import pandas as pd

from .models      import Score, Pizza
from user.models  import User
from store.models import Store

from datetime              import datetime, timedelta, date
from django.views          import View
from django.http           import HttpResponse, JsonResponse
from django.db.models      import Sum, Avg, Min, Count
from sklearn.preprocessing import MinMaxScaler

class PizzaView(View):
    def get(self, request):
        return JsonResponse({"pizza" : list(Pizza.objects.values())}, status = 200)

class ScoreView(View):
    def post(self, request):
        try:
            score_data = json.loads(request.body)
            Score.objects.create(
                order_number = score_data["order_number"],
                user         = User.objects.get(id = score_data["user_id"]),
                store        = Store.objects.get(name = score_data["store"]),
                pizza        = Pizza.objects.get(id = score_data["score"]["pizza_id"]),
                time         = score_data["score"]["time"],
                quality      = score_data["score"]["quality"],
                sauce        = score_data["score"]["sauce"],
                cheese       = score_data["score"]["cheese"],
                topping      = score_data["score"]["topping"]
            )
            return HttpResponse(status = 200)

        except User.DoesNotExist:
            return JsonResponse({"message" : "USER_DOES_NOT_EXIST"}, status = 400)

        except Store.DoesNotExist:
            return JsonResponse({"message" : "STORE_DOES_NOT_EXIST"}, status = 400)

        except Pizza.DoesNotExist:
            return JsonResponse({"message" : "PIZZA_DOES_NOT_EXIST"}, status = 400)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status = 400)

def get_user_list(pizza_id, time_delta):
    ranking_list = (
        User
        .objects
        .filter(**get_filter_condition(pizza_id, time_delta))
        .select_related('store')
        .prefetch_related('score_set')
        .annotate(
            total_count      = Count('score'),
            average_time     = Avg('score__time'),
            shortest_time    = Min('score__time'),
            average_quality  = Avg('score__quality'),
            average_sauce    = Avg('score__sauce'),
            average_cheese   = Avg('score__cheese'),
            average_topping  = Avg('score__topping'),
            completion_score = sum(
                [
                    Avg('score__quality'),
                    Avg('score__sauce'),
                    Avg('score__cheese'),
                    Avg('score__topping')
                ]
            )
        )
    )

    return ranking_list

def get_store_list(pizza_id, time_delta):
    ranking_list = (
        Store
        .objects
        .filter(**get_filter_condition(pizza_id, time_delta))
        .prefetch_related('user_set')
        .annotate(
            total_count      = Count('score'),
            average_time     = Avg('score__time'),
            shortest_time    = Min('score__time'),
            average_quality  = Avg('score__quality'),
            average_sauce    = Avg('score__sauce'),
            average_cheese   = Avg('score__cheese'),
            average_topping  = Avg('score__topping'),
            completion_score = sum(
                [
                    Avg('score__quality'),
                    Avg('score__sauce'),
                    Avg('score__cheese'),
                    Avg('score__topping')
                ]
            )
        )
    )

    return ranking_list

def get_filter_condition(pizza_id, time_delta):
    filter_condition = {}

    if time_delta:
        start_date = date.today() - timedelta(days = int(time_delta))
    else:
        start_date = Score.objects.earliest('created_at').created_at.date()

    filter_condition["score__created_at__range"] = (start_date, datetime.now())

    if pizza_id:
        filter_condition["score__pizza_id"] = pizza_id

    return filter_condition

def get_ranking(ranking_list, order_by):
    completion_importance, time_importance, count_importance = 50, 30, 20

    scores = pd.DataFrame({
        "completion_standard" : [rank.completion_score for rank in ranking_list],
        "time_standard"       : [-rank.average_time for rank in ranking_list],
        "count_standard"      : [rank.total_count for rank in ranking_list],
    })

    scores[ : ] = MinMaxScaler().fit_transform(scores[ : ]) * 100

    total_score = (
        scores.completion_standard * completion_importance
        + scores.time_standard * time_importance
        + scores.count_standard * count_importance
    )

    user_pd = pd.DataFrame(ranking_list.values())

    rank_table = user_pd.join(scores)

    rank_table['total_score'] = total_score

    ascending = (
        True
        if order_by == 'average_time' or order_by == 'shortest_time'
        else False
    )

    ordered_table = rank_table.sort_values(order_by, ascending = ascending)

    ordered_table['total_score_rank']      = ordered_table['total_score'].rank(ascending = False, method = 'min')
    ordered_table['total_count_rank']      = ordered_table['total_count'].rank(ascending = False, method = 'min')
    ordered_table['completion_score_rank'] = ordered_table['completion_score'].rank(ascending = False, method = 'min')
    ordered_table['average_time_rank']     = ordered_table['average_time'].rank(ascending = True, method = 'min')
    ordered_table['shortest_time_rank']    = ordered_table['shortest_time'].rank(ascending = True, method = 'min')

    return ordered_table

class UserRankView(View):
    def get(self, request):
        limit      = request.GET.get('limit', User.objects.count())
        pizza_id   = request.GET.get('pizza_id')
        order_by   = request.GET.get('order_by', 'total_score')
        time_delta = request.GET.get('time_delta')

        ranking_list = get_user_list(pizza_id, time_delta)

        if len(ranking_list) == 0:
            return JsonResponse({"message" : "RANKING_DOES_NOT_EXIST"}, status = 400)

        ordered_table = get_ranking(ranking_list, order_by)[:int(limit)]

        user_ranking = [
            {
                "id"               : user.id,
                "name"             : user.name,
                "image"            : user.image,
                "store_id"         : user.store_id,
                "store_name"       : user.store.name,
                "count"            : user.total_count,
                "average_time"     : round(user.average_time, 2),
                "shortest_time"    : user.shortest_time,
                "quality"          : round(user.average_quality),
                "sauce"            : round(user.average_sauce),
                "cheese"           : round(user.average_cheese),
                "topping"          : round(user.average_topping),
                "completion_score" : round(user.completion_score),
                "total_score"      : round(float(ordered_table[ordered_table['id'] == user.id]['total_score'])),
                "rank"             : round(float(ordered_table[ordered_table['id'] == user.id][f"{order_by}_rank"]))
            } for id_number in ordered_table['id'] if (user := ranking_list.get(id = id_number))]

        return JsonResponse({"ranking" : user_ranking}, status = 200)

class StoreRankView(View):
    def get(self, request):
        limit      = request.GET.get('limit', Store.objects.count())
        pizza_id   = request.GET.get('pizza_id')
        order_by   = request.GET.get('order_by', 'total_score')
        time_delta = request.GET.get('time_delta')

        ranking_list = get_store_list(pizza_id, time_delta)

        if len(ranking_list) == 0:
            return JsonResponse({"message" : "RANKING_DOES_NOT_EXIST"}, status = 400)

        ordered_table = get_ranking(ranking_list, order_by)[:int(limit)]

        store_ranking = [
            {
                "id"               : store.id,
                "name"             : store.name,
                "count"            : store.total_count,
                "average_time"     : round(store.average_time, 2),
                "shortest_time"    : store.shortest_time,
                "quality"          : round(store.average_quality),
                "sauce"            : round(store.average_sauce),
                "cheese"           : round(store.average_cheese),
                "topping"          : round(store.average_topping),
                "completion_score" : round(store.completion_score),
                "total_score"      : round(float(ordered_table[ordered_table['id'] == store.id]['total_score'])),
                "rank"             : round(float(ordered_table[ordered_table['id'] == store.id][f"{order_by}_rank"]))
            } for id_number in ordered_table['id'] if (store := ranking_list.get(id = id_number))]

        return JsonResponse({"ranking" : store_ranking}, status = 200)

class UserScoreView(View):
    def get(self, request, user_id):
        try:
            order_by   = request.GET.get('order_by', 'total_score')
            pizza_id   = request.GET.get('pizza_id')
            time_delta = request.GET.get('time_delta')

            ranking_list = get_user_list(pizza_id, time_delta)
            ordered_table = get_ranking(ranking_list, order_by)

            selected_user = ordered_table[ordered_table['id'] == user_id]

            user_info = selected_user[[
                'id',
                'name',
                'image',
                'store_id',
                'total_score',
                'total_count',
                'shortest_time',
                'average_time',
                'completion_score',
                'average_quality',
                'average_sauce',
                'average_cheese',
                'average_topping',
                'completion_standard',
                'time_standard',
                'count_standard',
                'total_score_rank',
                'total_count_rank',
                'completion_score_rank',
                'average_time_rank',
                'shortest_time_rank'
            ]].to_dict('records')[0]

            user_info['store_name'] = ranking_list.get(id = user_id).store.name

            return JsonResponse({"user_info" : user_info}, status = 200)

        except IndexError:
            return JsonResponse({"user_info" : list(User
                                                    .objects
                                                    .filter(id = user_id)
                                                    .values('id', 'image','store__name'))},
                                status = 200)

class StoreScoreView(View):
    def get(self, request, store_id):
        try:
            order_by   = request.GET.get('order_by', 'total_score')
            pizza_id   = request.GET.get('pizza_id')
            time_delta = request.GET.get('time_delta')

            ranking_list = get_store_list(pizza_id, time_delta)
            ordered_table = get_ranking(ranking_list, order_by)

            selected_store = ordered_table[ordered_table['id'] == store_id]

            store_info = selected_store[[
                'id',
                'name',
                'total_score',
                'total_count',
                'shortest_time',
                'average_time',
                'completion_score',
                'average_quality',
                'average_sauce',
                'average_cheese',
                'average_topping',
                'completion_standard',
                'time_standard',
                'count_standard',
                'total_score_rank',
                'total_count_rank',
                'completion_score_rank',
                'average_time_rank',
                'shortest_time_rank'
            ]].to_dict('records')[0]

            return JsonResponse({'store_info' : store_info}, status = 200)

        except IndexError:
            return JsonResponse({"message" : "SCORE_DOES_NOT_EXIST"}, status = 400)
