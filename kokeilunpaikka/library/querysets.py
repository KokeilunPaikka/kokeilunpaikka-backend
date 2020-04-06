from parler.managers import TranslatableQuerySet


class LibraryItemQuerySet(TranslatableQuerySet):

    def visible(self):
        return self.filter(is_visible=True)
