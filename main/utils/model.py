from sqlalchemy import inspect

from models import Base


def filter_by(session, model, **kwargs):
    return session.query(model).filter_by(**kwargs)


def get_or_create(session, model, **kwargs):
    filtered = session.query(model).filter_by(**kwargs)
    if filtered.count() > 1:
        raise ValueError(f"{filtered.count()} objects found.")
    instance = filtered.first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True


def create(session, model, **kwargs):
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance


def get(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    return instance if instance else None


def get_all_columns(model):
    mapper = inspect(model)
    return [column.key for column in mapper.attrs]


def get_name_to_model_dict():
    return {
        mapper.class_.__tablename__[: -len("_table")]: {
            "model": mapper.class_,
            "fields": get_all_columns(mapper.class_),
        }
        for mapper in Base.registry.mappers
        if not mapper.class_.__name__.startswith("_")
    }
