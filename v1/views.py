import calendar
import json
import time
from datetime import datetime, date, timedelta
from distutils.util import strtobool

from django.http import HttpResponse, HttpResponseNotModified, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .fcm_notification import send_message_when_registered_account_book, send_message_when_invite_successful, \
    send_message_when_join_group
from .models import User, Transaction, Ask, Notice
from .serializer import UserSerializer, TransactionSerializer, NoticeSerializer, AskSerializer
from .slack_message import send_to_slack_message


def index(request):
    return render(request, 'index.html')


def personal(request):
    return render(request, 'personal.html')


def dashboard(request):
    total_users = User.objects.all().count()

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    last_day_of_current_month = calendar.monthrange(current_year, current_month)[1]

    start_of_month = datetime(current_year, current_month, 1)
    end_of_month = datetime(current_year, current_month, last_day_of_current_month, 23, 59, 59)

    start_of_month_ms = start_of_month.timestamp() * 1000
    end_of_month_ms = end_of_month.timestamp() * 1000

    monthly_of_users = User.objects.filter(date__range=(start_of_month_ms, end_of_month_ms)).count()

    start_of_day = datetime(current_year, current_month, current_day)
    end_of_day = datetime(current_year, current_month, current_day, 23, 59, 59)

    start_of_day_ms = start_of_day.timestamp() * 1000
    end_of_day_ms = end_of_day.timestamp() * 1000

    daily_of_users = User.objects.filter(date__range=(start_of_day_ms, end_of_day_ms)).count()

    monthly_of_transactions = Transaction.objects.filter(date__range=(start_of_month_ms, end_of_month_ms)).count()

    daily_of_transactions = Transaction.objects.filter(date__range=(start_of_day_ms, end_of_day_ms)).count()

    incoming_users_of_monthly = []

    for month in range(1, 13):
        start_ms = datetime(current_year, month, 1).timestamp() * 1000
        last_day = calendar.monthrange(current_year, month)[1]
        end_ms = datetime(current_year, month, last_day).timestamp() * 1000
        users = User.objects.filter(date__range=(start_ms, end_ms)).count()
        incoming_users_of_monthly.append(users)

    today = date.today()
    month_ago = today.replace(day=1) - timedelta(days=1)
    last_day_of_month_ago = calendar.monthrange(month_ago.year, month_ago.month)[1]
    start_of_month_ago_ms = datetime(month_ago.year, month_ago.month, 1).timestamp() * 1000
    end_of_month_ago_ms = datetime(month_ago.year, month_ago.month, last_day_of_month_ago).timestamp() * 1000

    prev_monthly_of_users = User.objects.filter(date__range=(start_of_month_ago_ms, end_of_month_ago_ms)).count()

    today = date.today()
    yesterday = today - timedelta(days=1)

    start_of_yesterday_ms = datetime(yesterday.year, yesterday.month, yesterday.day).timestamp() * 1000
    end_of_yesterday_ms = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59).timestamp() * 1000

    if prev_monthly_of_users == 0:
        user_variance_of_monthly = monthly_of_users * 100
    else:
        user_variance_of_monthly = (monthly_of_users - prev_monthly_of_users) / prev_monthly_of_users * 100

    prev_daily_of_users = User.objects.filter(date__range=(start_of_yesterday_ms, end_of_yesterday_ms)).count()

    if prev_daily_of_users == 0:
        user_variance_of_daily = daily_of_users * 100
    else:
        user_variance_of_daily = (daily_of_users - prev_daily_of_users) / prev_daily_of_users * 100

    prev_monthly_of_transactions = Transaction.objects \
        .filter(date__range=(start_of_month_ago_ms, end_of_month_ago_ms)) \
        .count()

    if prev_monthly_of_transactions == 0:
        transaction_variance_of_monthly = monthly_of_transactions * 100
    else:
        transaction_variance_of_monthly = (
                                                  monthly_of_transactions - prev_monthly_of_transactions) / prev_monthly_of_transactions * 100

    prev_daily_of_transactions = Transaction.objects \
        .filter(date__range=(start_of_yesterday_ms, end_of_yesterday_ms)) \
        .count()

    if prev_daily_of_transactions == 0:
        transaction_variance_of_daily = daily_of_transactions * 100
    else:
        transaction_variance_of_daily = (
                                                daily_of_transactions - prev_daily_of_transactions) / prev_daily_of_transactions * 100

    context = {
        'total_users': total_users,
        'monthly_of_users': monthly_of_users,
        'daily_of_users': daily_of_users,
        'monthly_of_transactions': monthly_of_transactions,
        'daily_of_transactions': daily_of_transactions,
        'incoming_users': incoming_users_of_monthly,
        'user_variance_of_monthly': round(user_variance_of_monthly, 1),
        'user_variance_of_daily': round(user_variance_of_daily, 1),
        'transaction_variance_of_monthly': round(transaction_variance_of_monthly, 1),
        'transaction_variance_of_daily': round(transaction_variance_of_daily, 1)
    }
    return render(request, 'dashboard.html', context=context)


