import json
import time
from datetime import datetime
from distutils.util import strtobool

from django.http import HttpResponse, HttpResponseNotModified, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .fcm_notification import send_message_when_registered_account_book, send_message_when_invite_successful
from .models import User, Transaction, Notice, Ask
from .serializer import UserSerializer, TransactionSerializer, NoticeSerializer
from .slack_message import send_to_slack_message


def index(request):
    return render(request, 'index.html')


def personal(request):
    return render(request, 'personal.html')


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

            return HttpResponse(status=204)
        except Exception as e:
            print(e)
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

            if is_new_transaction:
                new_transaction = Transaction(
                    user_id=data['user_id'],
                    code=data['code'],
                    category=data['category'],
                    name=data['name'],
                    description=data['description'],
                    price=data['price'],
                    date=data['date'],
                    payment=data['payment']
                )
                new_transaction.save()
            else:
                new_transaction = None
                filtered_list.update(
                    category=data['category'],
                    name=data['name'],
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

                title = '지출 {}원 {}'.format(
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
                    str(data['price'])
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
                userId=user_id,
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
            Ask.objects.filter(userId=user_id).delete()
            return HttpResponse(status=204)
        except Exception as e:
            print(e)
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
