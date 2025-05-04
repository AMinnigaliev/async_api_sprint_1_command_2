class SingletonMeta(type):
    """Метакласс для паттерна Singleton."""

    instances_: dict = {}

    def __call__(cls, *args, **kwds):
        instance = super().__call__(*args, **kwds)
        if cls not in cls.instances_.keys():
            cls.instances_[cls] = instance

        return cls.instances_[cls]
