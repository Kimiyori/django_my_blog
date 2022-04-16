class Filter:
    def __call__(self,name:str,item):
        return {
            f'{name}__name__icontains':item
        }