def source(request):
    return render(request, 'source.html')


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def users(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            return HttpResponse(status=204)
    elif request.method == 'POST':
        try:
            exclude = request.POST.get('exclude')
            user = User.objects.get(id=user_id)

            if strtobool(exclude):
                group = User.objects.filter(code=user.code).exclude(id=user_id)
            else:
                group = User.objects.filter(code=user.code)

            serializer = UserSerializer(group, many=True)
            return Response(serializer.data)
        except Exception as e:
            return HttpResponse(status=204)


def token(request, user_id):
    if request.method == 'POST':
        try:
            new_token = request.POST.get('token', None)
            user = User.objects.get(id=user_id)
            user.token = new_token
            user.save()
            return HttpResponse()
        except Exception as e:
            return HttpResponse(status=204)


def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            t_code = data['code']

            if 'sponsor' in t_code:
                t_code = User.objects.get(id=t_code.split('_')[1]).code

            User(
                id=data['id'],
                name=data['name'],
                email=data['email'],
                profile=data['profile'],
                code=t_code,
                token=data['token'],
                budget=data['budget'],
                date=data['date'],
                year=data['year'],
                type=data['type']
            ).save()

            groups = User.objects.filter(code=t_code).exclude(id=data['id'])
            tokens = list(map(lambda u: u.token, groups))

            send_message_when_invite_successful(tokens, "channel_default", data['name'])

            return HttpResponse(t_code)
        except Exception as e:
            return HttpResponseNotModified()


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def transactions(request, user_id):
    if request.method == 'GET':
        try:
            start_date = request.GET.get('startDate')
            end_date = request.GET.get('endDate')

            user = User.objects.get(id=user_id)

            transaction_list = Transaction.objects.filter(
                code=user.code,
                date__gte=start_date,
                date__lte=end_date
            )

            serializer = TransactionSerializer(transaction_list, many=True)
            return Response(serializer.data)
        except Exception as e:
            return HttpResponse(status=204)


@api_view(['POST', 'PUT'])
@permission_classes((permissions.AllowAny,))
def code(request, user_id):
    if request.method == 'POST':
        try:
            sponsor_id = request.POST.get('sponsor_id', None)
            transfer = request.POST.get('transfer', None)

            new_code = User.objects.get(id=sponsor_id).code

            user = User.objects.get(id=user_id)

            if strtobool(transfer):
                for t in Transaction.objects.filter(user_id=user_id, code=user.code):
                    t.code = new_code
                    t.save()

            user.code = new_code
            user.save()

            groups = User.objects.filter(code=new_code).exclude(id=user_id)
            tokens = list(map(lambda u: u.token, groups))

            send_message_when_invite_successful(tokens, "channel_default", user.name)

            return HttpResponse(new_code)
        except Exception as e:
            return HttpResponseNotModified()
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)

            new_code = data['code']
            transfer = data['transfer']

            user = User.objects.get(id=user_id)
            others = User.objects.filter(code=new_code)

            if new_code != user.code and others.count() != 0:
                if transfer:
                    for t in Transaction.objects.filter(user_id=user_id, code=user.code):
                        t.code = new_code
                        t.save()

                    user.code = new_code
                user.save()

                groups = User.objects.filter(code=new_code).exclude(id=user_id)
                tokens = list(map(lambda u: u.token, groups))

                send_message_when_join_group(tokens, "channel_default", user.name)

                return HttpResponse(new_code)
            else:
                return HttpResponseNotModified()
        except Exception as e:
            return HttpResponseNotModified()


def year(request, user_id):
    if request.method == 'POST':
        try:
            new_year = request.POST.get('year', None)

            user = User.objects.get(id=user_id)

            user.year = new_year
            user.save()

            return HttpResponse()
        except Exception as e:
            return HttpResponseNotModified()


def budget(request, user_id):
    if request.method == 'POST':
        try:
            new_budget = request.POST.get('budget', None)

            user = User.objects.get(id=user_id)

            user.budget = new_budget
            user.save()

            return HttpResponse()
        except Exception as e:
            return HttpResponseNotModified()


def transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filtered_list = Transaction.objects.filter(id=data['id'])

            is_new_transaction = filtered_list.count() == 0

            user_id = data['user_id']
            user = User.objects.get(id=user_id)

            t_category = data['category']

            try:
                t_type = data['type']
                t_domain = data['domain']
            except:
                t_type = 0
                if t_category == 0:
                    t_domain = '식비'
                elif t_category == 1:
                    t_domain = '교통/차량'
                elif t_category == 2:
                    t_domain = '문화생활'
                elif t_category == 3:
                    t_domain = '마트/편의점'
                elif t_category == 4:
                    t_domain = '패션/미용'
                elif t_category == 5:
                    t_domain = '생활용품'
                elif t_category == 6:
                    t_domain = '주거/통신'
                elif t_category == 7:
                    t_domain = '건강'
                elif t_category == 8:
                    t_domain = '교육'
                elif t_category == 9:
                    t_domain = '경조사/회비'
                elif t_category == 10:
                    t_domain = '부모님'
                elif t_category == 11:
                    t_domain = '기타'
                elif t_category == 12:
                    t_domain = '카페'
                elif t_category == 13:
                    t_domain = '육아'
                elif t_category == 14:
                    t_domain = '의료'
                elif t_category == 15:
                    t_domain = '대출'
                else:
                    t_domain = '보험'

            if is_new_transaction:
                new_transaction = Transaction(
                    user_id=user_id,
                    code=user.code,
                    category=t_category,
                    name=data['name'],
                    domain=t_domain,
                    description=data['description'],
                    price=data['price'],
                    date=data['date'],
                    payment=data['payment'],
                    type=t_type
                )
                new_transaction.save()
            else:
                new_transaction = None
                filtered_list.update(
                    category=data['category'],
                    name=data['name'],
                    domain=t_domain,
                    description=data['description'],
                    price=data['price'],
                    date=data['date'],
                    payment=data['payment']
                )

            if is_new_transaction:
                price = data['price']
                formatted_price = f'{price:,}'
                date = datetime.fromtimestamp(data['date'] / 1000)
                user_id = data['user_id']
                user = User.objects.get(id=user_id)
                groups = User.objects.filter(code=data['code']).exclude(id=user_id)
                tokens = list(map(lambda u: u.token, groups))

                if t_type == 0:
                    t_title = "소비"
                else:
                    t_title = "수입"

                title = '{} {}원 {}'.format(
                    t_title,
                    formatted_price,
                    data['name']
                )

                weekdays = ['월', '화', '수', '목', '금', '토', '일']
                body = '{}/{}({}) {}님이 가계부를 등록했어요. '.format(
                    date.month,
                    date.day,
                    weekdays[date.weekday()],
                    user.name
                )

                send_message_when_registered_account_book(
                    tokens,
                    'channel_registration',
                    title,
                    body,
                    str(round(time.time() * 1000)),
                    user.name,
                    user.profile,
                    str(new_transaction.id),
                    data['name'],
                    str(data['date']),
                    str(data['price']),
                    str(t_type)
                )
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseNotModified()
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            Transaction.objects.filter(id=data['id']).delete()
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseNotModified()


def ask(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=user_id)

            Ask(
                user_id=user_id,
                message=data['message'],
                device=data['device'],
                os=data['os'],
                version=data['version'],
                date=data['date']
            ).save()

            user_info = '*사용자 정보*'
            id = '>:star: 아이디: {}'.format(user.id)
            email = '>:email: 이메일: {}'.format(user.email)
            name = '>:slightly_smiling_face: 이름: {}'.format(user.name)
            code = '>:lock: 코드: {}'.format(user.code)
            token = '>:key: 토큰: {}'.format(user.token)
            budget = '>:moneybag: 예산: {}원'.format(f'{user.budget:,}')

            if user.type == 0:
                sign_in = '카카오'
            else:
                sign_in = '구글'
            type = '>:eyes: 로그인: {}'.format(sign_in)

            timestamp = datetime.fromtimestamp(user.date / 1000)
            date = '>:wave: 가입일: {}.{}.{}'.format(timestamp.year, timestamp.month, timestamp.day)

            device_info = '*디바이스 정보*'
            device = '>:white_circle: 디바이스: {}'.format(data['device'])
            os = '>:large_blue_circle: OS 버전: {}'.format(data['os'])
            version = '>:red_circle: 앱 버전: {}'.format(data['version'])

            message = [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '*[우주라이트 문의사항]*\n{}'.format(data['message'])
                    }
                },
                {
                    'type': 'divider'
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(
                            user_info,
                            id,
                            email,
                            name,
                            code,
                            token,
                            budget,
                            type,
                            date
                        )
                    }
                },
                {
                    'type': 'divider'
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '{}\n{}\n{}\n{}'.format(
                            device_info,
                            device,
                            os,
                            version
                        )
                    }
                },
            ]
            send_to_slack_message(message)
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseNotModified()


def leave(request, user_id):
    if request.method == 'POST':
        try:
            User.objects.filter(id=user_id).delete()
            Transaction.objects.filter(user_id=user_id).delete()
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseNotModified()


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def notice(request):
    if request.method == 'GET':
        try:
            notices = Notice.objects.all()
            serializer = NoticeSerializer(notices, many=True)
            return Response(serializer.data)
        except Exception as e:
            return HttpResponseNotFound()


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def reply(request):
    if request.method == 'GET':
        try:
            asks = Ask.objects.all()
            serializer = AskSerializer(asks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return HttpResponseNotFound()
