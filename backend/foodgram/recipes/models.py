from django.db import models
from users.models import User


class Tag(models.Model):
    title = models.CharField(
        verbose_name = 'Тэг',
        max_length=200,
        unique=True
    )
    colour = models.CharField(
        verbose_name = 'Цветовой HEX-код',
        max_length=7,
        unique = True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.title
    

class Ingredient(models.Model):
    title = models.CharField(
        verbose_name = 'Ингридиент',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name = 'Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.title} ({self.measurement_unit})'
    

class Recipe(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    title = models.CharField(
        verbose_name = 'Рецепт',
        max_length=200
    )
    image = models.ImageField(
        verbose_name = 'Картинка',
        upload_to='recipes/'
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length = 200
    )
    ingridients = models.ManyToManyField(
        Ingredient,
        verbose_name = 'Ингридиенты'
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name = 'Тэг'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'

    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering  = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title
    

class AmountOfIngridient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингридиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингридиентов в рецепте'
        verbose_name_plural = 'Количество ингридиентов в рецептах'
    
    def __str__(self):
        return f'{self.ingredient} ({self.amount})'
    
class FavouriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourite',
        verbose_name='Пользователь'
    )
    favourtie_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Пользователь {self.user.username} добавил {self.favourtie_recipe.title} в избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'

    def __str__(self):
        return f'Пользователь {self.user.username} добавил {self.recipe.title} в корзину'
