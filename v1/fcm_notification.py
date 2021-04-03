from firebase_admin import messaging


def send_to_firebase_cloud_messaging(
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
                'notification_transaction_price': transaction_price
            },
            tokens=registration_tokens,
        )
        messaging.send_multicast(message)
    except Exception as e:
        print(e)
