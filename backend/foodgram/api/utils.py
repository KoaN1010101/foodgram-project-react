from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404

from recipes.models import Recipe


def add_or_delete(self, pk, serializer_class):
    user = self.request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    model_obj = serializer_class.Meta.model.objects.filter(
        user=user, recipe=recipe
    )

    if self.request.method == 'POST':
        serializer = serializer_class(
            data={'user': user.id, 'recipe': pk},
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
