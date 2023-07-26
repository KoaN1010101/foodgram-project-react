from django.contrib.auth.hashers import check_password
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from api.utils import creating_an_ingredient
from recipes.models import (AmountOfIngredient, FavouriteRecipe,
                            Ingredient, Recipe, ShoppingCart, Tag)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from users.models import User, Subscribe


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
                and Subscribe.objects.filter(
                    user=self.context.get('request').user,
                    author=obj
        ).exists())


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


class RecipeLittleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        model = Subscribe
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
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True)
    ingredients = AmountOfIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        return (self.context.get('request').user.is_authenticated
                and FavouriteRecipe.objects.filter(
                    user=self.context.get('request').user,
                    favorite_recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())


class IngredientsPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsPostSerializer(
        many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients',
            'name', 'image', 'text', 'cooking_time')

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
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                'Минимум 1 ингредиент.'
            )
        inrgedient_id_list = [item['id'] for item in data.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        creating_an_ingredient(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class FavouriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavouriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if FavouriteRecipe.objects.filter(user=user,
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
