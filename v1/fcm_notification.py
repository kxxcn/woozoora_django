from firebase_admin import messaging


def send_message_when_registered_account_book(
        registration_tokens,
        channel,
        title,
        body,
        date,
        user_name,
        user_profile,
        transaction_id,
        transaction_name,
        transaction_date,
        transaction_price,
        transaction_type,
):
    try:
        message = messaging.MulticastMessage(
            data={
                'notification_channel': channel,
                'notification_title': title,
                'notification_body': body,
                'notification_date': date,
                'notification_user_name': user_name,
                'notification_user_profile': user_profile,
                'notification_transaction_id': transaction_id,
                'notification_transaction_name': transaction_name,
                'notification_transaction_date': transaction_date,
                'notification_transaction_price': transaction_price,
                'notification_transaction_type': transaction_type
            },
            tokens=registration_tokens,
        )
        messaging.send_multicast(message)
    except Exception as e:
        print(e)


def send_message_when_invite_successful(
        registration_tokens,
        channel,
        user_name
):
    try:
        title = '\uD83D\uDE04 {}님이 초대를 수락했습니다. \uD83D\uDE4B'.format(user_name)
        body = '함께 가계부를 작성하고 지출을 관리하세요.'
        message = messaging.MulticastMessage(
            data={
                'notification_channel': channel,
                'notification_title': title,
                'notification_body': body
            },
            tokens=registration_tokens,
        )
        messaging.send_multicast(message)
    except Exception as e:
        print(e)


def send_message_when_join_group(
        registration_tokens,
        channel,
        user_name
):
    try:
        title = '\uD83D\uDE04 {}님이 그룹에 참여했습니다. \uD83D\uDE4B'.format(user_name)
        body = '함께 가계부를 작성하고 지출을 관리하세요.'
        message = messaging.MulticastMessage(
            data={
                'notification_channel': channel,
                'notification_title': title,
                'notification_body': body
            },
            tokens=registration_tokens,
        )
        messaging.send_multicast(message)
    except Exception as e:
        print(e)
