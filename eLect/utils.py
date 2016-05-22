import os.path

from eLect.main import app

# def get_or_create(session, model, defaults=None, **kwargs):
#     """ Returns instance if already exists, creates and returns one if not """
#     instance = session.query(model).filter_by(**kwargs).first()
#     if instance:
#         return instance, False
#     else:
#         params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
#         params.update(defaults or {})
#         instance = model(**params)
#         session.add(instance)
#         return instance, True