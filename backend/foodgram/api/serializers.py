from django.contrib.auth.hashers import check_password
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from api.utils import creating_an_ingredient
from recipes.models import (AmountOfIngredient, Favorite,
                            Ingredient, Recipe, ShoppingCart, Tag)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from users.models import User, Subscription


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return (self.context.get('request').user.is_authenticated
                and Subscription.objects.filter(
                    user=self.context.get('request').user,
                    author=obj
        ).exists())


class RecipeLittleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        user = self.context.get('request').user
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                'new_password': 'Пароль должен отличаться от предыдущего.'})
        check_current = check_password(data['current_password'], user.password)
        if check_current is False:
            raise serializers.ValidationError({
                'current_password': 'Введен неверный пароль.'})
        return data


class SubscribeInfoSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeLittleSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, data):
        user = self.context.get('request').user
        author = self.context.get('author_id')
        if user.follower.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(
            instance.author, context={'request': request}
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class AmountOfIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id',
    )
    name = serializers.CharField(
        source='ingredient.name',
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = AmountOfIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = AmountOfIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = AmountOfIngredientSerializer(many=True, read_only=True,
                                               source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientPostSerializer(
        many=True, source='amountofingredient'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, data):
        for field in ['name', 'text', 'cooking_time']:
            if not data.get(field):
                raise serializers.ValidationError(
                    f'{field} - Обязательное поле.'
                )
        if not data.get('tags'):
            raise serializers.ValidationError(
                'Минимум 1 тэг.'
            )
        if not data.get('amountofingredient'):
            raise serializers.ValidationError(
                'Минимум 1 ингредиент.'
            )
        inrgedient_id_list = [
            item['id'] for item in data.get('amountofingredient')
        ]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('amountofingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        creating_an_ingredient(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('amountofingredient')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        AmountOfIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        creating_an_ingredient(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(
            instance,
            context={'request': request}
        ).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if Favorite.objects.filter(user=user,
                                   favorite_recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в избранном'})
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if ShoppingCart.objects.filter(user=user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в списке'})
        return data
