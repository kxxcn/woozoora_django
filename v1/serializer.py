from rest_framework import serializers

from .models import User, Transaction, Notice, Ask, Reply


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = '__all__'


class AskSerializer(serializers.ModelSerializer):
    reply = serializers.SerializerMethodField()

    @staticmethod
    def get_reply(obj):
        try:
            reply = Reply.objects.get(ask_id=obj.id)
            serializer = ReplySerializer(reply)
            return serializer.data
        except Exception as e:
            print(e)
            return None

    class Meta:
        model = Ask
        fields = '__all__'
