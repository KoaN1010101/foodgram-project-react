from base64 import b64decode
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField
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


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='photo.' + ext)
        return super().to_internal_value(data)
