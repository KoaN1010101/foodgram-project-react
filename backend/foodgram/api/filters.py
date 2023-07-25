from django.shortcuts import get_object_or_404
from django_filters.rest_framework import filters, FilterSet

from recipes.models import AmountOfIngredient, Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favourited = filters.BooleanFilter(
        method='get_is_favourited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favourited', 'is_in_shopping_cart')

    def get_is_favourited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favourites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset


def creating_an_ingredient(ingredients, recipe):
    ingredient_list = []
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(Ingredient,
                                               id=ingredient.get('id'))
        amount = ingredient.get('amount')
        ingredient_list.append(
            AmountOfIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    AmountOfIngredient.objects.bulk_create(ingredient_list)
