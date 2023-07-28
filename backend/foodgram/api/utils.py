from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from recipes.models import AmountOfIngredient, Ingredient, Recipe


def add_or_delete(self, id, serializer_class):
    user = self.request.user
    recipe = get_object_or_404(Recipe, pk=id)
    model_obj = serializer_class.Meta.model.objects.filter(
        user=user, recipe=recipe
    )

    if self.request.method == 'POST':
        serializer = serializer_class(
            data={'user': user.id, 'recipe': id},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if self.request.method == 'DELETE':
        if not model_obj.exists():
            return Response({'error': 'Рецепт не в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
    model_obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


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

def recipe_ingredients_set(
    recipe: Recipe, ingredients: dict[int, tuple["Ingredient", int]]
) -> None:
    """Записывает ингредиенты вложенные в рецепт.

    Создаёт объект AmountIngredient связывающий объекты Recipe и
    Ingredient с указанием количества(`amount`) конкретного ингридиента.

    Args:
        recipe (Recipe):
            Рецепт, в который нужно добавить игридиенты.
        ingridients (list[dict]):
            Список ингридентов и количества сих.
    """
    objs = []

    for ingredient, amount in ingredients.values():
        objs.append(
            AmountIngredient(
                recipe=recipe, ingredients=ingredient, amount=amount
            )
        )

    AmountOfIngredient.objects.bulk_create(objs)
