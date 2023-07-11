from django.contrib import admin

from recipes.models import (AmountOfIngridient, FavouriteRecipe,
                            Ingredient, Recipe, ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'colour', 'slug')
    search_fields = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'measurement_unit')
    list_filter = ('title', )
    search_fields = ('title', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'favourites_amount')
    readonly_fields = ('favourites_amount',)
    list_filter = ('title', 'author', 'tag')
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def favourites_amount(self, obj):
        return obj.favourite.count()


@admin.register(AmountOfIngridient)
class AmountOfIngridientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    empty_value_display = '-пусто-'


@admin.register(FavouriteRecipe)
class FavouriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'favourtie_recipe')
    search_fields = ('user', 'favourtie_recipe')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'
